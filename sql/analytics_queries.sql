-- 1. Core business KPIs
SELECT COUNT(*) AS order_lines,
       SUM(quantity) AS units_sold,
       ROUND(SUM(gross_revenue), 2) AS gross_revenue,
       ROUND(SUM(net_revenue), 2) AS net_revenue,
       ROUND(SUM(profit), 2) AS total_profit
FROM fact_sales;

-- 2. Monthly sales and profit trend
SELECT DATE_TRUNC('month', order_date)::date AS month,
       ROUND(SUM(net_revenue), 2) AS net_revenue,
       ROUND(SUM(profit), 2) AS profit
FROM fact_sales
GROUP BY 1
ORDER BY 1;

-- 3. Category performance
SELECT p.category, SUM(f.quantity) AS units_sold,
       ROUND(SUM(f.net_revenue), 2) AS net_revenue,
       ROUND(SUM(f.profit), 2) AS profit
FROM fact_sales f
JOIN dim_products p USING (product_id)
GROUP BY p.category
ORDER BY net_revenue DESC;

-- 4. City performance
SELECT c.city, ROUND(SUM(f.net_revenue), 2) AS net_revenue
FROM fact_sales f
JOIN dim_customers c USING (customer_id)
GROUP BY c.city
ORDER BY net_revenue DESC;

-- 5. Customer-type comparison
SELECT c.customer_type, COUNT(DISTINCT f.order_id) AS orders,
       ROUND(SUM(f.net_revenue), 2) AS net_revenue,
       ROUND(SUM(f.profit), 2) AS profit
FROM fact_sales f
JOIN dim_customers c USING (customer_id)
GROUP BY c.customer_type
ORDER BY net_revenue DESC;

-- 6. Top 10 products by net revenue
SELECT p.product_name, p.category, SUM(f.quantity) AS units_sold,
       ROUND(SUM(f.net_revenue), 2) AS net_revenue
FROM fact_sales f
JOIN dim_products p USING (product_id)
GROUP BY p.product_id, p.product_name, p.category
ORDER BY net_revenue DESC
LIMIT 10;

-- 7. Pipeline run history
SELECT * FROM etl_run_log ORDER BY finished_at DESC;

-- 8. Data integrity check: expected to return zero rows
SELECT * FROM fact_sales
WHERE quantity <= 0 OR unit_price < 0 OR discount < 0 OR discount > 1;
