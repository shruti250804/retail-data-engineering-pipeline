CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    customer_email TEXT,
    city TEXT,
    customer_type TEXT
);

CREATE TABLE IF NOT EXISTS dim_products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_cost NUMERIC(12,2) NOT NULL CHECK (unit_cost >= 0)
);

CREATE TABLE IF NOT EXISTS fact_sales (
    order_line_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    order_date DATE NOT NULL,
    customer_id TEXT NOT NULL REFERENCES dim_customers(customer_id),
    product_id TEXT NOT NULL REFERENCES dim_products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    discount NUMERIC(5,4) NOT NULL CHECK (discount >= 0 AND discount <= 1),
    gross_revenue NUMERIC(14,2) NOT NULL,
    net_revenue NUMERIC(14,2) NOT NULL,
    profit NUMERIC(14,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS etl_run_log (
    run_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    input_rows INTEGER NOT NULL,
    accepted_rows INTEGER NOT NULL,
    rejected_rows INTEGER NOT NULL,
    duplicate_rows_removed INTEGER NOT NULL,
    finished_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fact_sales_order_date ON fact_sales(order_date);
CREATE INDEX IF NOT EXISTS idx_fact_sales_customer ON fact_sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON fact_sales(product_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_order ON fact_sales(order_id);
