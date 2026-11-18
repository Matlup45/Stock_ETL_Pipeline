"""Create schemas and tables by running sql/init/01_init.sql.
Safe to run repeatedly (the SQL uses IF NOT EXISTS)."""
from pathlib import Path

from stock_etl.load import get_engine

sql = (Path(__file__).resolve().parents[1] / "sql" / "init" / "01_init.sql").read_text()

with get_engine().begin() as conn:
    conn.exec_driver_sql(sql)

print("Database initialised: schemas raw/staging/marts/ops and tables are ready.")