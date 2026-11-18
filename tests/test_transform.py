import pandas as pd

from stock_etl.transform import clean_prices, validate_prices


def _raw():
    return pd.DataFrame({
        "Date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-03"]),
        "Open": [10, 10, 11, 12],
        "High": [12, 12, 10, 14],
        "Low": [9, 9, 10.5, 11],
        "Close": [11, 11.5, 10.8, None],
        "Adj Close": [11, 11.5, 10.8, None],
        "Volume": [100, 100, 200, 300],
        "Dividends": [0, 0, 0, 0],
        "Stock Splits": [0, 0, 0, 0],
    })


def test_clean_drops_null_close_and_duplicates():
    out = clean_prices(_raw(), "TEST.NS")
    assert len(out) == 2                       # 1 duplicate and 1 null close removed
    assert out["ticker"].unique().tolist() == ["TEST.NS"]


def test_validate_rejects_high_below_low():
    out = clean_prices(_raw(), "TEST.NS")
    valid, rejected = validate_prices(out)
    assert len(rejected) == 1                  # Jan 2 has high (10) < low (10.5)
    assert len(valid) == 1