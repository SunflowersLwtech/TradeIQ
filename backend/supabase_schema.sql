-- TradeIQ - Supabase Schema (Design Document v3.0, Section 7 & Appendix B)
-- Run this in Supabase SQL Editor if Supabase MCP is read-only.
-- Enable UUID extension if not already enabled.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. users (app profile; Supabase Auth manages auth.users separately)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    preferences JSONB DEFAULT '{}',
    watchlist JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. trades
CREATE TABLE IF NOT EXISTS trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    instrument VARCHAR(64) NOT NULL,
    direction VARCHAR(16),
    entry_price DECIMAL(20, 8),
    exit_price DECIMAL(20, 8),
    pnl DECIMAL(20, 8) NOT NULL,
    duration_seconds INTEGER,
    opened_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    is_mock BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_opened_at ON trades(opened_at);

-- 3. behavioral_metrics (pattern_flags for e.g. revenge_trading)
CREATE TABLE IF NOT EXISTS behavioral_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    trading_date DATE NOT NULL,
    total_trades INTEGER NOT NULL DEFAULT 0,
    win_count INTEGER NOT NULL DEFAULT 0,
    loss_count INTEGER NOT NULL DEFAULT 0,
    avg_hold_time DOUBLE PRECISION,
    risk_score DOUBLE PRECISION,
    emotional_state VARCHAR(64),
    pattern_flags JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_behavioral_metrics_user_date ON behavioral_metrics(user_id, trading_date);

-- 4. ai_personas (Calm Analyst, Data Nerd, etc.)
CREATE TABLE IF NOT EXISTS ai_personas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(128) NOT NULL,
    personality_type VARCHAR(64),
    system_prompt TEXT,
    voice_config JSONB DEFAULT '{}',
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. social_posts (platform default 'bluesky', content, status)
CREATE TABLE IF NOT EXISTS social_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    persona_id UUID NOT NULL REFERENCES ai_personas(id) ON DELETE CASCADE,
    platform VARCHAR(32) NOT NULL DEFAULT 'bluesky',
    content TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    engagement_metrics JSONB DEFAULT '{}',
    scheduled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_social_posts_persona_id ON social_posts(persona_id);
CREATE INDEX IF NOT EXISTS idx_social_posts_status ON social_posts(status);

-- Optional: link users to Supabase auth if you use auth.users
-- ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_uid UUID REFERENCES auth.users(id);
