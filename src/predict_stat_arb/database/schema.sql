CREATE TABLE IF NOT EXISTS kalshi_price_history (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    price NUMERIC(10, 4),
    yes_bid NUMERIC(10, 4),
    yes_ask NUMERIC(10, 4),
    volume NUMERIC(18, 4),
    open_interest NUMERIC(18, 4),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (ticker, timestamp)
);

CREATE TABLE IF NOT EXISTS polymarket_price_history (
    id BIGSERIAL PRIMARY KEY,
    token_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    price NUMERIC(10, 4) NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (token_id, timestamp)
);

CREATE TABLE IF NOT EXISTS house_2026_dem_spread (
    timestamp TIMESTAMPTZ PRIMARY KEY,
    kalshi_yes_price NUMERIC(10, 4) NOT NULL,
    polymarket_yes_price NUMERIC(10, 4) NOT NULL,
    dem_spread NUMERIC(10, 4) NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kalshi_price_history_ticker_timestamp
    ON kalshi_price_history (ticker, timestamp);

CREATE INDEX IF NOT EXISTS idx_polymarket_price_history_token_timestamp
    ON polymarket_price_history (token_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_house_2026_dem_spread_timestamp
    ON house_2026_dem_spread (timestamp);
