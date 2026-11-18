CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS ops;

CREATE TABLE IF NOT EXISTS raw.daily_prices (
    ticker        TEXT          NOT NULL,
    trade_date    DATE          NOT NULL,
    open          NUMERIC(18,4),
    high          NUMERIC(18,4),
    low           NUMERIC(18,4),
    close         NUMERIC(18,4),
    adj_close     NUMERIC(18,4),
    volume        BIGINT,
    dividends     NUMERIC(18,6) DEFAULT 0,
    stock_splits  NUMERIC(18,6) DEFAULT 0,
    ingested_at   TIMESTAMPTZ   NOT NULL DEFAULT now(),
    PRIMARY KEY (ticker, trade_date)
);

CREATE TABLE IF NOT EXISTS raw.stock_metadata (
    ticker    TEXT PRIMARY KEY,
    name      TEXT,
    sector    TEXT,
    exchange  TEXT,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ops.pipeline_runs (
    run_id        BIGSERIAL PRIMARY KEY,
    run_ts        TIMESTAMPTZ NOT NULL DEFAULT now(),
    ticker        TEXT,
    status        TEXT NOT NULL,
    rows_fetched  INT DEFAULT 0,
    rows_loaded   INT DEFAULT 0,
    rows_rejected INT DEFAULT 0,
    duration_sec  NUMERIC(10,2),
    error_message TEXT
);