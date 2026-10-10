from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from retail_pipeline.config import CLEAN_DATA_PATH
from retail_pipeline.s3_storage import upload_file_to_s3

if __name__ == "__main__":
    print("Uploaded:", upload_file_to_s3(CLEAN_DATA_PATH))
