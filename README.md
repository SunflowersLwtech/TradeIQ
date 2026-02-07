# TradeIQ - Intelligent Trading Analyst

> The Bloomberg Terminal for retail traders, the trading coach they never had, and the content team they always wanted.

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Using automated script (recommended)
./scripts/setup_env.sh

# Or manually create
conda env create -f scripts/environment.yml
conda activate tradeiq
```

### 2. Configure Environment Variables

Ensure `.env` file is configured (see `docs/ENV_CHECKLIST.md`)

### 3. Run the Project

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

Visit: http://localhost:8000

## 📁 Project Structure

```
tradeiq/
├── backend/              # Django backend application
│   ├── agents/           # AI Agent routing and tools
│   ├── behavior/        # Behavioral analysis module
│   ├── market/           # Market analysis module
│   ├── content/          # Content generation module
│   ├── chat/             # WebSocket chat
│   └── demo/             # Demo tools
│
├── docs/                 # Project documentation
│   ├── DESIGN_DOCUMENT.md
│   ├── DEEPSEEK_MIGRATION.md
│   ├── LLM_COST_COMPARISON.md
│   ├── ENV_CHECKLIST.md
│   ├── ENV_SETUP.md
│   ├── QUICK_START.md
│   └── ...
│
├── scripts/              # Utility scripts
│   ├── setup_env.sh      # Environment setup script
│   ├── verify_env.py     # Environment verification script
│   ├── environment.yml   # Conda environment configuration
│   └── test_*.py         # Test scripts
│
├── dev/                  # Development resources
│   ├── diagrams/         # Architecture diagrams
│   └── docs/             # Original design documents
│
├── .env                  # Environment variables (not committed to Git)
├── .gitignore
└── README.md             # This file
```

## 🎯 Core Features

1. **Market Analysis** - Real-time market analysis and explanations
2. **Behavioral Coaching** - Trading behavior pattern detection and recommendations
3. **Social Content Engine** - AI-generated social media content

## 🛠️ Tech Stack

- **Backend**: Django 5 + DRF + Channels
- **AI/LLM**: DeepSeek-V3.2 (Function Calling)
- **Database**: Supabase (PostgreSQL)
- **WebSocket**: Django Channels (InMemoryChannelLayer)
- **External APIs**: Deriv, NewsAPI, Bluesky

## 📚 Documentation

- [Quick Start Guide](docs/QUICK_START.md)
- [Environment Setup Guide](docs/ENV_SETUP.md)
- [Design Document](docs/DESIGN_DOCUMENT.md)
- [DeepSeek Migration Guide](docs/DEEPSEEK_MIGRATION.md)
- [LLM Cost Comparison](docs/LLM_COST_COMPARISON.md)

## 🔧 Development Tools

```bash
# Verify environment
python scripts/verify_env.py

# Run tests
cd backend
python manage.py test

# Load demo data
python manage.py loaddata fixtures/demo_*.json
```

## 📝 License

Deriv AI Hackathon 2026
