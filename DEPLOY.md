# TradeIQ Quick Deployment Guide

## System Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  Frontend    │────▶│   Backend    │────▶│   Supabase    │
│  Next.js     │     │  Django+ASGI │     │  PostgreSQL   │
│  :3000       │     │  :8000       │     │  (Cloud)      │
└─────────────┘     └──────────────┘     └───────────────┘
                          │
                    ┌─────┴─────┐
                    │  LLM API  │  (DeepSeek / OpenRouter)
                    │  NewsAPI  │
                    │  Bluesky  │
                    └───────────┘
```

---

## Method 1: Docker Compose One-Click Deployment (Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- `.env` file configured (see below)

### Steps

```bash
# 1. Clone the repository
git clone <repo-url> && cd "deriv hackathon"

# 2. Configure environment variables
cp backend/.env.example .env
# Edit .env and fill in all API Keys and database connection

# 3. One-click start
docker compose up --build

# Run in background
docker compose up --build -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

### Access
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Pipeline Page**: http://localhost:3000/pipeline

### Custom Ports
```bash
BACKEND_PORT=9000 FRONTEND_PORT=4000 docker compose up --build
```

---

## Method 2: Direct Deployment (No Docker)

### Prerequisites
- Python 3.11+ (conda recommended)
- Node.js 20+
- npm

### Steps

```bash
# 1. Create conda environment
conda create -n tradeiq python=3.11 -y
conda activate tradeiq

# 2. Install backend dependencies
pip install -r backend/requirements.txt

# 3. Install frontend dependencies
cd frontend && npm ci && cd ..

# 4. Configure environment variables
cp backend/.env.example .env
# Edit .env and fill in all values

cp frontend/.env.example frontend/.env.local
# Edit frontend/.env.local

# 5. Run database migrations
cd backend && python manage.py migrate && cd ..

# 6. One-click start (production mode)
./scripts/start_prod.sh
```

### Or Start Separately (Development Mode)

```bash
# Terminal 1: Backend
./scripts/start_backend.sh

# Terminal 2: Frontend
./scripts/start_frontend.sh
```

---

## Method 3: Cloud Platform Deployment

### Railway (Recommended, Free Tier)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy backend
cd backend
railway up

# Deploy frontend
cd ../frontend
railway up
```

### Render

1. Connect GitHub repository to [Render](https://render.com)
2. Create two Web Services:
   - **Backend**: Build Command: `pip install -r requirements.txt`, Start Command: `daphne -b 0.0.0.0 -p $PORT tradeiq.asgi:application`
   - **Frontend**: Build Command: `npm ci && npm run build`, Start Command: `npm start`
3. Configure all environment variables in Environment settings

---

## Environment Variables Checklist

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Supabase PostgreSQL connection string | ✅ |
| `DJANGO_SECRET_KEY` | Django secret key (random string) | ✅ |
| `SUPABASE_URL` | Supabase project URL | ✅ |
| `SUPABASE_JWT_SECRET` | Supabase JWT secret | ✅ |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | ✅* |
| `OPENROUTER_API_KEY` | OpenRouter API Key | ✅* |
| `DERIV_APP_ID` | Deriv API App ID | ✅ |
| `DERIV_TOKEN` | Deriv API Token | ✅ |
| `NEWS_API_KEY` | NewsAPI.org Key | ✅ |
| `FINNHUB_API_KEY` | Finnhub.io Key | ✅ |
| `BLUESKY_HANDLE` | Bluesky account handle | ✅ |
| `BLUESKY_APP_PASSWORD` | Bluesky App Password | ✅ |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | ⚠️ |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Secret | ⚠️ |
| `CALLBACK_URL` | OAuth callback URL | ⚠️ |

> *At least one of `DEEPSEEK_API_KEY` or `OPENROUTER_API_KEY` is required

---

## Feature Verification

After deployment, run test scripts to verify all features:

```bash
# Check environment
conda run -n tradeiq python scripts/verify_env.py

# Run comprehensive feature tests
conda run --no-capture-output -n tradeiq python -u scripts/test_all_features.py
```

### Core Feature Tests

1. **Visit Homepage**: http://localhost:3000 → Dashboard shows real-time data
2. **Pipeline Page**: http://localhost:3000/pipeline → Click "BTC/USD +5.2%"
3. **Full Pipeline**: Market Monitor → Analyst → Portfolio Advisor → Content Creator → Bluesky Publish
4. **AI Chat**: Enter "Why did BTC spike today?" in sidebar to test LLM response

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend 502 | Check `DATABASE_URL` in `.env` is correct |
| LLM no response | Verify `DEEPSEEK_API_KEY` or `OPENROUTER_API_KEY` has balance |
| Bluesky publish failed | Check `BLUESKY_HANDLE` and `BLUESKY_APP_PASSWORD` |
| Frontend FALLBACK mode | Ensure backend is running on :8000, check `NEXT_PUBLIC_API_URL` |
| Docker build failed | Run `docker compose build --no-cache` |
| WebSocket disconnected | Check `NEXT_PUBLIC_WS_URL` configuration |
