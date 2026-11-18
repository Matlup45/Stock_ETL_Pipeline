"""Central configuration. Reads settings from the .env file."""
import os

from dotenv import load_dotenv

load_dotenv()


def db_url() -> str:
    return (
        f"postgresql+psycopg2://{os.getenv('WAREHOUSE_USER', 'etl_user')}:"
        f"{os.getenv('WAREHOUSE_PASSWORD', '')}@"
        f"{os.getenv('WAREHOUSE_HOST', 'localhost')}:"
        f"{os.getenv('WAREHOUSE_PORT', '54332')}/"
        f"{os.getenv('WAREHOUSE_DB', 'stock_dw')}"
    )