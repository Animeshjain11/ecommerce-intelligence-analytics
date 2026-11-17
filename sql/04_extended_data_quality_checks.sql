-- 1. Duplicate customer IDs
SELECT COUNT(*) AS duplicate_customer_ids
FROM (
    SELECT customer_id
    FROM raw.customers
    GROUP BY customer_id
    HAVING COUNT(*) > 1
) AS duplicates;

-- 2. Duplicate product IDs
SELECT COUNT(*) AS duplicate_product_ids
FROM (
    SELECT product_id
    FROM raw.products
    GROUP BY product_id
    HAVING COUNT(*) > 1
) AS duplicates;

-- 3. Duplicate seller IDs
SELECT COUNT(*) AS duplicate_seller_ids
FROM (
    SELECT seller_id
    FROM raw.sellers
    GROUP BY seller_id
    HAVING COUNT(*) > 1
) AS duplicates;

-- 4. Missing order or order-item IDs
SELECT COUNT(*) AS missing_order_item_ids
FROM raw.order_items
WHERE order_id IS NULL
   OR TRIM(order_id) = ''
   OR order_item_id IS NULL
   OR TRIM(order_item_id) = '';

-- 5. Missing payment order IDs
SELECT COUNT(*) AS missing_payment_order_ids
FROM raw.payments
WHERE order_id IS NULL
   OR TRIM(order_id) = '';

-- 6. Invalid product prices
-- Product prices are stored in raw.order_items.price
SELECT COUNT(*) AS invalid_product_prices
FROM raw.order_items
WHERE price IS NULL
   OR TRIM(price) = ''
   OR CASE
        WHEN TRIM(price) ~ '^[0-9]+([.][0-9]+)?$'
        THEN price::numeric <= 0
        ELSE TRUE
      END;

-- 7. Invalid product weights
SELECT COUNT(*) AS invalid_product_weights
FROM raw.products
WHERE product_weight_g IS NULL
   OR TRIM(product_weight_g) = ''
   OR CASE
        WHEN TRIM(product_weight_g) ~ '^[0-9]+([.][0-9]+)?$'
        THEN product_weight_g::numeric < 0
        ELSE TRUE
      END;

-- 8. Missing purchase timestamps
SELECT COUNT(*) AS missing_purchase_timestamps
FROM raw.orders
WHERE order_purchase_timestamp IS NULL
   OR TRIM(order_purchase_timestamp) = '';

-- 9. Zero-value payment records
SELECT COUNT(*) AS zero_value_payment_records
FROM raw.payments
WHERE TRIM(payment_value) ~ '^[0-9]+([.][0-9]+)?$'
  AND payment_value::numeric = 0;

-- 10. Invalid payment values
-- Zero values are reported separately above
SELECT COUNT(*) AS invalid_payment_values
FROM raw.payments
WHERE payment_value IS NULL
   OR TRIM(payment_value) = ''
   OR CASE
        WHEN TRIM(payment_value) ~ '^[0-9]+([.][0-9]+)?$'
        THEN payment_value::numeric < 0
        ELSE TRUE
      END;
