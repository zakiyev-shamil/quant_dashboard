-- QuantLab Lite — PostgreSQL Schema
-- Run this manually to create the database tables.
--
-- Usage:
--   1. Create database:  CREATE DATABASE quantlab;
--   2. Connect:          \c quantlab
--   3. Run this file:    \i db_schema.sql

-- ============================================================
-- Prices table — stores OHLCV data from yfinance
-- ============================================================
CREATE TABLE IF NOT EXISTS prices (
    id            BIGSERIAL PRIMARY KEY,
    symbol        VARCHAR(20)    NOT NULL,
    date          DATE           NOT NULL,
    interval      VARCHAR(10)    NOT NULL DEFAULT '1d',
    open          DOUBLE PRECISION,
    high          DOUBLE PRECISION,
    low           DOUBLE PRECISION,
    close         DOUBLE PRECISION,
    adjusted_close DOUBLE PRECISION,
    volume        BIGINT,
    source        VARCHAR(20)    NOT NULL DEFAULT 'yfinance',
    created_at    TIMESTAMP      NOT NULL DEFAULT NOW(),

    -- Prevent duplicate entries for same symbol + date + interval
    CONSTRAINT uq_prices_symbol_date_interval UNIQUE (symbol, date, interval)
);

-- Index for fast lookups by symbol
CREATE INDEX IF NOT EXISTS idx_prices_symbol ON prices (symbol);

-- Index for fast range queries
CREATE INDEX IF NOT EXISTS idx_prices_symbol_date ON prices (symbol, date);

-- Index for interval filtering
CREATE INDEX IF NOT EXISTS idx_prices_symbol_interval ON prices (symbol, interval);

-- Composite index for the most common query pattern
CREATE INDEX IF NOT EXISTS idx_prices_symbol_date_interval ON prices (symbol, date, interval);


-- ============================================================
-- Data status table — tracks download metadata per symbol
-- ============================================================
CREATE TABLE IF NOT EXISTS data_status (
    id            SERIAL PRIMARY KEY,
    symbol        VARCHAR(20)    NOT NULL,
    interval      VARCHAR(10)    NOT NULL DEFAULT '1d',
    first_date    DATE,
    last_date     DATE,
    row_count     INTEGER        DEFAULT 0,
    last_updated  TIMESTAMP      NOT NULL DEFAULT NOW(),
    source        VARCHAR(20)    NOT NULL DEFAULT 'yfinance',

    CONSTRAINT uq_data_status_symbol_interval UNIQUE (symbol, interval)
);
