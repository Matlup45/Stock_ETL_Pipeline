from datetime import date

from sqlalchemy import text

from stock_etl.extract import fetch_prices
from stock_etl.load import get_engine, get_watermark, upsert_prices
from stock_etl.transform import clean_prices, validate_prices

TICKER = "TCS.NS"
engine = get_engine()

raw = fetch_prices(TICKER, date(2024, 1, 1), date(2024, 1, 15))
valid, rejected = validate_prices(clean_prices(raw, TICKER))
loaded = upsert_prices(engine, valid)

with engine.connect() as conn:
    total = conn.execute(text("SELECT count(*) FROM raw.daily_prices")).scalar()

print(f"loaded={loaded} rejected={len(rejected)} total_rows_in_table={total}")
print("watermark:", get_watermark(engine, TICKER))
