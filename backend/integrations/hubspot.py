import json
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import base64
import requests
from integrations.integration_item import IntegrationItem
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('HUBSPOT_CLIENT_ID')
CLIENT_SECRET = os.getenv('HUBSPOT_CLIENT_SECRET')
REDIRECT_URI = os.getenv('HUBSPOT_REDIRECT_URI')

authorization_url = 'https://app.hubspot.com/oauth/authorize'
token_url = 'https://api.hubspot.com/oauth/v1/token'

async def authorize_hubspot(user_id, org_id):
    """Generate authorization URL for HubSpot OAuth flow"""
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = base64.urlsafe_b64encode(json.dumps(state_data).encode('utf-8')).decode('utf-8')
    
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', json.dumps(state_data), expire=600)
    
    auth_url = (
        f'{authorization_url}'
        f'?client_id={CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        f'&scope=crm.objects.contacts.read%20crm.objects.companies.read'
        f'&state={encoded_state}'
    )
    
    return auth_url

async def oauth2callback_hubspot(request: Request):
    """Handle OAuth callback from HubSpot"""
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error_description'))
    
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    
    try:
        state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode('utf-8'))
    except:
        raise HTTPException(status_code=400, detail='Invalid state format')
    
    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')
    
    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')
    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')
    
    async with httpx.AsyncClient() as client:
        try:
            response, _ = await asyncio.gather(
                client.post(
                    token_url,
                    data={
                        'grant_type': 'authorization_code',
                        'client_id': CLIENT_ID,
                        'client_secret': CLIENT_SECRET,
                        'redirect_uri': REDIRECT_URI,
                        'code': code
                    },
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                ),
                delete_key_redis(f'hubspot_state:{org_id}:{user_id}')
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=f'Token exchange failed: {str(e)}')
    
    await add_key_value_redis(
        f'hubspot_credentials:{org_id}:{user_id}',
        json.dumps(response.json()),
        expire=600
    )
    
    return HTMLResponse(content="<html><script>window.close();</script></html>")

async def get_hubspot_credentials(user_id, org_id):
    """Retrieve stored HubSpot credentials"""
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    
    try:
        credentials = json.loads(credentials)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail='Invalid credentials format')
    
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')
    return credentials

def create_integration_item_metadata_object(response_json: dict, item_type: str) -> IntegrationItem:
    """Create IntegrationItem object from HubSpot response"""
    return IntegrationItem(
        id=str(response_json.get('id')),
        name=response_json.get('properties', {}).get('name', 'Unnamed'),
        type=item_type,
        creation_time=response_json.get('createdAt'),
        last_modified_time=response_json.get('updatedAt'),
        parent_id=None
    )

async def get_items_hubspot(credentials) -> list[IntegrationItem]:
    """Fetch and aggregate HubSpot items (contacts and companies)"""
    try:
        credentials = json.loads(credentials)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail='Invalid credentials format')
        
    access_token = credentials.get('access_token')
    if not access_token:
        raise HTTPException(status_code=400, detail='Access token not found')
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    items = []
    
    # Fetch companies
    try:
        companies_response = requests.get(
            'https://api.hubapi.com/crm/v3/objects/companies',
            headers=headers
        )
        companies_response.raise_for_status()
        
        if companies_response.status_code == 200:
            companies = companies_response.json().get('results', [])
            items.extend([create_integration_item_metadata_object(company, 'company') 
                         for company in companies])
    
        # Fetch contacts
        contacts_response = requests.get(
            'https://api.hubapi.com/crm/v3/objects/contacts',
            headers=headers
        )
        contacts_response.raise_for_status()
        
        if contacts_response.status_code == 200:
            contacts = contacts_response.json().get('results', [])
            items.extend([create_integration_item_metadata_object(contact, 'contact') 
                         for contact in contacts])
            
        return items
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f'Failed to fetch HubSpot items: {str(e)}')