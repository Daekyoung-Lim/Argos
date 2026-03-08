# Quickstart: Company Asset Management (001-asset-management)

**Date**: 2026-03-04  
**Branch**: `001-asset-management`

## Prerequisites

- Python 3.11+
- Node.js 18+ / npm 9+
- Docker Desktop
- Azure CLI (`az`) - configured with subscription access
- Azure SQL Database 접속 가능한 네트워크 환경

## Environment Variables

프로젝트 루트에 `.env` 파일을 생성합니다:

```env
# Azure SQL Database
AZURE_SQL_DB_SERVER_NAME=argos-sql-server.database.windows.net
AZURE_SQL_DB_USER_NAME=argosdmin
AZURE_SQL_DB_PASSWORD=<your_db_password>

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://rs-prj-argos.openai.azure.com/openai/v1/
AZURE_OPENAI_API_KEY=<your_openai_api_key_here>
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
AZURE_OPENAI_API_VERSION=2025-04-14

# Azure AI Vision
AZURE_AI_VISION_ENDPOINT=https://koreacentral.api.cognitive.microsoft.com/
AZURE_AI_VISION_API_KEY=<your_vision_api_key_here>

# Azure Blob Storage
AZURE_STORAGE_ACCOUNT_NAME=argosstphotos
AZURE_STORAGE_ACCOUNT_KEY=<your_storage_account_key_here>
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=argosstphotos;AccountKey=<your_storage_account_key_here>;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER_NAME=asset-photos

# JWT Config
JWT_SECRET_KEY=<your-secret-key-change-in-production>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=480
```

## Backend (Development)

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run dev server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API Docs: http://localhost:8000/docs

## Frontend (Development)

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Run dev server
npm run dev
```

App: http://localhost:5173

## Docker (Backend Only)

```bash
# Build
docker build -t argos-backend ./backend

# Run
docker run -p 8000:8000 --env-file .env argos-backend
```

## Azure Deployment

```bash
# 1. Login to Azure
az login

# 2. Push to ACR
az acr login --name <acr-name>
docker tag argos-backend <acr-name>.azurecr.io/argos-backend:latest
docker push <acr-name>.azurecr.io/argos-backend:latest

# 3. Deploy to Azure Container Apps
az containerapp create \
  --name argos-backend \
  --resource-group <resource-group> \
  --environment <aca-environment> \
  --image <acr-name>.azurecr.io/argos-backend:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars-file .env

# 4. Deploy Frontend to Azure Static Web Apps
# (via GitHub Actions or Azure CLI swa deploy)
```

## Project Structure

```
argos_draft_v01/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Environment config
│   │   ├── auth/                # JWT authentication
│   │   ├── models/              # SQLAlchemy models
│   │   ├── api/                 # API route handlers
│   │   ├── services/            # Business logic
│   │   ├── crews/               # CrewAI crews
│   │   │   ├── asset_audit/     # Asset Diligence Crew
│   │   │   └── admin_analyst/   # Admin Analyst Crew
│   │   └── tools/               # CrewAI custom tools
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── .env
└── specs/                        # Feature specifications
```
