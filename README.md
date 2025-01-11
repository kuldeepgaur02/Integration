# VectorShift Integration Project

## Project Overview
This project demonstrates a scalable integration system that connects multiple third-party services (HubSpot, Airtable, and Notion) through OAuth2 authentication. Built with React (frontend) and FastAPI (backend), it showcases a modern architecture for handling enterprise integrations.

### 🌟 Key Features
- OAuth2 authentication flow implementation
- Modular integration architecture
- Real-time data fetching from multiple platforms
- Secure credential management using Redis
- Modern, responsive UI with Material-UI
- Easy-to-extend integration system

## 🛠 Technology Stack
- **Frontend**: React, Material-UI, Axios
- **Backend**: Python, FastAPI
- **Database**: Redis (for token management)
- **Authentication**: OAuth2
- **APIs Integrated**: 
  - HubSpot (CRM data)
  - Airtable (Database)
  - Notion (Workspace)

## 🏗 Architecture

### Frontend Structure
```
frontend/
├── src/
│   ├── integrations/
│   │   ├── airtable.js
│   │   ├── notion.js
│   │   └── hubspot.js
│   ├── data-form.js
│   └── integration-form.js
```

### Backend Structure
```
backend/
├── integrations/
│   ├── airtable.py
│   ├── notion.py
│   ├── hubspot.py
│   └── integration_item.py
├── main.py
└── redis_client.py
```

## 🚀 Getting Started

### Prerequisites
- Node.js and npm
- Python 3.8+
- Redis server
- HubSpot, Airtable, and Notion developer accounts

### Setup Instructions

1. **Clone the repository**
```bash
git clone [repository-url]
cd vectorshift-integration
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Create .env file in backend directory**
```env
HUBSPOT_CLIENT_ID=your_client_id
HUBSPOT_CLIENT_SECRET=your_client_secret
HUBSPOT_REDIRECT_URI=http://localhost:8000/integrations/hubspot/oauth2callback
```

4. **Frontend Setup**
```bash
cd frontend
npm install
```

5. **Start Services**
```bash
# Start Redis Server
redis-server

# Start Backend (in backend directory)
uvicorn main:app --reload

# Start Frontend (in frontend directory)
npm start
```

## 🔄 Integration Flow
1. User selects an integration platform (HubSpot/Airtable/Notion)
2. OAuth2 authorization is initiated
3. User authenticates with the chosen platform
4. Access tokens are securely stored in Redis
5. Integration data can be loaded through the UI

## 🔐 Security Features
- Secure token management using Redis
- State verification in OAuth flow
- Automatic token expiration
- CORS protection
- Environment variable configuration

## 💡 Implementation Details

### OAuth2 Flow
1. **Authorization Request**: Generates a secure state token and redirects to service's auth page
2. **Callback Handling**: Verifies state, exchanges code for access token
3. **Token Management**: Stores encrypted tokens in Redis with expiration

### Data Integration
Each integration follows a standardized pattern:
- Common `IntegrationItem` class for data consistency
- Service-specific API calls
- Error handling and rate limiting
- Data transformation to common format

### Frontend Components
- **IntegrationForm**: Main container managing integration state
- **Service-specific components**: Handle OAuth flow and UI state
- **DataForm**: Displays and manages retrieved data

## 🔍 Testing
1. Configure developer accounts for each service
2. Set up OAuth credentials
3. Run the application
4. Test integration flows
5. Verify data retrieval

## 🛣 Future Enhancements
- Additional service integrations
- Batch data processing
- Enhanced error handling
- Data visualization components
- Automated testing suite
- Rate limiting implementation

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details

---

Feel free to reach out for any questions or clarifications!