<p align="center">
  <img src="frontend/public/tradeiq_favicon.svg" width="80" alt="TradeIQ Logo" />
</p>

<h1 align="center">TradeIQ</h1>

<p align="center">
  <strong>The Bloomberg Terminal for retail traders, the trading coach they never had, and the content team they always wanted.</strong>
</p>

<p align="center">
  <a href="https://deriv.com"><img src="https://img.shields.io/badge/Deriv_AI_Hackathon-2026-ff444f?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZD0iTTEyIDJMMiAyMmgyMEwxMiAyeiIgZmlsbD0id2hpdGUiLz48L3N2Zz4=" alt="Deriv Hackathon 2026" /></a>
  <img src="https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js" alt="Next.js" />
  <img src="https://img.shields.io/badge/Django-5-092E20?style=for-the-badge&logo=django" alt="Django" />
  <img src="https://img.shields.io/badge/DeepSeek-AI-4A90D9?style=for-the-badge" alt="DeepSeek" />
  <img src="https://img.shields.io/badge/Supabase-DB-3ECF8E?style=for-the-badge&logo=supabase" alt="Supabase" />
</p>

<p align="center">
  <a href="https://deepwiki.com/SunflowersLwtech/deriv-hackathon"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>

---

## The Problem

Traders face two interconnected challenges: **understanding what's happening in markets** and **managing their own behaviour**. Professional traders have analyst teams for market insights and coaches for discipline. Retail traders have neither.

> *"I see the price dropped 5% but I don't know why. By the time I find the news, the move is over."*
>
> *"I didn't realise I was on a losing streak until I'd lost half my account. No one warned me."*
>
> *"I wish there was a trusted voice that explained what's happening in markets without the hype."*

**TradeIQ** bridges this gap with AI-powered intelligence across three pillars:

<table>
<tr>
<td width="33%" align="center">

**Market Analysis**

Real-time prices, technical indicators, sentiment analysis, economic calendar, and AI-powered market Q&A

</td>
<td width="33%" align="center">

**Behavioral Coaching**

Trade pattern detection (revenge trading, overtrading, loss chasing), personalized nudges, and risk scoring

</td>
<td width="33%" align="center">

**Social Content Engine**

AI-generated market commentary with multiple personas, auto-hashtags, one-click publish to Bluesky

</td>
</tr>
</table>

> **Note**: TradeIQ provides educational analysis only. It does **not** provide trading signals, predictions, or financial advice.

---

## Quick Start

```bash
# Clone and setup
git clone https://github.com/SunflowersLwtech/deriv-hackathon.git
cd "deriv hackathon"
cp .env.example .env          # Fill in your API keys

# Backend
conda create -n tradeiq python=3.11 -y && conda activate tradeiq
pip install -r backend/requirements.txt
cd backend && python manage.py runserver

# Frontend (new terminal)
cd frontend && npm ci && npm run dev
```

Open **http://localhost:3000** (frontend) and **http://localhost:8000/api/** (backend).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16, React 19, Tailwind CSS 4, Recharts, Framer Motion |
| **Backend** | Django 5, DRF, Django Channels (Daphne ASGI), WebSocket |
| **AI/LLM** | DeepSeek V3 via OpenRouter (function calling + multi-agent pipeline) |
| **Database** | Supabase PostgreSQL, Upstash Redis (channel layer) |
| **Auth** | Supabase Auth (Google OAuth, JWT) |
| **External APIs** | Deriv WebSocket, NewsAPI, Finnhub, Bluesky AT Protocol |

---

## 5-Agent Pipeline

```
[1] Market Monitor ──> [2] Event Analyst ──> [3] Portfolio Advisor
      (Deriv API)          (News + LLM)          (User positions)
                                                        │
[5] Content Creator <── [4] Behavioral Sentinel <───────┘
     (Bluesky post)         (Trade history)
```

Each agent receives structured input from the previous stage, runs DeepSeek function calling with specialized tools, and passes results forward. The pipeline produces a complete analysis from raw market event to published Bluesky post.

---

<details>
<summary><h2>External APIs & Integration Details</h2></summary>

### Deriv WebSocket API
- **Live prices** (`ticks`) and **OHLC candles** (`ticks_history`)
- **Trade history** (`profit_table`) for behavioral analysis
- **Portfolio** and **balance** for real-time account data
- **Active symbols** for dynamic instrument listing
- **Reality check** for official session health data
- Connection: `wss://ws.derivws.com/websockets/v3?app_id=YOUR_APP_ID`

### Finnhub API
- **Economic calendar** (`/calendar/economic`) — explains "why did EUR/USD drop?"
- **Chart pattern recognition** (`/scan/pattern`) — head-and-shoulders, triangles, etc.
- **Real-time quotes** (`/quote`) — fallback for Deriv coverage gaps
- **Market news** (`/news`) — aggregated with NewsAPI

