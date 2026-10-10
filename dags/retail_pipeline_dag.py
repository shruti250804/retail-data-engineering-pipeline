"""Optional Airflow DAG example; install/configure Airflow separately."""
import os
import sys
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_DIR = os.environ.get("RETAIL_PROJECT_DIR", "/opt/retail_data_engineering_final")
sys.path.insert(0, str(os.path.join(PROJECT_DIR, "src")))

def run_retail_pipeline():
    from retail_pipeline.pipeline import run_pipeline
    run_pipeline()

with DAG(
    dag_id="retail_analytics_etl",
    description="Run the retail CSV-to-PostgreSQL ETL pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["retail", "etl", "portfolio"],
) as dag:
    run_pipeline = PythonOperator(
        task_id="extract_transform_quality_and_load",
        python_callable=run_retail_pipeline,
    )
