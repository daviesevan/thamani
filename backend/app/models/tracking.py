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

    def to_dict(self):
        """Convert wishlist to dictionary"""
        return {
            'wishlist_id': self.wishlist_id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items_count': len(self.items) if self.items else 0
        }


class WishlistItem(db.Model):
    __tablename__ = 'wishlist_items'

    wishlist_item_id = Column(Integer, primary_key=True, autoincrement=True)
    wishlist_id = Column(Integer, ForeignKey('user_wishlists.wishlist_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    added_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    target_price = Column(Numeric(10, 2))
    notes = Column(Text)  # User notes about the wishlist item
    priority = Column(String(10), default='medium')  # low, medium, high

    # Price tracking when added to wishlist (for scraped products)
    price_when_added = Column(Numeric(10, 2))
    currency_code = Column(String(3), default='KES')

    # Source tracking (to know if it came from scraped data)
    source = Column(String(20), default='database')  # 'database' or 'web_scraping'
    original_scraped_id = Column(String(100))  # Original scraped product ID if applicable

    # Relationships
    wishlist = relationship("UserWishlist", back_populates="items")
    product = relationship("Product", back_populates="wishlist_items")

    # Unique constraint
    __table_args__ = (UniqueConstraint('wishlist_id', 'product_id'),)

    def to_dict(self):
        """Convert wishlist item to dictionary"""
        return {
            'wishlist_item_id': self.wishlist_item_id,
            'wishlist_id': self.wishlist_id,
            'product_id': self.product_id,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'target_price': float(self.target_price) if self.target_price else None,
            'notes': self.notes,
            'priority': self.priority,
            'price_when_added': float(self.price_when_added) if self.price_when_added else None,
            'currency_code': self.currency_code,
            'source': self.source,
            'original_scraped_id': self.original_scraped_id
        }


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