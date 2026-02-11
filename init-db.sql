-- Initial database setup script
-- This will be executed when PostgreSQL container starts for the first time

-- Create database (already created by POSTGRES_DB env var, but keeping for reference)
-- CREATE DATABASE talentree ENCODING 'UTF8' LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8';

-- Connect to database
\c talentree;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(20) PRIMARY KEY,
    user_type VARCHAR(10) NOT NULL CHECK (user_type IN ('owner', 'customer')),
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    governorate VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE
);

-- Create brands table
CREATE TABLE IF NOT EXISTS brands (
    brand_id VARCHAR(20) PRIMARY KEY,
    owner_user_id VARCHAR(20) NOT NULL,
    business_name VARCHAR(100) NOT NULL,
    business_name_ar VARCHAR(100),
    category VARCHAR(50) NOT NULL CHECK (category IN (
        'Fashion & Accessories',
        'Handmade & Crafts',
        'Natural & Beauty'
    )),
    bio TEXT,
    verified BOOLEAN DEFAULT FALSE,
    profile_complete BOOLEAN DEFAULT FALSE,
    total_sales_egp DECIMAL(12, 2) DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    avg_rating DECIMAL(3, 2) DEFAULT 0,
    rating_count INTEGER DEFAULT 0,
    risk_score DECIMAL(3, 2) DEFAULT 0,
    risk_level VARCHAR(10) CHECK (risk_level IN ('low', 'medium', 'high')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_brand_owner FOREIGN KEY (owner_user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    brand_id VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200),
    description TEXT,
    category VARCHAR(50) NOT NULL,
    price_egp DECIMAL(10, 2) NOT NULL CHECK (price_egp > 0),
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'approved', 'rejected'
    )),
    views INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    sales_count INTEGER DEFAULT 0,
    quality_score DECIMAL(3, 2) DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_brand FOREIGN KEY (brand_id) 
        REFERENCES brands(brand_id) ON DELETE CASCADE
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(20) PRIMARY KEY,
    customer_user_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    brand_id VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_egp DECIMAL(10, 2) NOT NULL,
    total_price_egp DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'processing', 'completed', 'cancelled'
    )),
    shipping_governorate VARCHAR(50) NOT NULL,
    shipping_address TEXT,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    delivery_date TIMESTAMP,
    cancelled_at TIMESTAMP,
    fraud_score DECIMAL(3, 2) DEFAULT 0,
    is_suspicious BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_order_customer FOREIGN KEY (customer_user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_order_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) ON DELETE RESTRICT,
    CONSTRAINT fk_order_brand FOREIGN KEY (brand_id) 
        REFERENCES brands(brand_id) ON DELETE RESTRICT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_brands_owner ON brands(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_brands_category ON brands(category);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand_id);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_user_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date DESC);

-- Print success message
DO $$
BEGIN
    RAISE NOTICE 'TalentTree database initialized successfully!';
    RAISE NOTICE 'Tables created: users, brands, products, orders';
    RAISE NOTICE 'Indexes created for performance optimization';
END $$;
