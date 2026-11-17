
-- Project: E-Commerce Intelligence & Business Performance Analytics
-- Purpose: Create typed staging tables from raw CSV data

CREATE TABLE IF NOT EXISTS staging.orders AS
SELECT
    NULLIF(TRIM(order_id), '') AS order_id,
    NULLIF(TRIM(customer_id), '') AS customer_id,
    NULLIF(TRIM(order_status), '') AS order_status,
    NULLIF(TRIM(order_purchase_timestamp), '')::TIMESTAMP
        AS order_purchase_timestamp,
    NULLIF(TRIM(order_approved_at), '')::TIMESTAMP
        AS order_approved_at,
    NULLIF(TRIM(order_delivered_carrier_date), '')::TIMESTAMP
        AS order_delivered_carrier_date,
    NULLIF(TRIM(order_delivered_customer_date), '')::TIMESTAMP
        AS order_delivered_customer_date,
    NULLIF(TRIM(order_estimated_delivery_date), '')::TIMESTAMP
        AS order_estimated_delivery_date
FROM raw.orders;

CREATE TABLE IF NOT EXISTS staging.order_items AS
SELECT
    NULLIF(TRIM(order_id), '') AS order_id,
    NULLIF(TRIM(order_item_id), '')::INTEGER AS order_item_id,
    NULLIF(TRIM(product_id), '') AS product_id,
    NULLIF(TRIM(seller_id), '') AS seller_id,
    NULLIF(TRIM(shipping_limit_date), '')::TIMESTAMP
        AS shipping_limit_date,
    NULLIF(TRIM(price), '')::NUMERIC(12,2) AS price,
    NULLIF(TRIM(freight_value), '')::NUMERIC(12,2) AS freight_value
FROM raw.order_items;

CREATE TABLE IF NOT EXISTS staging.payments AS
SELECT
    NULLIF(TRIM(order_id), '') AS order_id,
    NULLIF(TRIM(payment_sequential), '')::INTEGER
        AS payment_sequential,
    NULLIF(TRIM(payment_type), '') AS payment_type,
    NULLIF(TRIM(payment_installments), '')::INTEGER
        AS payment_installments,
    NULLIF(TRIM(payment_value), '')::NUMERIC(12,2) AS payment_value
FROM raw.payments;

CREATE TABLE IF NOT EXISTS staging.customers AS
SELECT
    NULLIF(TRIM(customer_id), '') AS customer_id,
    NULLIF(TRIM(customer_unique_id), '') AS customer_unique_id,
    NULLIF(TRIM(customer_zip_code_prefix), '') AS customer_zip_code_prefix,
    NULLIF(TRIM(customer_city), '') AS customer_city,
    NULLIF(TRIM(customer_state), '') AS customer_state
FROM raw.customers;

CREATE TABLE IF NOT EXISTS staging.products AS
SELECT
    NULLIF(TRIM(product_id), '') AS product_id,
    NULLIF(TRIM(product_category_name), '') AS product_category_name,
    NULLIF(TRIM(product_name_lenght), '')::INTEGER
        AS product_name_length,
    NULLIF(TRIM(product_description_lenght), '')::INTEGER
        AS product_description_length,
    NULLIF(TRIM(product_photos_qty), '')::INTEGER AS product_photos_qty,
    NULLIF(TRIM(product_weight_g), '')::NUMERIC(12,2) AS product_weight_g,
    NULLIF(TRIM(product_length_cm), '')::NUMERIC(12,2) AS product_length_cm,
    NULLIF(TRIM(product_height_cm), '')::NUMERIC(12,2) AS product_height_cm,
    NULLIF(TRIM(product_width_cm), '')::NUMERIC(12,2) AS product_width_cm
FROM raw.products;
