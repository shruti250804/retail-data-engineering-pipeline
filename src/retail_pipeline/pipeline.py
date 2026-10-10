import logging
import uuid
from datetime import datetime, timezone

from .config import (
    RAW_DATA_PATH, CLEAN_DATA_PATH, QUALITY_REPORT_PATH, REJECTED_ROWS_PATH,
    LOG_PATH, get_db_config,
)
from .extract import extract_csv
from .transform import transform_data
from .quality import write_quality_outputs
from .load import load_to_postgres

def configure_logging():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )

def run_pipeline():
    configure_logging()
    logger = logging.getLogger("retail_pipeline")
    run_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc)
    logger.info("Pipeline started; run_id=%s", run_id)
    try:
        raw_df = extract_csv(RAW_DATA_PATH)
        logger.info("Extracted %d rows", len(raw_df))

        clean_df, rejected_df, metrics = transform_data(raw_df)
        report = write_quality_outputs(
            metrics, rejected_df, QUALITY_REPORT_PATH, REJECTED_ROWS_PATH
        )
        CLEAN_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        clean_df.to_csv(CLEAN_DATA_PATH, index=False)
        logger.info("Data quality report: %s", report)
        if not rejected_df.empty:
            logger.warning("%d rows rejected; see %s", len(rejected_df), REJECTED_ROWS_PATH)

        load_to_postgres(clean_df, get_db_config(), run_id, metrics)
        elapsed = (datetime.now(timezone.utc) - started).total_seconds()
        logger.info("Pipeline succeeded in %.2f seconds; run_id=%s", elapsed, run_id)
        print("\nPipeline completed successfully.")
        print(f"Run ID: {run_id}")
        print(f"Rows read: {metrics['input_rows']}")
        print(f"Duplicates removed: {metrics['duplicate_rows_removed']}")
        print(f"Rows rejected: {metrics['rejected_rows']}")
        print(f"Rows accepted/upserted: {metrics['accepted_rows']}")
        print(f"Quality report: {QUALITY_REPORT_PATH}")
        print(f"Clean output: {CLEAN_DATA_PATH}")
    except Exception:
        logger.exception("Pipeline failed; run_id=%s", run_id)
        raise
