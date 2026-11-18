"""LOAD: idempotent writes into Postgres."""
from datetime import date, datetime

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from . import config
from .logger import get_logger

log = get_logger(__name__)


def get_engine() -> Engine:
    return create_engine(config.db_url(), pool_pre_ping=True)


def get_watermark(engine: Engine, ticker: str) -> date | None:
    """Latest trade_date already loaded for a ticker (None on the first load)."""
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT max(trade_date) FROM raw.daily_prices WHERE ticker = :t"),
            {"t": ticker},
        ).scalar()


def upsert_prices(engine: Engine, df: pd.DataFrame) -> int:
    """INSERT ... ON CONFLICT DO UPDATE: re-running never creates duplicates."""
    if df.empty:
        return 0
    sql = text("""
        INSERT INTO raw.daily_prices
            (ticker, trade_date, open, high, low, close, adj_close,
             volume, dividends, stock_splits)
        VALUES
            (:ticker, :trade_date, :open, :high, :low, :close, :adj_close,
             :volume, :dividends, :stock_splits)
        ON CONFLICT (ticker, trade_date) DO UPDATE SET
            open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low,
            close = EXCLUDED.close, adj_close = EXCLUDED.adj_close,
            volume = EXCLUDED.volume, dividends = EXCLUDED.dividends,
            stock_splits = EXCLUDED.stock_splits, ingested_at = now()
    """)
    # NaN -> None so the database stores NULL instead of the text 'NaN'
    clean = df.astype(object).where(df.notna(), None)
    records = clean.to_dict(orient="records")
    with engine.begin() as conn:      # one transaction: all rows load, or none do
        conn.execute(sql, records)
    return len(records)

def save_raw_parquet(df: pd.DataFrame, ticker: str) -> None:
    """Keep an untouched copy of what the API returned: data/raw/prices/ticker=X/run_date=....parquet"""
    if df.empty:
        return
    folder = config.RAW_DIR / "prices" / f"ticker={ticker}"
    folder.mkdir(parents=True, exist_ok=True)
    df.to_parquet(folder / f"run_date={datetime.now():%Y-%m-%d}.parquet", index=False)


def upsert_metadata(engine: Engine, tickers: list[dict]) -> None:
    sql = text("""
        INSERT INTO raw.stock_metadata (ticker, name, sector, exchange)
        VALUES (:symbol, :name, :sector, :exchange)
        ON CONFLICT (ticker) DO UPDATE SET
            name = EXCLUDED.name, sector = EXCLUDED.sector,
            exchange = EXCLUDED.exchange, loaded_at = now()
    """)
    with engine.begin() as conn:
        conn.execute(sql, tickers)


def log_run(engine: Engine, ticker: str, status: str, fetched=0, loaded=0,
            rejected=0, duration=0.0, error: str | None = None) -> None:
    """One row per ticker per run in ops.pipeline_runs (powers the health dashboard later)."""
    sql = text("""
        INSERT INTO ops.pipeline_runs
            (ticker, status, rows_fetched, rows_loaded, rows_rejected, duration_sec, error_message)
        VALUES (:t, :s, :f, :l, :r, :d, :e)
    """)
    with engine.begin() as conn:
        conn.execute(sql, {"t": ticker, "s": status, "f": fetched, "l": loaded,
                           "r": rejected, "d": duration, "e": error})