from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

ROOT_DIR = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT_DIR / "sql" / "schema.sql"

def sql_value(value):
    return None if pd.isna(value) else value

def load_to_postgres(clean_df, db_config, run_id, metrics):
    """Idempotently upsert dimension and fact rows; record each pipeline run."""
    conn = psycopg2.connect(**db_config)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(SCHEMA_PATH.read_text(encoding="utf-8"))

                customers = clean_df[
                    ["customer_id", "customer_name", "customer_email", "city", "customer_type"]
                ].drop_duplicates(subset=["customer_id"], keep="last")
                products = clean_df[
                    ["product_id", "product_name", "category", "unit_cost"]
                ].drop_duplicates(subset=["product_id"], keep="last")

                if not customers.empty:
                    customer_rows = [
                        tuple(sql_value(v) for v in row)
                        for row in customers.itertuples(index=False, name=None)
                    ]
                    execute_values(cur, '''
                        INSERT INTO dim_customers
                            (customer_id, customer_name, customer_email, city, customer_type)
                        VALUES %s
                        ON CONFLICT (customer_id) DO UPDATE SET
                            customer_name = EXCLUDED.customer_name,
                            customer_email = EXCLUDED.customer_email,
                            city = EXCLUDED.city,
                            customer_type = EXCLUDED.customer_type
                    ''', customer_rows)

                if not products.empty:
                    product_rows = [
                        tuple(sql_value(v) for v in row)
                        for row in products.itertuples(index=False, name=None)
                    ]
                    execute_values(cur, '''
                        INSERT INTO dim_products (product_id, product_name, category, unit_cost)
                        VALUES %s
                        ON CONFLICT (product_id) DO UPDATE SET
                            product_name = EXCLUDED.product_name,
                            category = EXCLUDED.category,
                            unit_cost = EXCLUDED.unit_cost
                    ''', product_rows)

                if not clean_df.empty:
                    fact_rows = []
                    for row in clean_df.itertuples(index=False):
                        fact_rows.append((
                            row.order_line_id, row.order_id, row.order_date,
                            row.customer_id, row.product_id, int(row.quantity),
                            float(row.unit_price), float(row.discount),
                            float(row.gross_revenue), float(row.net_revenue),
                            float(row.profit),
                        ))
                    execute_values(cur, '''
                        INSERT INTO fact_sales
                            (order_line_id, order_id, order_date, customer_id, product_id,
                             quantity, unit_price, discount, gross_revenue, net_revenue, profit)
                        VALUES %s
                        ON CONFLICT (order_line_id) DO UPDATE SET
                            order_id = EXCLUDED.order_id,
                            order_date = EXCLUDED.order_date,
                            customer_id = EXCLUDED.customer_id,
                            product_id = EXCLUDED.product_id,
                            quantity = EXCLUDED.quantity,
                            unit_price = EXCLUDED.unit_price,
                            discount = EXCLUDED.discount,
                            gross_revenue = EXCLUDED.gross_revenue,
                            net_revenue = EXCLUDED.net_revenue,
                            profit = EXCLUDED.profit
                    ''', fact_rows)

                cur.execute('''
                    INSERT INTO etl_run_log
                        (run_id, status, input_rows, accepted_rows, rejected_rows,
                         duplicate_rows_removed, finished_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (run_id) DO UPDATE SET
                        status = EXCLUDED.status,
                        input_rows = EXCLUDED.input_rows,
                        accepted_rows = EXCLUDED.accepted_rows,
                        rejected_rows = EXCLUDED.rejected_rows,
                        duplicate_rows_removed = EXCLUDED.duplicate_rows_removed,
                        finished_at = EXCLUDED.finished_at
                ''', (
                    run_id, "SUCCESS", metrics["input_rows"], metrics["accepted_rows"],
                    metrics["rejected_rows"], metrics["duplicate_rows_removed"]
                ))
    finally:
        conn.close()
