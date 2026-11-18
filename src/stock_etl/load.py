"""LOAD: idempotent writes into Postgres."""
from datetime import date

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