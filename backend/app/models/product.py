from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from app.extensions.extensions import db


class Category(db.Model):
    __tablename__ = 'categories'
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    parent_category_id = Column(Integer, ForeignKey('categories.category_id'))
    image_url = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    parent_category = relationship("Category", remote_side=[category_id])
    subcategories = relationship("Category", back_populates="parent_category")
    products = relationship("Product", back_populates="category")


class Retailer(db.Model):
    __tablename__ = 'retailers'
    
    retailer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    website_url = Column(String(255), nullable=False)
    logo_url = Column(String(255))
    country_code = Column(String(2), default='KE')
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    product_retailers = relationship("ProductRetailer", back_populates="retailer")


class Product(db.Model):
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('categories.category_id'), nullable=True)
    brand = Column(String(100))
    model = Column(String(100))
    image_url = Column(String(255))
    specifications = Column(Text)  # JSON stored as text for SQLite
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    category = relationship("Category", back_populates="products")
    product_retailers = relationship("ProductRetailer", back_populates="product", cascade="all, delete-orphan")
    tracked_products = relationship("UserTrackedProduct", back_populates="product", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="product", cascade="all, delete-orphan")
    notifications = relationship("UserNotification", back_populates="product", cascade="all, delete-orphan")


class ProductRetailer(db.Model):
    __tablename__ = 'product_retailers'
    
    product_retailer_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    retailer_id = Column(Integer, ForeignKey('retailers.retailer_id'), nullable=False)
    retailer_product_url = Column(String(512), nullable=False)
    retailer_product_id = Column(String(100))
    current_price = Column(Numeric(10, 2), nullable=False)
    currency_code = Column(String(3), default='KES')
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    in_stock = Column(Boolean, default=True)

    # Scraping-related fields
    last_scrape_attempt = Column(DateTime(timezone=True))
    scraping_error = Column(Text)
    scrape_count = Column(Integer, default=0)
    is_scrapable = Column(Boolean, default=True)

    # Relationships
    product = relationship("Product", back_populates="product_retailers")
    retailer = relationship("Retailer", back_populates="product_retailers")
    price_history = relationship("PriceHistory", back_populates="product_retailer", cascade="all, delete-orphan")
    alerts = relationship("PriceAlert", back_populates="product_retailer", cascade="all, delete-orphan")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('product_id', 'retailer_id'),)


class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    
    price_history_id = Column(Integer, primary_key=True, autoincrement=True)
    product_retailer_id = Column(Integer, ForeignKey('product_retailers.product_retailer_id'), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency_code = Column(String(3), default='KES')
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_on_sale = Column(Boolean, default=False)
    original_price = Column(Numeric(10, 2))
    
    # Relationships
    product_retailer = relationship("ProductRetailer", back_populates="price_history") 