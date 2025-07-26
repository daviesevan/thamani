from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from app.extensions.extensions import db


class UserTrackedProduct(db.Model):
    __tablename__ = 'user_tracked_products'
    
    tracking_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    added_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    target_price = Column(Numeric(10, 2))
    notes = Column(Text)
    is_archived = Column(Boolean, default=False)
    tracking_status = Column(String(20), default='active')
    last_notification_sent = Column(DateTime(timezone=True))
    alert_threshold_percent = Column(Numeric(5, 2), default=10.00)
    
    # Relationships
    user = relationship("User", back_populates="tracked_products")
    product = relationship("Product", back_populates="tracked_products")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'product_id'),)


class UserWishlist(db.Model):
    __tablename__ = 'user_wishlists'
    
    wishlist_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="wishlists")
    items = relationship("WishlistItem", back_populates="wishlist", cascade="all, delete-orphan")


class WishlistItem(db.Model):
    __tablename__ = 'wishlist_items'
    
    wishlist_item_id = Column(Integer, primary_key=True, autoincrement=True)
    wishlist_id = Column(Integer, ForeignKey('user_wishlists.wishlist_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    added_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    target_price = Column(Numeric(10, 2))
    
    # Relationships
    wishlist = relationship("UserWishlist", back_populates="items")
    product = relationship("Product", back_populates="wishlist_items")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('wishlist_id', 'product_id'),)


class PriceAlert(db.Model):
    __tablename__ = 'price_alerts'
    
    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    product_retailer_id = Column(Integer, ForeignKey('product_retailers.product_retailer_id'), nullable=False)
    price_threshold = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_triggered = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    product_retailer = relationship("ProductRetailer", back_populates="alerts")


class UserNotification(db.Model):
    __tablename__ = 'user_notifications'
    
    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    notification_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    related_product_id = Column(Integer, ForeignKey('products.product_id'))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    read_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    product = relationship("Product", back_populates="notifications") 