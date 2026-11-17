
-- 1. Monthly order volume
\copy (SELECT TO_CHAR(order_purchase_timestamp, 'YYYY-MM') AS order_month, COUNT(*) AS total_orders FROM staging.orders GROUP BY 1 ORDER BY 1) TO 'powerbi/exports/monthly_orders.csv' WITH (FORMAT CSV, HEADER TRUE);

-- 2. Monthly sales and freight
\copy (SELECT TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM') AS order_month, COUNT(DISTINCT o.order_id) AS total_orders, ROUND(SUM(oi.price), 2) AS product_sales, ROUND(SUM(oi.freight_value), 2) AS freight_revenue, ROUND(SUM(oi.price + oi.freight_value), 2) AS sales_plus_freight FROM staging.orders o JOIN staging.order_items oi ON o.order_id = oi.order_id WHERE o.order_status <> 'canceled' GROUP BY 1 ORDER BY 1) TO 'powerbi/exports/monthly_sales.csv' WITH (FORMAT CSV, HEADER TRUE);

-- 3. Order status summary
\copy (SELECT order_status, COUNT(*) AS total_orders, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage FROM staging.orders GROUP BY 1 ORDER BY total_orders DESC) TO 'powerbi/exports/order_status.csv' WITH (FORMAT CSV, HEADER TRUE);

-- 4. Top 10 product categories
\copy (SELECT COALESCE(NULLIF(TRIM(p.product_category_name), ''), 'Unknown') AS product_category, COUNT(*) AS items_sold, ROUND(SUM(oi.price), 2) AS product_sales FROM staging.order_items oi JOIN staging.products p ON oi.product_id = p.product_id JOIN staging.orders o ON oi.order_id = o.order_id WHERE o.order_status <> 'canceled' GROUP BY 1 ORDER BY product_sales DESC LIMIT 10) TO 'powerbi/exports/top_categories.csv' WITH (FORMAT CSV, HEADER TRUE);

-- 5. Payment method analysis
\copy (SELECT payment_type, COUNT(*) AS payment_records, ROUND(SUM(payment_value), 2) AS total_payment_value, ROUND(AVG(payment_value), 2) AS average_payment_value FROM staging.payments GROUP BY 1 ORDER BY total_payment_value DESC) TO 'powerbi/exports/payment_methods.csv' WITH (FORMAT CSV, HEADER TRUE);

-- 6. Delivery performance
\copy (SELECT COUNT(*) FILTER (WHERE order_delivered_customer_date IS NOT NULL) AS delivered_orders, ROUND(AVG(EXTRACT(EPOCH FROM (order_delivered_customer_date - order_purchase_timestamp)) / 86400.0) FILTER (WHERE order_delivered_customer_date IS NOT NULL), 2) AS avg_days_to_deliver, COUNT(*) FILTER (WHERE order_delivered_customer_date > order_estimated_delivery_date) AS delivered_late_orders FROM staging.orders) TO 'powerbi/exports/delivery_performance.csv' WITH (FORMAT CSV, HEADER TRUE);