### NewsAPI
- **Top headlines** (`/v2/top-headlines?category=business`) — dashboard news feed
- **Keyword search** (`/v2/everything`) — instrument-specific news for sentiment
- Domain filtering for authoritative sources (Reuters, Bloomberg, CNBC)

### Bluesky AT Protocol
- **Post publishing** with auto-hashtag facets (`#TradeIQ #trading`)
- **Thread publishing** for multi-part analysis
- **Link card embeds** for news source references
- **Post search** for social sentiment analysis
- Authentication via app password (not OAuth)

</details>

---

<details>
<summary><h2>API Reference</h2></summary>

All endpoints served under `/api/`. Auth via `Authorization: Bearer <supabase_jwt>` (most endpoints work without auth for demo).

### Market Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/market/ask/` | Ask AI market analyst a question |
| `POST` | `/api/market/brief/` | Market summary for instruments |
| `POST` | `/api/market/price/` | Live price (Deriv WebSocket) |
| `POST` | `/api/market/history/` | OHLC candles |
| `POST` | `/api/market/technicals/` | SMA, RSI, support/resistance |
| `POST` | `/api/market/sentiment/` | AI sentiment analysis |
| `GET` | `/api/market/calendar/` | Economic calendar (Finnhub) |
| `GET` | `/api/market/headlines/` | Top headlines (NewsAPI) |
| `GET` | `/api/market/instruments/` | Active symbols (Deriv) |
| `POST` | `/api/market/patterns/` | Chart patterns (Finnhub) |

### Behavioral Coaching

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/behavior/trades/` | Trade history |
| `POST` | `/api/behavior/trades/analyze_batch/` | Pattern detection |
| `POST` | `/api/behavior/trades/sync_deriv/` | Sync from Deriv account |
| `GET` | `/api/behavior/portfolio/` | Deriv portfolio |
| `GET` | `/api/behavior/balance/` | Deriv balance |
| `GET` | `/api/behavior/reality-check/` | Deriv reality check |

### Content Engine

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/content/generate/` | Generate social content |
| `POST` | `/api/content/publish-bluesky/` | Publish to Bluesky |
| `GET` | `/api/content/bluesky-search/` | Search Bluesky posts |
| `GET` | `/api/content/personas/` | List AI personas |

### Agent Pipeline

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/agents/pipeline/` | Full 5-stage pipeline |
| `POST` | `/api/agents/monitor/` | Stage 1: Market Monitor |
| `POST` | `/api/agents/analyst/` | Stage 2: Event Analyst |
| `POST` | `/api/agents/advisor/` | Stage 3: Portfolio Advisor |
| `POST` | `/api/agents/sentinel/` | Stage 4: Behavioral Sentinel |
| `POST` | `/api/agents/content-gen/` | Stage 5: Content Creator |
| `POST` | `/api/agents/chat/` | Auto-routed chat |

### Demo

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/demo/seed/` | Initialize demo data |
| `POST` | `/api/demo/analyze/` | Load scenario + analyze |
| `POST` | `/api/demo/wow-moment/` | Three-pillar combined demo |

</details>

---

<details>
<summary><h2>Behavioral Detection Algorithms</h2></summary>

### Revenge Trading
- **Trigger**: 3+ trades within 10 minutes after a loss
- **Severity**: Low (3 trades), Medium (4), High (5+)
- **Nudge**: "I notice you've made several trades quickly after a loss. Consider taking a breath."

### Overtrading
- **Trigger**: Daily trade count > 2x historical average
- **Severity**: Low (2-2.5x), Medium (2.5-3x), High (3x+)
- **Nudge**: "You're at X trades today, which is Y times your average. Quality over quantity."

### Loss Chasing
- **Trigger**: 2+ consecutive losses with 20%+ position size increase
- **Severity**: Based on consecutive count and size escalation
- **Nudge**: "I see increasing position sizes after losses. Classic loss-chasing pattern."

### Time-Based Patterns
- **Trigger**: Win rate < 35% during specific hours (min 3 trades/hour)
- **Output**: Identifies worst-performing trading hours

All nudges are **supportive, not restrictive** — they inform and suggest, never block or judge.

</details>

---

<details>
<summary><h2>Project Structure</h2></summary>

