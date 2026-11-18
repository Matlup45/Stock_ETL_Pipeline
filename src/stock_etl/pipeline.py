"""Runs Extract -> Transform -> Validate -> Load for every ticker.

Usage:
    python -m stock_etl.pipeline                         # incremental, all tickers
    python -m stock_etl.pipeline --tickers TCS.NS INFY.NS
    python -m stock_etl.pipeline --backfill-from 2015-01-01
"""
import argparse
import time
from datetime import date, timedelta

from . import config
from .extract import fetch_prices
from .load import (get_engine, get_watermark, log_run, save_raw_parquet,
                   upsert_metadata, upsert_prices)
from .logger import get_logger
from .transform import clean_prices, validate_prices

log = get_logger(__name__)


def run(tickers: list[str] | None = None, backfill_from: str | None = None) -> None:
    engine = get_engine()
    meta = config.load_tickers()
    upsert_metadata(engine, meta)
    symbols = tickers or [t["symbol"] for t in meta]
    end = date.today() + timedelta(days=1)          # yfinance 'end' is exclusive
    failures: list[str] = []

    for ticker in symbols:
        t0 = time.time()
        try:
            if backfill_from:
                start = date.fromisoformat(backfill_from)
            else:
                watermark = get_watermark(engine, ticker)
                if watermark:   # incremental: restart a few days early to catch corrections
                    start = watermark - timedelta(days=config.LOOKBACK_DAYS)
                else:           # first ever load
                    start = date.fromisoformat(config.HISTORY_START_DATE)

            raw = fetch_prices(ticker, start, end)
            if raw.empty:
                log.warning("%s: no data returned", ticker)
                log_run(engine, ticker, "NO_DATA", duration=time.time() - t0)
                continue

            save_raw_parquet(raw, ticker)
            clean = clean_prices(raw, ticker)
            valid, rejected = validate_prices(clean)
            loaded = upsert_prices(engine, valid)

            log_run(engine, ticker, "SUCCESS", len(raw), loaded, len(rejected), time.time() - t0)
            log.info("%s: fetched=%d loaded=%d rejected=%d", ticker, len(raw), loaded, len(rejected))
        except Exception as exc:   # one bad ticker must not stop the others
            log.exception("%s failed", ticker)
            log_run(engine, ticker, "FAILED", duration=time.time() - t0, error=str(exc)[:500])
            failures.append(ticker)

    if failures:   # still fail loudly at the end, so schedulers and alerts notice
        raise RuntimeError(f"ETL failed for tickers: {failures}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", nargs="*")
    parser.add_argument("--backfill-from")
    args = parser.parse_args()
    run(args.tickers, args.backfill_from)