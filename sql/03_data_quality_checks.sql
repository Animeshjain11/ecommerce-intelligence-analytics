-- 1. Check duplicate order IDs
SELECT COUNT(*) AS duplicate_order_ids
FROM (
    SELECT order_id
    FROM raw.orders
    GROUP BY order_id
    HAVING COUNT(*) > 1
) AS duplicates;

-- 2. Check missing or blank order IDs
SELECT COUNT(*) AS missing_order_ids
FROM raw.orders
WHERE order_id IS NULL
   OR TRIM(order_id) = '';

-- 3. Analyze order status distribution
SELECT
    order_status,
    COUNT(*) AS total_orders,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM raw.orders
GROUP BY order_status
ORDER BY total_orders DESC;
