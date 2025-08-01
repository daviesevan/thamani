#!/usr/bin/env python3
"""
Add a sample user for testing the application
"""

from app import create_app
from app.models.user import User, UserPreference
from app.models.tracking import UserTrackedProduct
from app.models.product import Product
from app.extensions.extensions import db, bcrypt
from datetime import datetime, timezone
import uuid

def create_sample_user():
    """Create a sample user for testing"""
    app = create_app()
    with app.app_context():
        print("👤 Creating Sample User")
        print("=" * 30)
        
        # Check if user already exists
        existing_user = User.query.filter_by(email="test@thamani.com").first()
        if existing_user:
            print("⚠️  Sample user already exists!")
            print(f"   Email: {existing_user.email}")
            print(f"   Username: {existing_user.username}")
            return existing_user
        
        # Create sample user
        user = User(
            user_id=str(uuid.uuid4()),
            email="test@thamani.com",
            username="testuser",
            full_name="Test User",
            password_hash=bcrypt.generate_password_hash("password123").decode('utf-8'),
            account_status="active",
            email_verified=True
        )
        db.session.add(user)
        db.session.flush()
        
        # Create user preferences
        preferences = UserPreference(
            user_id=user.user_id,
            currency="KES",
            language="en",
            theme="light",
            notification_email=True,
            notification_push=True,
            onboarding_completed=True
        )
        db.session.add(preferences)
        
        # Add some tracked products
        products = Product.query.limit(3).all()
        for product in products:
            current_price = float(product.product_retailers[0].current_price)
            tracked_product = UserTrackedProduct(
                user_id=user.user_id,
                product_id=product.product_id,
                target_price=current_price * 0.9,  # 10% discount target
                notes=f"Tracking {product.name}",
                alert_threshold_percent=10.0,
                tracking_status='active'
            )
            db.session.add(tracked_product)
        
        db.session.commit()
        
        print("✅ Sample user created successfully!")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Password: password123")
        print(f"   Tracked Products: {len(products)}")
        
        return user

if __name__ == '__main__':
    create_sample_user()
