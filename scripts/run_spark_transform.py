from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from retail_pipeline.config import RAW_DATA_PATH, ROOT_DIR
from retail_pipeline.spark_transform import transform_csv_with_spark

if __name__ == "__main__":
    output = ROOT_DIR / "data" / "processed" / "spark_output"
    transform_csv_with_spark(RAW_DATA_PATH, output)
