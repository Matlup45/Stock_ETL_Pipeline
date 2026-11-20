"""Daily stock pipeline: extract/transform/load -> dbt run -> dbt test.

Schedule: 11:00 UTC = 16:30 IST, after NSE closes (15:30 IST), Monday to Friday.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

DBT = "/home/airflow/dbt_venv/bin/dbt"
DBT_ARGS = "--project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/dbt"

# dbt writes logs and build files; keep them inside the container, not on the Windows drive
DBT_ENV = {"DBT_TARGET_PATH": "/tmp/dbt_target", "DBT_LOG_PATH": "/tmp/dbt_logs"}

default_args = {
    "owner": "data-eng",
    "retries": 3,                           # try again if the API hiccups
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,      # wait longer after each failure
    "execution_timeout": timedelta(minutes=15),
}


def _extract_transform_load():
    from stock_etl.pipeline import run
    run()


with DAG(
    dag_id="stock_etl_daily",
    description="Incremental NSE prices -> Postgres -> dbt models and tests",
    start_date=datetime(2024, 1, 1),
    schedule="0 11 * * 1-5",
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    tags=["stocks", "etl"],
) as dag:

    etl = PythonOperator(
        task_id="extract_transform_load",
        python_callable=_extract_transform_load,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"{DBT} run {DBT_ARGS}",
        env=DBT_ENV,
        append_env=True,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"{DBT} test {DBT_ARGS}",
        env=DBT_ENV,
        append_env=True,
    )

    etl >> dbt_run >> dbt_test       # the order the tasks run in