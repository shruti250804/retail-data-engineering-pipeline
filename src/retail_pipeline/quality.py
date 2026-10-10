import json
from datetime import datetime, timezone
from pathlib import Path

def write_quality_outputs(metrics, rejected_df, report_path, rejected_path):
    report_path = Path(report_path)
    rejected_path = Path(rejected_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    rejected_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if metrics["rejected_rows"] == 0 else "PASS_WITH_REJECTIONS",
        **metrics,
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if not rejected_df.empty:
        rejected_df.to_csv(rejected_path, index=False)
    elif rejected_path.exists():
        rejected_path.unlink()
    return report
