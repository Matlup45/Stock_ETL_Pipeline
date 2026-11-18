"""Central configuration: environment variables and the ticker list."""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"

HISTORY_START_DATE = os.getenv("HISTORY_START_DATE", "2019-01-01")
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "5"))  # re-fetch recent days to catch corrections


def db_url() -> str:
    return (
        f"postgresql+psycopg2://{os.getenv('WAREHOUSE_USER', 'etl_user')}:"
        f"{os.getenv('WAREHOUSE_PASSWORD', '')}@"
        f"{os.getenv('WAREHOUSE_HOST', 'localhost')}:"
        f"{os.getenv('WAREHOUSE_PORT', '54332')}/"
        f"{os.getenv('WAREHOUSE_DB', 'stock_dw')}"
    )


def load_tickers() -> list[dict]:
    with open(ROOT / "config" / "tickers.yml") as f:
        return yaml.safe_load(f)["tickers"]