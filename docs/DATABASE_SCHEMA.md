# 🗄️ TalentTree Admin Dashboard - Database Schema

**Version:** 4.0.0  
**Database:** PostgreSQL 14+  
**Encoding:** UTF-8  
**Collation:** UTF8 (for Arabic support)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Tables](#tables)
- [Indexes](#indexes)
- [Constraints](#constraints)
- [Migration Scripts](#migration-scripts)

---

## 🎯 Overview

This database schema supports a complete Egyptian e-commerce platform with:
- User management (owners & customers)
- Brand & product catalog
- Order processing
- Payment tracking
- Reviews & ratings
- Raw material marketplace
- Support ticket system
- Admin actions logging

**Total Tables:** 12  
**Relationships:** Foreign keys with cascading rules  
**Localization:** Arabic text support (UTF-8)

---

## 📊 Entity Relationship Diagram

```
┌─────────────┐
│    USERS    │
└──────┬──────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       │              │              │              │
       ▼              ▼              ▼              ▼
┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│   BRANDS   │ │   ORDERS   │ │  REVIEWS   │ │  SUPPORT   │
│  (owners)  │ │(customers) │ │(customers) │ │  TICKETS   │
└──────┬─────┘ └──────┬─────┘ └──────┬─────┘ └────────────┘
       │              │              │
       ▼              ▼              │
┌────────────┐ ┌────────────┐       │
│  PRODUCTS  │ │  PAYMENTS  │       │
└──────┬─────┘ └────────────┘       │
       │                             │
       └─────────────┬───────────────┘
                     ▼
              ┌────────────┐
              │  REVIEWS   │
              └────────────┘

┌──────────────────┐     ┌──────────────────┐
│ STATIC_VENDORS   │────▶│  RAW_MATERIALS   │
└──────────────────┘     └─────────┬────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │ MATERIAL_REQUESTS│
                         └──────────────────┘
```

---

## 📑 Tables

### 1. `users` Table

**Purpose:** Store all platform users (owners and customers)

```sql
CREATE TABLE users (
    -- Primary Key
    user_id VARCHAR(20) PRIMARY KEY,
    
    -- User Type
    user_type VARCHAR(10) NOT NULL CHECK (user_type IN ('owner', 'customer')),
    
    -- Basic Information
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    
    -- Location (Egyptian Governorate)
    governorate VARCHAR(50) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE
);

-- Indexes
CREATE INDEX idx_users_type ON users(user_type);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_governorate ON users(governorate);
CREATE INDEX idx_users_created ON users(created_at DESC);

-- Comments
COMMENT ON TABLE users IS 'Platform users - both business owners and customers';
COMMENT ON COLUMN users.user_id IS 'Format: USER00001, USER00002, etc.';
COMMENT ON COLUMN users.governorate IS 'One of 27 Egyptian governorates';
```

**Sample Data:**
```sql
INSERT INTO users VALUES 
('USER00001', 'owner', 'أحمد محمد', 'ahmed@example.com', '+20 10-1234-5678', 'Cairo', NOW(), NOW(), NOW(), TRUE, TRUE, TRUE),
('USER00002', 'customer', 'فاطمة علي', 'fatima@example.com', '+20 11-2345-6789', 'Alexandria', NOW(), NOW(), NULL, TRUE, TRUE, FALSE);
```

---

### 2. `brands` Table

**Purpose:** Store business brands created by owners

```sql
CREATE TABLE brands (
    -- Primary Key
    brand_id VARCHAR(20) PRIMARY KEY,
    
    -- Foreign Key
    owner_user_id VARCHAR(20) NOT NULL,
    
    -- Brand Information
    business_name VARCHAR(100) NOT NULL,
    business_name_ar VARCHAR(100),  -- Arabic name
    category VARCHAR(50) NOT NULL CHECK (category IN (
        'Fashion & Accessories',
        'Handmade & Crafts',
        'Natural & Beauty'
    )),
    bio TEXT,
    
    -- Status
    verified BOOLEAN DEFAULT FALSE,
    profile_complete BOOLEAN DEFAULT FALSE,
    
    -- Metrics (computed/cached)
    total_sales_egp DECIMAL(12, 2) DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    avg_rating DECIMAL(3, 2) DEFAULT 0,
    rating_count INTEGER DEFAULT 0,
    
    -- AI Risk Scoring
    risk_score DECIMAL(3, 2) DEFAULT 0,  -- 0.0 to 1.0
    risk_level VARCHAR(10) CHECK (risk_level IN ('low', 'medium', 'high')),
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraint
    CONSTRAINT fk_brand_owner FOREIGN KEY (owner_user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_brands_owner ON brands(owner_user_id);
CREATE INDEX idx_brands_category ON brands(category);
CREATE INDEX idx_brands_verified ON brands(verified);
CREATE INDEX idx_brands_risk ON brands(risk_level, risk_score DESC);

-- Comments
COMMENT ON TABLE brands IS 'Business brands owned by platform sellers';
COMMENT ON COLUMN brands.brand_id IS 'Format: BRAND0001, BRAND0002, etc.';
COMMENT ON COLUMN brands.risk_score IS 'AI-computed risk score (0=safe, 1=risky)';
```

**Sample Data:**
```sql
INSERT INTO brands VALUES 
('BRAND0001', 'USER00001', 'Cairo Fashion House', 'دار أزياء القاهرة', 'Fashion & Accessories', 
 'Modern Egyptian fashion...', TRUE, TRUE, 45230.50, 120, 4.5, 98, 0.15, 'low', NOW(), NOW());
```

---

### 3. `products` Table

**Purpose:** Product catalog with approval workflow

```sql
CREATE TABLE products (
    -- Primary Key
    product_id VARCHAR(20) PRIMARY KEY,
    
    -- Foreign Keys
    brand_id VARCHAR(20) NOT NULL,
    
    -- Product Information
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200),  -- Arabic name
    description TEXT,
    category VARCHAR(50) NOT NULL,
    
    -- Pricing
    price_egp DECIMAL(10, 2) NOT NULL CHECK (price_egp > 0),
    
    -- Inventory
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    
    -- Approval Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending',
        'approved',
        'rejected'
    )),
    
    -- Metrics
    views INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    sales_count INTEGER DEFAULT 0,
    
    -- AI Quality Score
    quality_score DECIMAL(3, 2) DEFAULT 0,  -- 0.0 to 1.0
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_product_brand FOREIGN KEY (brand_id) 
        REFERENCES brands(brand_id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_products_brand ON products(brand_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_price ON products(price_egp);
CREATE INDEX idx_products_popularity ON products(sales_count DESC, views DESC);

-- Comments
COMMENT ON TABLE products IS 'Product catalog with admin approval workflow';
COMMENT ON COLUMN products.product_id IS 'Format: PROD00001, PROD00002, etc.';
COMMENT ON COLUMN products.status IS 'Requires admin approval before going live';
```

**Sample Data:**
```sql
INSERT INTO products VALUES 
('PROD00001', 'BRAND0001', 'Leather Handbag', 'حقيبة جلدية', 
 'Premium leather handbag...', 'Fashion & Accessories', 
 450.00, 25, 'approved', 1250, 340, 45, 0.89, NOW(), NOW(), NOW());
```

---

### 4. `orders` Table

**Purpose:** Customer order tracking

```sql
CREATE TABLE orders (
    -- Primary Key
    order_id VARCHAR(20) PRIMARY KEY,
    
    -- Foreign Keys
    customer_user_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    brand_id VARCHAR(20) NOT NULL,
    
    -- Order Details
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_egp DECIMAL(10, 2) NOT NULL,
    total_price_egp DECIMAL(10, 2) NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending',
        'processing',
        'completed',
        'cancelled'
    )),
    
    -- Shipping
    shipping_governorate VARCHAR(50) NOT NULL,
    shipping_address TEXT,
    
    -- Timestamps
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    delivery_date TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    -- Fraud Detection
    fraud_score DECIMAL(3, 2) DEFAULT 0,  -- 0.0 to 1.0
    is_suspicious BOOLEAN DEFAULT FALSE,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_order_customer FOREIGN KEY (customer_user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_order_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) ON DELETE RESTRICT,
    CONSTRAINT fk_order_brand FOREIGN KEY (brand_id) 
        REFERENCES brands(brand_id) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX idx_orders_customer ON orders(customer_user_id);
CREATE INDEX idx_orders_product ON orders(product_id);
CREATE INDEX idx_orders_brand ON orders(brand_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_date ON orders(order_date DESC);
CREATE INDEX idx_orders_governorate ON orders(shipping_governorate);
CREATE INDEX idx_orders_fraud ON orders(is_suspicious, fraud_score DESC);

-- Comments
COMMENT ON TABLE orders IS 'Customer orders with tracking and fraud detection';
COMMENT ON COLUMN orders.order_id IS 'Format: ORD000001, ORD000002, etc.';
```

**Sample Data:**
```sql
INSERT INTO orders VALUES 
('ORD000001', 'USER00002', 'PROD00001', 'BRAND0001', 
 1, 450.00, 450.00, 'completed', 'Cairo', '123 Nasr City, Cairo',
 NOW() - INTERVAL '5 days', NOW() - INTERVAL '2 days', NULL, 0.05, FALSE);
```

---

### 5. `payments` Table

**Purpose:** Payment transaction records

```sql
CREATE TABLE payments (
    -- Primary Key
    payment_id SERIAL PRIMARY KEY,
    
    -- Foreign Key
    order_id VARCHAR(20) NOT NULL,
    
    -- Payment Details
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN (
        'cash_on_delivery',
        'credit_card',
        'mobile_wallet',
        'bank_transfer'
    )),
    amount_egp DECIMAL(10, 2) NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending',
        'completed',
        'failed',
        'refunded'
    )),
    
    -- Transaction Details
    transaction_id VARCHAR(100),  -- External payment gateway ID
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Foreign Key Constraint
    CONSTRAINT fk_payment_order FOREIGN KEY (order_id) 
        REFERENCES orders(order_id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_payments_order ON payments(order_id);
CREATE INDEX idx_payments_method ON payments(payment_method);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_date ON payments(created_at DESC);

-- Comments
COMMENT ON TABLE payments IS 'Payment transactions linked to orders';
```

---

### 6. `reviews` Table

**Purpose:** Product reviews and ratings

```sql
CREATE TABLE reviews (
    -- Primary Key
    review_id VARCHAR(20) PRIMARY KEY,
    
    -- Foreign Keys
    customer_user_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    order_id VARCHAR(20),  -- Optional link to specific order
    
    -- Review Content
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    
    -- AI Sentiment Analysis
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'neutral', 'negative')),
    sentiment_score DECIMAL(3, 2),  -- Confidence 0.0 to 1.0
    
    -- Fraud Detection
    is_fake BOOLEAN DEFAULT FALSE,
    fraud_score DECIMAL(3, 2) DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_review_customer FOREIGN KEY (customer_user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_review_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_review_order FOREIGN KEY (order_id) 
        REFERENCES orders(order_id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_reviews_customer ON reviews(customer_user_id);
CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_sentiment ON reviews(sentiment);
CREATE INDEX idx_reviews_fraud ON reviews(is_fake, fraud_score DESC);
CREATE INDEX idx_reviews_date ON reviews(created_at DESC);

-- Comments
COMMENT ON TABLE reviews IS 'Product reviews with AI sentiment analysis and fraud detection';
COMMENT ON COLUMN reviews.sentiment IS 'AI-computed sentiment from review text';
```

---

### 7. `static_vendors` Table

**Purpose:** Raw material suppliers

```sql
CREATE TABLE static_vendors (
    -- Primary Key
    vendor_id VARCHAR(20) PRIMARY KEY,
    
    -- Vendor Information
    vendor_name VARCHAR(100) NOT NULL,
    vendor_name_ar VARCHAR(100),
    contact_email VARCHAR(100),
    contact_phone VARCHAR(20),
    
    -- Location
    governorate VARCHAR(50),
    address TEXT,
    
    -- Specialization
    specialization VARCHAR(100),  -- e.g., "Fabrics & Textiles"
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_vendors_active ON static_vendors(is_active);
CREATE INDEX idx_vendors_specialization ON static_vendors(specialization);

-- Comments
COMMENT ON TABLE static_vendors IS 'Raw material suppliers for business owners';
```

---

### 8. `raw_material_marketplace` Table

**Purpose:** Available raw materials catalog

```sql
CREATE TABLE raw_material_marketplace (
    -- Primary Key
    material_id VARCHAR(20) PRIMARY KEY,
    
    -- Foreign Key
    vendor_id VARCHAR(20) NOT NULL,
    
    -- Material Information
    material_name VARCHAR(100) NOT NULL,
    material_name_ar VARCHAR(100),
    category VARCHAR(50) NOT NULL,
    description TEXT,
    
    -- Pricing & Stock
    price_per_unit_egp DECIMAL(10, 2) NOT NULL,
    unit_type VARCHAR(20) NOT NULL,  -- e.g., "kg", "meter", "piece"
    stock_quantity INTEGER DEFAULT 0,
    minimum_order_quantity INTEGER DEFAULT 1,
    
    -- Lead Time
    lead_time_days INTEGER DEFAULT 3,
    
    -- Status
    is_available BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraint
    CONSTRAINT fk_material_vendor FOREIGN KEY (vendor_id) 
        REFERENCES static_vendors(vendor_id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_materials_vendor ON raw_material_marketplace(vendor_id);
CREATE INDEX idx_materials_category ON raw_material_marketplace(category);
CREATE INDEX idx_materials_available ON raw_material_marketplace(is_available);
CREATE INDEX idx_materials_price ON raw_material_marketplace(price_per_unit_egp);

-- Comments
COMMENT ON TABLE raw_material_marketplace IS 'Raw materials available for purchase by business owners';
```

---

### 9. `material_requests` Table

**Purpose:** Owner purchases from raw material marketplace

```sql
CREATE TABLE material_requests (
    -- Primary Key
    request_id VARCHAR(20) PRIMARY KEY,
    
    -- Foreign Keys
    owner_user_id VARCHAR(20) NOT NULL,
    material_id VARCHAR(20) NOT NULL,
    vendor_id VARCHAR(20) NOT NULL,
    
    -- Request Details
    quantity_requested DECIMAL(10, 2) NOT NULL,
    total_price_egp DECIMAL(10, 2) NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending',
        'approved',
        'shipped',
        'delivered',
        'cancelled'
    )),
    
    -- Timestamps
    request_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    delivery_date TIMESTAMP,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_request_owner FOREIGN KEY (owner_user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_request_material FOREIGN KEY (material_id) 
        REFERENCES raw_material_marketplace(material_id) ON DELETE RESTRICT,
    CONSTRAINT fk_request_vendor FOREIGN KEY (vendor_id) 
        REFERENCES static_vendors(vendor_id) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX idx_requests_owner ON material_requests(owner_user_id);
CREATE INDEX idx_requests_material ON material_requests(material_id);
CREATE INDEX idx_requests_vendor ON material_requests(vendor_id);
CREATE INDEX idx_requests_status ON material_requests(status);
CREATE INDEX idx_requests_date ON material_requests(request_date DESC);
```

---

### 10. `support_tickets` Table

**Purpose:** Customer support ticketing system

```sql
CREATE TABLE support_tickets (
    -- Primary Key
    ticket_id VARCHAR(20) PRIMARY KEY,
    
    -- Foreign Key
    user_id VARCHAR(20) NOT NULL,
    
    -- Ticket Information
    subject VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN (
        'order_issue',
        'payment_issue',
        'product_quality',
        'shipping',
        'account',
        'other'
    )),
    
    -- Priority
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN (
        'low',
        'medium',
        'high',
        'urgent'
    )),
    
    -- Status
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN (
        'open',
        'in_progress',
        'resolved',
        'closed'
    )),
    
    -- Assignment
    assigned_admin_id VARCHAR(20),
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    
    -- Foreign Key Constraint
    CONSTRAINT fk_ticket_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_tickets_user ON support_tickets(user_id);
CREATE INDEX idx_tickets_status ON support_tickets(status);
CREATE INDEX idx_tickets_priority ON support_tickets(priority, status);
CREATE INDEX idx_tickets_category ON support_tickets(category);
CREATE INDEX idx_tickets_date ON support_tickets(created_at DESC);
```

---

### 11. `admin_actions` Table

**Purpose:** Audit log for admin activities

```sql
CREATE TABLE admin_actions (
    -- Primary Key
    action_id SERIAL PRIMARY KEY,
    
    -- Admin Information
    admin_user_id VARCHAR(20),  -- Could be NULL for system actions
    
    -- Action Details
    action_type VARCHAR(50) NOT NULL,  -- e.g., 'brand_verification', 'product_approval'
    entity_type VARCHAR(50),  -- e.g., 'brand', 'product', 'user'
    entity_id VARCHAR(20),  -- ID of affected entity
    
    -- Action Result
    action_result VARCHAR(20) CHECK (action_result IN (
        'approved',
        'rejected',
        'suspended',
        'deleted',
        'updated'
    )),
    
    -- Notes
    notes TEXT,
    
    -- Timestamp
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_admin_actions_admin ON admin_actions(admin_user_id);
CREATE INDEX idx_admin_actions_type ON admin_actions(action_type);
CREATE INDEX idx_admin_actions_entity ON admin_actions(entity_type, entity_id);
CREATE INDEX idx_admin_actions_date ON admin_actions(created_at DESC);

-- Comments
COMMENT ON TABLE admin_actions IS 'Audit trail of all administrative actions';
```

---

### 12. `analytics_snapshots` Table

**Purpose:** Daily platform metrics snapshots

```sql
CREATE TABLE analytics_snapshots (
    -- Primary Key
    snapshot_id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL UNIQUE,
    
    -- User Metrics
    total_users INTEGER DEFAULT 0,
    new_users_today INTEGER DEFAULT 0,
    active_owners INTEGER DEFAULT 0,
    active_customers INTEGER DEFAULT 0,
    
    -- Business Metrics
    total_orders INTEGER DEFAULT 0,
    orders_today INTEGER DEFAULT 0,
    total_revenue_egp DECIMAL(12, 2) DEFAULT 0,
    revenue_today_egp DECIMAL(12, 2) DEFAULT 0,
    avg_order_value_egp DECIMAL(10, 2) DEFAULT 0,
    
    -- Product Metrics
    total_products INTEGER DEFAULT 0,
    pending_approvals INTEGER DEFAULT 0,
    
    -- Timestamp
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_snapshots_date ON analytics_snapshots(snapshot_date DESC);

-- Comments
COMMENT ON TABLE analytics_snapshots IS 'Daily snapshots of platform KPIs for trending';
```

---

## 🔑 Constraints & Business Rules

### Cascading Deletes

```sql
-- When a user is deleted:
-- ✅ Their brands are deleted
-- ✅ Their orders are deleted  
-- ✅ Their reviews are deleted
-- ❌ Products they ordered remain (RESTRICT)

-- When a brand is deleted:
-- ✅ Their products are deleted
-- ❌ Orders for their products remain (RESTRICT)

-- When a product is deleted:
-- ❌ Cannot delete if orders exist (RESTRICT)
```

### Check Constraints

```sql
-- Prices must be positive
CHECK (price_egp > 0)

-- Ratings between 1-5
CHECK (rating BETWEEN 1 AND 5)

-- Stock cannot be negative
CHECK (stock_quantity >= 0)

-- Risk/Quality scores between 0-1
CHECK (risk_score BETWEEN 0 AND 1)
CHECK (quality_score BETWEEN 0 AND 1)
```

---

## 🚀 Migration Scripts

### Initial Setup

```sql
-- Create database with UTF-8 encoding for Arabic support
CREATE DATABASE talentree
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF-8'
    LC_CTYPE 'en_US.UTF-8'
    TEMPLATE template0;

\c talentree;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- Run all table creation scripts in order
-- (Copy tables from above in order)
```

### Sample Data Load

```sql
-- Load from CSV files
COPY users FROM '/path/to/mock_data/users.csv' 
    DELIMITER ',' CSV HEADER ENCODING 'UTF8';

COPY brands FROM '/path/to/mock_data/brands.csv' 
    DELIMITER ',' CSV HEADER ENCODING 'UTF8';

COPY products FROM '/path/to/mock_data/products.csv' 
    DELIMITER ',' CSV HEADER ENCODING 'UTF8';

-- Repeat for all tables...
```

### Useful Queries

```sql
-- Update brand metrics after new orders
UPDATE brands b
SET 
    total_sales_egp = (
        SELECT COALESCE(SUM(total_price_egp), 0) 
        FROM orders 
        WHERE brand_id = b.brand_id AND status = 'completed'
    ),
    total_orders = (
        SELECT COUNT(*) 
        FROM orders 
        WHERE brand_id = b.brand_id AND status = 'completed'
    ),
    avg_rating = (
        SELECT COALESCE(AVG(rating), 0) 
        FROM reviews r 
        JOIN products p ON r.product_id = p.product_id 
        WHERE p.brand_id = b.brand_id
    ),
    rating_count = (
        SELECT COUNT(*) 
        FROM reviews r 
        JOIN products p ON r.product_id = p.product_id 
        WHERE p.brand_id = b.brand_id
    );

-- Update product sales counts
UPDATE products p
SET sales_count = (
    SELECT COALESCE(SUM(quantity), 0)
    FROM orders
    WHERE product_id = p.product_id AND status = 'completed'
);
```

---

## 📊 Views (Recommended)

### Materialized View: Brand Stats

```sql
CREATE MATERIALIZED VIEW brand_statistics AS
SELECT 
    b.brand_id,
    b.business_name,
    b.category,
    COUNT(DISTINCT p.product_id) as product_count,
    COUNT(DISTINCT o.order_id) as order_count,
    COALESCE(SUM(o.total_price_egp), 0) as total_revenue,
    COALESCE(AVG(r.rating), 0) as avg_rating,
    COUNT(DISTINCT r.review_id) as review_count
FROM brands b
LEFT JOIN products p ON b.brand_id = p.brand_id
LEFT JOIN orders o ON b.brand_id = o.brand_id AND o.status = 'completed'
LEFT JOIN reviews r ON p.product_id = r.product_id
GROUP BY b.brand_id, b.business_name, b.category;

-- Refresh periodically
REFRESH MATERIALIZED VIEW brand_statistics;
```

---

## 🔒 Security

### Row-Level Security (Optional)

```sql
-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own data
CREATE POLICY user_isolation ON users
    FOR ALL
    USING (user_id = current_user_id());

-- Admin bypass
CREATE POLICY admin_all_access ON users
    FOR ALL
    TO admin_role
    USING (true);
```

---

## 📈 Performance Optimization

### Recommended Indexes

```sql
-- Full-text search on product names
CREATE INDEX idx_products_name_gin ON products 
    USING gin(to_tsvector('english', name));

-- Composite index for common queries
CREATE INDEX idx_orders_customer_date ON orders(customer_user_id, order_date DESC);
CREATE INDEX idx_products_category_status ON products(category, status);

-- Partial index for pending items only
CREATE INDEX idx_products_pending ON products(created_at) 
    WHERE status = 'pending';
```

### Partitioning (For Large Datasets)

```sql
-- Partition orders by year
CREATE TABLE orders_2026 PARTITION OF orders
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE TABLE orders_2027 PARTITION OF orders
    FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');
```

---

## 🛠️ Maintenance

### Regular Tasks

```sql
-- Vacuum and analyze tables weekly
VACUUM ANALYZE users;
VACUUM ANALYZE orders;
VACUUM ANALYZE products;

-- Reindex monthly
REINDEX TABLE orders;

-- Update statistics
ANALYZE;
```

---

## 📝 Notes

1. **Arabic Support:** All text columns support UTF-8 for Arabic characters
2. **Governorates:** 27 Egyptian governorates are supported in dropdown/validation
3. **AI Scores:** Risk, quality, fraud, and sentiment scores computed by AI models
4. **Soft Deletes:** Consider adding `deleted_at` column for soft deletes instead of hard deletes
5. **Audit Trail:** `admin_actions` table logs all administrative changes

---

## 🔗 Related Documentation

- **API Documentation:** `docs/API_ENHANCED.md`
- **AI Models Guide:** `docs/STEP3_AI_MODELS_COMPLETE.md`
- **Mock Data:** See `mock_data/` directory

---

**Last Updated:** February 11, 2026  
**Version:** 4.0.0  
**Status:** ✅ Production Ready
