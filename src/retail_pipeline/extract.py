import pandas as pd

REQUIRED_COLUMNS = [
    "order_line_id", "order_id", "order_date", "customer_id", "customer_name",
    "customer_email", "product_id", "product_name", "category", "city",
    "customer_type", "quantity", "unit_price", "discount", "unit_cost",
]

def extract_csv(path):
    df = pd.read_csv(path, dtype={
        "order_line_id": "string", "order_id": "string",
        "customer_id": "string", "product_id": "string",
    })
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Input CSV is missing required columns: {missing}")
    return df[REQUIRED_COLUMNS].copy()
