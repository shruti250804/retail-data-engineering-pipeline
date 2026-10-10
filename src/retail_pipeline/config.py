import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

RAW_DATA_PATH = ROOT_DIR / "data" / "raw" / "retail_transactions.csv"
CLEAN_DATA_PATH = ROOT_DIR / "data" / "processed" / "retail_transactions_clean.csv"
QUALITY_REPORT_PATH = ROOT_DIR / "reports" / "data_quality_report.json"
REJECTED_ROWS_PATH = ROOT_DIR / "reports" / "rejected_rows.csv"
LOG_PATH = ROOT_DIR / "logs" / "pipeline.log"

def get_db_config():
    required = ["PGHOST", "PGDATABASE", "PGUSER", "PGPASSWORD"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise ValueError(
            f"Missing database settings: {', '.join(missing)}. "
            "Copy .env.example to .env and set your PostgreSQL credentials."
        )
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "dbname": os.getenv("PGDATABASE", "retail_analytics"),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD"),
    }