```
deriv hackathon/
├── frontend/                  # Next.js 16 (React 19)
│   ├── src/app/               # App Router pages (dashboard, market, behavior, content, pipeline)
│   ├── src/components/        # 25+ React components (layout, market, behavior, chat, ui)
│   ├── src/hooks/             # Custom hooks (useMarketData, useBehaviorData, useApiWithFallback)
│   └── src/lib/               # API client (60+ types), WebSocket client, Supabase client
│
├── backend/                   # Django 5 + DRF + Channels
│   ├── agents/                # AI Agent Team (router, agent_team, tools_registry, compliance)
│   ├── market/                # Market Analysis (Deriv WebSocket, Finnhub, NewsAPI tools)
│   ├── behavior/              # Behavioral Coach (detection algorithms, Deriv client, nudges)
│   ├── content/               # Content Engine (personas, Bluesky AT Protocol client)
│   ├── chat/                  # WebSocket consumer (auto-routing to agents)
│   ├── demo/                  # Demo scenarios (revenge_trading, overtrading, loss_chasing)
│   └── tradeiq/               # Django config (settings, ASGI, JWT auth middleware)
│
├── scripts/                   # Setup, start, and verification scripts
├── dev/                       # Architecture diagrams (10 PNGs) and design docs
└── .env.example               # Environment variables template
```

</details>

---

<details>
<summary><h2>Environment Variables</h2></summary>

```bash
# Database
DATABASE_URL=postgresql://...          # Supabase connection string

# Django
DJANGO_SECRET_KEY=...
DEBUG=True

# LLM (need at least one)
DEEPSEEK_API_KEY=...                   # Direct DeepSeek
OPENROUTER_API_KEY=...                 # OpenRouter (recommended)

# Deriv API (free at api.deriv.com)
DERIV_APP_ID=...                       # App registration ID
DERIV_TOKEN=...                        # API token (read + trade scope)

# News & Data
NEWS_API_KEY=...                       # newsapi.org
FINNHUB_API_KEY=...                    # finnhub.io

# Social
BLUESKY_HANDLE=...                     # your-handle.bsky.social
BLUESKY_APP_PASSWORD=...               # App password (not main password)

# Auth
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_JWT_SECRET=...
GOOGLE_CLIENT_ID=...                   # For Google OAuth

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

All API keys work on **free tiers** for hackathon demo purposes.

</details>

---

<details>
<summary><h2>Demo Scenarios</h2></summary>

Pre-configured behavioral patterns for live demo:

| Scenario | Trades | Pattern | Expected Detection |
|----------|--------|---------|-------------------|
| `revenge_trading` | 5 trades in 8 min after -$200 loss | Rapid trading post-loss | Revenge trading (high) |
| `overtrading` | 22 trades in 80 min (2.75x avg) | Excessive frequency | Overtrading (medium) |
| `loss_chasing` | 4 consecutive losses, 1.5x size increase | Position size escalation | Loss chasing (high) |
| `healthy_session` | 6 trades, 60% win rate | Disciplined trading | No patterns (healthy) |

```bash
# Load and analyze a scenario
curl -X POST http://localhost:8000/api/demo/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"scenario": "revenge_trading"}'

# Three-pillar "wow moment" demo
curl -X POST http://localhost:8000/api/demo/wow-moment/ \
  -H "Content-Type: application/json" \
  -d '{"instrument": "EUR/USD"}'
```

</details>

---

<details>
<summary><h2>Design Decisions</h2></summary>

| Decision | Rationale |
|----------|-----------|
| **No predictions/signals** | Hackathon requirement: educational analysis only, brand-safe |
| **Supportive coaching** | Nudges inform and suggest, never block trades or judge |
| **Graceful degradation** | Frontend works with mock data when backend is offline |
| **LLM fallback chain** | DeepSeek direct -> OpenRouter with automatic failover |
| **WebSocket + REST** | Chat uses WebSocket with REST fallback for reliability |
| **Function calling** | DeepSeek native tool use instead of LangGraph for simplicity |
| **Multi-persona content** | Different AI voices (Calm Analyst, Data Nerd, Trading Coach) |
| **Compliance-first** | Every LLM output filtered for blocklisted terms + disclaimer injection |

</details>

---

<details>
<summary><h2>Compliance System</h2></summary>

All AI outputs pass through a compliance filter before reaching users:

**Blocklist**: `guaranteed`, `moon`, `easy money`, `get rich`, `sure thing`

**Prediction detection**: Regex matching `will hit`, `price will`, `going to`

**Auto-disclaimer**: Every response includes `"This is analysis, not financial advice."`

**System prompts**: All agents have master compliance rules embedded:
- Never predict future prices
- Always use past/present tense
- Frame everything as educational
- Reference specific data sources

</details>

---

## License

Built for the [Deriv AI Hackathon 2026](https://deriv.com).

<p align="center">
  <img src="frontend/public/tradeiq_favicon.svg" width="40" alt="TradeIQ" />
  <br />
  <sub>TradeIQ - Making trading intelligent</sub>
</p>
