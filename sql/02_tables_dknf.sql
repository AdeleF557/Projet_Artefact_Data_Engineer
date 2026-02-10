
---------- Tables de référence ---------


-- Table clients
CREATE TABLE IF NOT EXISTS ecommerce.customers (
    customer_id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    gender VARCHAR(10) NOT NULL,
    age_range VARCHAR(20) NOT NULL,
    country VARCHAR(50) NOT NULL,
    signup_date DATE NOT NULL CHECK (signup_date <= CURRENT_DATE)
);


-- Table produits
CREATE TABLE IF NOT EXISTS ecommerce.products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    color VARCHAR(50) NOT NULL,
    size VARCHAR(20) NOT NULL,
    catalog_price NUMERIC(10,2) NOT NULL CHECK (catalog_price > 0),
    cost_price NUMERIC(10,2) NOT NULL CHECK (cost_price >= 0)
);


-- Table canaux
CREATE TABLE IF NOT EXISTS ecommerce.channels (
    channel_id SERIAL PRIMARY KEY,
    channel_name VARCHAR(100) NOT NULL UNIQUE
);


-- Table campagnes
CREATE TABLE IF NOT EXISTS ecommerce.campaigns (
    campaign_id SERIAL PRIMARY KEY,
    campaign_name VARCHAR(100)
);

------------Tables transactionnelles ----------------


-- Table ventes
CREATE TABLE IF NOT EXISTS ecommerce.sales (
    sale_id SERIAL PRIMARY KEY,
    sale_date DATE NOT NULL CHECK (sale_date <= CURRENT_DATE),
    customer_id INT NOT NULL,
    channel_id INT NOT NULL,
    campaign_id INT,

    CONSTRAINT fk_sales_customer
        FOREIGN KEY (customer_id)
        REFERENCES ecommerce.customers(customer_id),

    CONSTRAINT fk_sales_channel
        FOREIGN KEY (channel_id)
        REFERENCES ecommerce.channels(channel_id),

    CONSTRAINT fk_sales_campaign
        FOREIGN KEY (campaign_id)
        REFERENCES ecommerce.campaigns(campaign_id)
);


-- Table lignes de vente
CREATE TABLE IF NOT EXISTS ecommerce.sale_items (
    item_id SERIAL PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price > 0),
    discount_percent NUMERIC(5,2) CHECK (discount_percent BETWEEN 0 AND 100),

    CONSTRAINT fk_items_sale
        FOREIGN KEY (sale_id)
        REFERENCES ecommerce.sales(sale_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_items_product
        FOREIGN KEY (product_id)
        REFERENCES ecommerce.products(product_id)
);

