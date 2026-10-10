import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from retail_pipeline.transform import transform_data

def base_row(**overrides):
    row = {
        "order_line_id": "L1", "order_id": "O1", "order_date": "2026-01-01",
        "customer_id": "C1", "customer_name": " Ada Lovelace ",
        "customer_email": "ADA@EXAMPLE.COM", "product_id": "P1",
        "product_name": " Notebook ", "category": "stationery", "city": "new delhi",
        "customer_type": "consumer", "quantity": "2", "unit_price": "100",
        "discount": "0.10", "unit_cost": "50",
    }
    row.update(overrides)
    return row

def test_normalization_and_revenue_calculations():
    clean, rejected, metrics = transform_data(pd.DataFrame([base_row()]))
    assert len(clean) == 1
    assert rejected.empty
    row = clean.iloc[0]
    assert row["customer_name"] == "Ada Lovelace"
    assert row["customer_email"] == "ada@example.com"
    assert row["category"] == "Stationery"
    assert row["city"] == "New Delhi"
    assert row["gross_revenue"] == 200
    assert row["net_revenue"] == 180
    assert row["profit"] == 80
    assert metrics["accepted_rows"] == 1

def test_duplicate_order_line_removed():
    clean, rejected, metrics = transform_data(pd.DataFrame([base_row(), base_row()]))
    assert len(clean) == 1
    assert metrics["duplicate_rows_removed"] == 1

def test_invalid_quantity_discount_and_date_rejected():
    rows = [
        base_row(order_line_id="L2", quantity="-1"),
        base_row(order_line_id="L3", discount="1.5"),
        base_row(order_line_id="L4", order_date="not-a-date"),
    ]
    clean, rejected, metrics = transform_data(pd.DataFrame(rows))
    assert clean.empty
    assert len(rejected) == 3
    assert metrics["rejected_rows"] == 3

def test_negative_cost_rejected():
    clean, rejected, metrics = transform_data(pd.DataFrame([base_row(unit_cost="-5")]))
    assert clean.empty
    assert len(rejected) == 1
