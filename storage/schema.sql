-- SOVEREIGN-Ω PostgreSQL Schema
-- All tables are append-only. Records are never deleted. Moat never decreases.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Coherence cycles
CREATE TABLE IF NOT EXISTS cycles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_id        TEXT UNIQUE NOT NULL,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    query_hash      TEXT NOT NULL,
    psi_score       DOUBLE PRECISION NOT NULL,
    delta_threshold DOUBLE PRECISION NOT NULL,
    gate_open       BOOLEAN NOT NULL,
    p_score         DOUBLE PRECISION,
    i_score         DOUBLE PRECISION,
    c_score         DOUBLE PRECISION,
    s_score         DOUBLE PRECISION,
    w_score         DOUBLE PRECISION,
    domain          TEXT,
    lambda_at_time  DOUBLE PRECISION,
    omega_value     DOUBLE PRECISION
);
CREATE INDEX idx_cycles_timestamp ON cycles(timestamp DESC);
CREATE INDEX idx_cycles_gate_open ON cycles(gate_open);

-- Silence episodes
CREATE TABLE IF NOT EXISTS silence_log (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_id    TEXT REFERENCES cycles(cycle_id),
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    psi         DOUBLE PRECISION NOT NULL,
    delta       DOUBLE PRECISION NOT NULL,
    gap         DOUBLE PRECISION GENERATED ALWAYS AS (delta - psi) STORED,
    reason      TEXT,
    plane_p     DOUBLE PRECISION,
    plane_i     DOUBLE PRECISION,
    plane_c     DOUBLE PRECISION,
    plane_s     DOUBLE PRECISION,
    plane_w     DOUBLE PRECISION
);
CREATE INDEX idx_silence_timestamp ON silence_log(timestamp DESC);

-- Trades
CREATE TABLE IF NOT EXISTS trades (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trade_id            TEXT UNIQUE NOT NULL,
    pharos_tx_open      TEXT,
    pharos_tx_close     TEXT,
    symbol              TEXT NOT NULL,
    direction           TEXT NOT NULL CHECK (direction IN ('LONG', 'SHORT')),
    strategy            TEXT,
    entry_price         DOUBLE PRECISION,
    exit_price          DOUBLE PRECISION,
    size                DOUBLE PRECISION,
    stop_loss           DOUBLE PRECISION,
    psi_at_entry        DOUBLE PRECISION,
    delta_at_entry      DOUBLE PRECISION,
    kelly_fraction      DOUBLE PRECISION,
    expected_edge       DOUBLE PRECISION,
    pnl                 DOUBLE PRECISION,
    pnl_pct             DOUBLE PRECISION,
    won                 BOOLEAN,
    opened_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at           TIMESTAMPTZ,
    lambda_at_entry     DOUBLE PRECISION,
    iq_at_entry         DOUBLE PRECISION
);
CREATE INDEX idx_trades_opened_at ON trades(opened_at DESC);
CREATE INDEX idx_trades_symbol ON trades(symbol);

-- Domain mastery snapshots
CREATE TABLE IF NOT EXISTS mastery_snapshots (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    domain          TEXT NOT NULL,
    mastery_score   DOUBLE PRECISION NOT NULL,
    knowledge_count INTEGER NOT NULL,
    tests_passed    INTEGER NOT NULL
);
CREATE INDEX idx_mastery_domain ON mastery_snapshots(domain, timestamp DESC);

-- Social posts
CREATE TABLE IF NOT EXISTS social_posts (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    platform    TEXT NOT NULL CHECK (platform IN ('twitter', 'discord', 'telegram')),
    content     TEXT NOT NULL,
    psi_at_post DOUBLE PRECISION,
    post_id     TEXT,
    quality     DOUBLE PRECISION,
    silenced    BOOLEAN DEFAULT FALSE,
    silence_reason TEXT
);
CREATE INDEX idx_social_platform ON social_posts(platform, timestamp DESC);

-- Moat history
CREATE TABLE IF NOT EXISTS moat_history (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    lambda_val  DOUBLE PRECISION NOT NULL,
    n_cycles    INTEGER NOT NULL,
    iq_score    DOUBLE PRECISION,
    pharos_tx   TEXT,
    event_type  TEXT
);
CREATE INDEX idx_moat_history_timestamp ON moat_history(timestamp DESC);
