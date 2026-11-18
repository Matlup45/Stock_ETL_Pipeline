"""TRANSFORM: standardise and validate raw price data."""
import pandas as pd

COLUMN_MAP = {
    "Date": "trade_date", "Open": "open", "High": "high", "Low": "low",
    "Close": "close", "Adj Close": "adj_close", "Volume": "volume",
    "Dividends": "dividends", "Stock Splits": "stock_splits",
}
FINAL_COLS = ["ticker", "trade_date", "open", "high", "low", "close",
              "adj_close", "volume", "dividends", "stock_splits"]


def clean_prices(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Rename columns, fix types, drop duplicates and rows with no close price."""
    if df.empty:
        return pd.DataFrame(columns=FINAL_COLS)
    out = df.rename(columns=COLUMN_MAP).copy()
    out["ticker"] = ticker
    # Drop the timezone but keep the local calendar date (2024-01-01 00:00+05:30 -> 2024-01-01)
    out["trade_date"] = pd.to_datetime(out["trade_date"]).dt.tz_localize(None).dt.date
    for col in ["dividends", "stock_splits"]:
        if col not in out:
            out[col] = 0.0
    out = out[FINAL_COLS]
    out = out.dropna(subset=["close"])
    out = out.drop_duplicates(subset=["ticker", "trade_date"], keep="last")
    out["volume"] = out["volume"].fillna(0).astype("int64")
    return out.reset_index(drop=True)


def validate_prices(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Row-level quality rules. Returns (valid_rows, rejected_rows)."""
    if df.empty:
        return df, df
    bad = (
        (df["high"] < df["low"])
        | (df[["open", "high", "low", "close"]] <= 0).any(axis=1)
        | (df["volume"] < 0)
    )
    return df[~bad].reset_index(drop=True), df[bad].reset_index(drop=True)