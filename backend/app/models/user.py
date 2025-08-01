import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.extensions.extensions import db


class User(db.Model):
    __tablename__ = 'users'
    
    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(50), unique=True)
    full_name = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime(timezone=True))
    account_status = Column(String(20), default='active')
    profile_image_url = Column(String(255))
    email_verified = Column(Boolean, default=False)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    tracked_products = relationship("UserTrackedProduct", back_populates="user", cascade="all, delete-orphan")
    wishlists = relationship("UserWishlist", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("PriceAlert", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("UserNotification", back_populates="user", cascade="all, delete-orphan")


class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    session_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    token = Column(String(255), nullable=False)
    device_info = Column(Text)  # JSON stored as text for SQLite
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_active_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="sessions")


class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    preference_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False, unique=True)
    currency = Column(String(3), default='KES')
    language = Column(String(10), default='en')
    theme = Column(String(20), default='light')
    notification_email = Column(Boolean, default=True)
    notification_push = Column(Boolean, default=True)
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="preferences")


class EmailVerificationOTP(db.Model):
    __tablename__ = 'email_verification_otps'

    otp_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    email = Column(String(255), nullable=False)
    otp_code = Column(String(6), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)

    # Relationships
    user = relationship("User")

    def is_expired(self):
        """Check if OTP has expired"""
        now = datetime.now(timezone.utc)
        # Ensure both datetimes are timezone-aware for comparison
        if self.expires_at.tzinfo is None:
            expires_at = self.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at = self.expires_at
        return now > expires_at

    def is_valid(self):
        """Check if OTP is valid (not used, not expired, attempts < 3)"""
        return not self.is_used and not self.is_expired() and self.attempts < 3