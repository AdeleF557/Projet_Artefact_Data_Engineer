\echo 'Application des contraintes et index'

-- 1️.CONTRAINTES MÉTIER 

ALTER TABLE ecommerce.customers
    ADD CONSTRAINT chk_customers_gender 
    CHECK (gender IN ('Male', 'Female', 'Other'));

ALTER TABLE ecommerce.customers
    ADD CONSTRAINT chk_customers_age_range 
    CHECK (age_range IN ('16-25','26-35','36-45','46-55','56+'));

ALTER TABLE ecommerce.products
    ADD CONSTRAINT chk_products_catalog_price 
    CHECK (catalog_price >= 0);

ALTER TABLE ecommerce.products
    ADD CONSTRAINT chk_products_cost_price 
    CHECK (cost_price >= 0);

ALTER TABLE ecommerce.sales
    ADD CONSTRAINT chk_sales_sale_date 
    CHECK (sale_date <= CURRENT_DATE);

ALTER TABLE ecommerce.sale_items
    ADD CONSTRAINT chk_sale_items_quantity 
    CHECK (quantity > 0);

ALTER TABLE ecommerce.sale_items
    ADD CONSTRAINT chk_sale_items_unit_price 
    CHECK (unit_price >= 0);

ALTER TABLE ecommerce.sale_items
    ADD CONSTRAINT chk_sale_items_discount_percent 
    CHECK (discount_percent BETWEEN 0 AND 100);

ALTER TABLE ecommerce.sale_items
    ADD CONSTRAINT chk_sale_items_total_price_positive 
    CHECK (quantity * unit_price * (1 - discount_percent/100) >= 0);

-- 2️. INDEX POUR OPTIMISATION

-- Index sur les clés étrangères
CREATE INDEX IF NOT EXISTS idx_sales_customer_id 
    ON ecommerce.sales(customer_id);

CREATE INDEX IF NOT EXISTS idx_sales_channel_id 
    ON ecommerce.sales(channel_id);

CREATE INDEX IF NOT EXISTS idx_sales_campaign_id 
    ON ecommerce.sales(campaign_id);

CREATE INDEX IF NOT EXISTS idx_sale_items_sale_id 
    ON ecommerce.sale_items(sale_id);

CREATE INDEX IF NOT EXISTS idx_sale_items_product_id 
    ON ecommerce.sale_items(product_id);

-- Index sur la date pour analyses temporelles
CREATE INDEX IF NOT EXISTS idx_sales_sale_date 
    ON ecommerce.sales(sale_date);

-- Index composite pour jointures
CREATE INDEX IF NOT EXISTS idx_sale_items_sale_product 
    ON ecommerce.sale_items(sale_id, product_id);

-- 3️. CONTRAINTES D'UNICITÉ

ALTER TABLE ecommerce.sale_items
    ADD CONSTRAINT uq_sale_items_sale_product 
    UNIQUE (sale_id, product_id);

\echo 'Contraintes et index appliqués avec succès'