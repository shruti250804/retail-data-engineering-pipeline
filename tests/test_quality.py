import json
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from retail_pipeline.quality import write_quality_outputs

def test_quality_report_and_rejected_rows(tmp_path):
    rejected = pd.DataFrame([{"order_line_id": "bad", "quantity": -1}])
    report_path = tmp_path / "reports" / "report.json"
    rejected_path = tmp_path / "reports" / "rejected.csv"
    metrics = {
        "input_rows": 2, "duplicate_rows_removed": 0,
        "rejected_rows": 1, "accepted_rows": 1,
    }
    report = write_quality_outputs(metrics, rejected, report_path, rejected_path)
    saved = json.loads(report_path.read_text(encoding="utf-8"))
    assert saved["status"] == "PASS_WITH_REJECTIONS"
    assert saved["accepted_rows"] == 1
    assert rejected_path.exists()
