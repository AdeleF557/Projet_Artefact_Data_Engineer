-- MODÉLISATION EN ÉTOILE

-- 1. TABLE DE FAITS
CREATE OR REPLACE VIEW ecommerce.fact_sales_star AS
SELECT
    si.item_id,
    si.sale_id,
    s.customer_id,
    si.product_id,
    s.channel_id,
    s.campaign_id,
    s.sale_date,

    si.quantity,
    si.unit_price,
    si.discount_percent,

    si.quantity * si.unit_price * (1 - COALESCE(si.discount_percent, 0)/100) AS net_amount,
    CASE WHEN COALESCE(si.discount_percent,0) > 0 THEN TRUE ELSE FALSE END AS has_discount
FROM ecommerce.sale_items si
JOIN ecommerce.sales s ON si.sale_id = s.sale_id;


-- 2. DIMENSIONS

-- DIMENSION CLIENT
CREATE OR REPLACE VIEW ecommerce.dim_customer_star AS
SELECT
    customer_id,
    email,
    gender,
    age_range,
    country
FROM ecommerce.customers;


-- DIMENSION PRODUIT
CREATE OR REPLACE VIEW ecommerce.dim_product_star AS
SELECT
    product_id,
    product_name,
    category,
    brand,
    color,
    size
FROM ecommerce.products;


-- DIMENSION CANAL
CREATE OR REPLACE VIEW ecommerce.dim_channel_star AS
SELECT
    channel_id,
    channel_name
FROM ecommerce.channels;


-- DIMENSION CAMPAGNE
CREATE OR REPLACE VIEW ecommerce.dim_campaign_star AS
SELECT
    campaign_id,
    campaign_name
FROM ecommerce.campaigns;


-- DIMENSION DATE
CREATE OR REPLACE VIEW ecommerce.dim_date_star AS
SELECT
    sale_date AS date_value,
    EXTRACT(YEAR FROM sale_date) AS year,
    EXTRACT(MONTH FROM sale_date) AS month,
    EXTRACT(DAY FROM sale_date) AS day,
    EXTRACT(DOW FROM sale_date) AS day_of_week,
    TO_CHAR(sale_date, 'Month') AS month_name,
    TO_CHAR(sale_date, 'Day') AS day_name,
    EXTRACT(QUARTER FROM sale_date) AS quarter,
    CASE WHEN EXTRACT(DOW FROM sale_date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
FROM ecommerce.sales;
