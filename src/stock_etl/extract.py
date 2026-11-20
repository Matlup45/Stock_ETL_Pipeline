"""EXTRACT: pull daily OHLCV prices from Yahoo Finance, with retries."""
from datetime import date

import pandas as pd
import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential

from .logger import get_logger

log = get_logger(__name__)


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2, min=2, max=30), reraise=True)
def fetch_prices(ticker: str, start: date, end: date) -> pd.DataFrame:
    """Fetch daily prices in [start, end). Note: yfinance 'end' is exclusive."""
    log.info("Fetching %s from %s to %s", ticker, start, end)
    df = yf.Ticker(ticker).history(start=str(start), end=str(end), auto_adjust=False, timeout=20)
    if df is None or df.empty:
        return pd.DataFrame()
    return df.reset_index()