import pandas as pd

TEXT_COLUMNS = [
    "order_line_id", "order_id", "customer_id", "customer_name",
    "customer_email", "product_id", "product_name", "category", "city",
    "customer_type",
]

def transform_data(raw_df):
    """Clean rows and return (accepted_df, rejected_df, metrics)."""
    df = raw_df.copy()
    input_rows = len(df)

    for col in TEXT_COLUMNS:
        df[col] = df[col].astype("string").str.strip()

    df["customer_email"] = df["customer_email"].str.lower()
    for col in ["category", "city", "customer_type"]:
        df[col] = df[col].str.title()

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    for col in ["quantity", "unit_price", "discount", "unit_cost"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # An order line is uniquely identified by order_line_id. Keep first occurrence.
    duplicate_mask = df["order_line_id"].duplicated(keep="first")
    duplicate_count = int(duplicate_mask.sum())
    df = df.loc[~duplicate_mask].copy()

    required = [
        "order_line_id", "order_id", "order_date", "customer_id",
        "customer_name", "product_id", "product_name", "category",
        "quantity", "unit_price", "discount", "unit_cost",
    ]
    valid = df[required].notna().all(axis=1)
    valid &= df["quantity"] > 0
    valid &= df["unit_price"] >= 0
    valid &= df["unit_cost"] >= 0
    valid &= df["discount"].between(0, 1, inclusive="both")
    for col in ["order_line_id", "order_id", "customer_id", "product_id"]:
        valid &= df[col].ne("")

    rejected = df.loc[~valid].copy()
    clean = df.loc[valid].copy()
    clean["quantity"] = clean["quantity"].astype(int)
    clean["unit_price"] = clean["unit_price"].round(2)
    clean["unit_cost"] = clean["unit_cost"].round(2)
    clean["discount"] = clean["discount"].round(4)
    clean["order_date"] = clean["order_date"].dt.date
    clean["gross_revenue"] = (clean["quantity"] * clean["unit_price"]).round(2)
    clean["net_revenue"] = (
        clean["quantity"] * clean["unit_price"] * (1 - clean["discount"])
    ).round(2)
    clean["profit"] = (
        clean["quantity"] * (clean["unit_price"] * (1 - clean["discount"]) - clean["unit_cost"])
    ).round(2)

    metrics = {
        "input_rows": int(input_rows),
        "duplicate_rows_removed": duplicate_count,
        "rejected_rows": int(len(rejected)),
        "accepted_rows": int(len(clean)),
    }
    return clean.reset_index(drop=True), rejected.reset_index(drop=True), metrics
