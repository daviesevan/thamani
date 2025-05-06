-- Enable UUID extension for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Core User Tables
CREATE TABLE users (
user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
email VARCHAR(255) UNIQUE NOT NULL,
password_hash VARCHAR(255) NOT NULL,
username VARCHAR(50) UNIQUE,
full_name VARCHAR(255),
created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
last_login_at TIMESTAMP WITH TIME ZONE,
account_status VARCHAR(20) NOT NULL DEFAULT 'active',
profile_image_url VARCHAR(255),
email_verified BOOLEAN DEFAULT FALSE
);

CREATE TABLE user_sessions (
session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID REFERENCES users(user_id) NOT NULL,
token VARCHAR(255) NOT NULL,
device_info JSONB,
ip_address VARCHAR(45),
created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
last_active_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_preferences (
preference_id SERIAL PRIMARY KEY,
user_id UUID REFERENCES users(user_id) NOT NULL UNIQUE,
currency VARCHAR(3) DEFAULT 'KES',
language VARCHAR(10) DEFAULT 'en',
theme VARCHAR(20) DEFAULT 'light',
notification_email BOOLEAN DEFAULT TRUE,
notification_push BOOLEAN DEFAULT TRUE,
onboarding_completed BOOLEAN DEFAULT FALSE,
created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Product and Price Related Tables
CREATE TABLE categories (
category_id SERIAL PRIMARY KEY,
name VARCHAR(100) NOT NULL,
parent_category_id INTEGER REFERENCES categories(category_id),
image_url VARCHAR(255),
created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE retailers (
retailer_id SERIAL PRIMARY KEY,
name VARCHAR(100) NOT NULL,
website_url VARCHAR(255) NOT NULL,
logo_url VARCHAR(255),
country_code VARCHAR(2) DEFAULT 'KE',
created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE products (
product_id SERIAL PRIMARY KEY,
name VARCHAR(255) NOT NULL,
description TEXT,
category_id INTEGER REFERENCES categories(category_id) NOT NULL,
brand VARCHAR(100),
model VARCHAR(100),
image_url VARCHAR(255),
specifications JSONB,
created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product_retailers (
product_retailer_id SERIAL PRIMARY KEY,
product_id INTEGER REFERENCES products(product_id) NOT NULL,
retailer_id INTEGER REFERENCES retailers(retailer_id) NOT NULL,
retailer_product_url VARCHAR(512) NOT NULL,
retailer_product_id VARCHAR(100),
current_price DECIMAL(10,2) NOT NULL,
currency_code VARCHAR(3) DEFAULT 'KES',
last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
in_stock BOOLEAN DEFAULT TRUE,
UNIQUE(product_id, retailer_id)
);

CREATE TABLE price_history (
price_history_id SERIAL PRIMARY KEY,
product_retailer_id INTEGER REFERENCES product_retailers(product_retailer_id) NOT NULL,
price DECIMAL(10,2) NOT NULL,
currency_code VARCHAR(3) DEFAULT 'KES',
timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
is_on_sale BOOLEAN DEFAULT FALSE,
original_price DECIMAL(10,2)
);

-- User Tracking and Alerts
CREATE TABLE user_tracked_products (
tracking_id SERIAL PRIMARY KEY,
user_id UUID REFERENCES users(user_id) NOT NULL,
product_id INTEGER REFERENCES products(product_id) NOT NULL,
added_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
target_price DECIMAL(10,2),
notes TEXT,
is_archived BOOLEAN DEFAULT FALSE,
tracking_status VARCHAR(20) DEFAULT 'active',
last_notification_sent TIMESTAMP WITH TIME ZONE,
alert_threshold_percent DECIMAL(5,2) DEFAULT 10.00,
UNIQUE(user_id, product_id)
);

CREATE TABLE user_wishlists (
wishlist_id SERIAL PRIMARY KEY,
user_id UUID REFERENCES users(user_id) NOT NULL,
name VARCHAR(100) NOT NULL,
description TEXT,
is_default BOOLEAN DEFAULT FALSE,
created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE wishlist_items (
wishlist_item_id SERIAL PRIMARY KEY,
wishlist_id INTEGER REFERENCES user_wishlists(wishlist_id) NOT NULL,
product_id INTEGER REFERENCES products(product_id) NOT NULL,
added_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
target_price DECIMAL(10,2),
UNIQUE(wishlist_id, product_id)
);

CREATE TABLE price_alerts (
alert_id SERIAL PRIMARY KEY,
user_id UUID REFERENCES users(user_id) NOT NULL,
product_retailer_id INTEGER REFERENCES product_retailers(product_retailer_id) NOT NULL,
price_threshold DECIMAL(10,2) NOT NULL,
is_active BOOLEAN DEFAULT TRUE,
created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
last_triggered TIMESTAMP WITH TIME ZONE
);

CREATE TABLE user_notifications (
notification_id SERIAL PRIMARY KEY,
user_id UUID REFERENCES users(user_id) NOT NULL,
notification_type VARCHAR(50) NOT NULL,
title VARCHAR(255) NOT NULL,
message TEXT NOT NULL,
related_product_id INTEGER REFERENCES products(product_id),
is_read BOOLEAN DEFAULT FALSE,
created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
read_at TIMESTAMP WITH TIME ZONE
);

-- Essential Indices for Performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_user_sessions_token ON user_sessions(token);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_product_retailers_product ON product_retailers(product_id);
CREATE INDEX idx_product_retailers_retailer ON product_retailers(retailer_id);
CREATE INDEX idx_price_history_product_retailer ON price_history(product_retailer_id);
CREATE INDEX idx_tracked_products_user_id ON user_tracked_products(user_id);
CREATE INDEX idx_tracked_products_product_id ON user_tracked_products(product_id);
CREATE INDEX idx_wishlists_user_id ON user_wishlists(user_id);
CREATE INDEX idx_wishlist_items_wishlist_id ON wishlist_items(wishlist_id);
CREATE INDEX idx_notifications_user_id ON user_notifications(user_id);
CREATE INDEX idx_notifications_read ON user_notifications(is_read);
