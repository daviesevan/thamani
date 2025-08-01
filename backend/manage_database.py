#!/usr/bin/env python3
"""
Database management script for Thamani Price Tracker
Provides commands to seed, reset, and manage the database
"""

import argparse
import sys
from app import create_app
from app.models.product import Category, Retailer, Product, ProductRetailer, PriceHistory
from app.models.user import User, UserPreference
from app.models.tracking import UserTrackedProduct, PriceAlert, UserNotification
from app.extensions.extensions import db
from seed_database import seed_database
from add_sample_user import create_sample_user

def check_database():
    """Check current database content"""
    app = create_app()
    with app.app_context():
        print("🔍 Database Content Check")
        print("=" * 50)
        
        # Check Categories
        categories = Category.query.all()
        print(f"\n📁 Categories ({len(categories)}):")
        for cat in categories:
            print(f"  - ID: {cat.category_id}, Name: {cat.name}")
        
        # Check Retailers
        retailers = Retailer.query.all()
        print(f"\n🏪 Retailers ({len(retailers)}):")
        for retailer in retailers:
            print(f"  - ID: {retailer.retailer_id}, Name: {retailer.name}")
            print(f"    URL: {retailer.website_url}")
        
        # Check Products
        products = Product.query.all()
        print(f"\n📱 Products ({len(products)}):")
        for product in products:
            print(f"  - ID: {product.product_id}")
            print(f"    Name: {product.name}")
            print(f"    Brand: {product.brand}")
            print(f"    Category: {product.category.name if product.category else 'None'}")
            
            # Show retailer prices
            for pr in product.product_retailers:
                print(f"    💰 {pr.retailer.name}: KES {pr.current_price:,.0f}")
            print()
        
        # Check Users
        users = User.query.all()
        print(f"\n👥 Users ({len(users)}):")
        for user in users:
            print(f"  - ID: {user.user_id}")
            print(f"    Email: {user.email}")
            print(f"    Username: {user.username}")
            
            # Show tracked products
            tracked = UserTrackedProduct.query.filter_by(user_id=user.user_id).all()
            print(f"    📊 Tracked Products: {len(tracked)}")
            print()

def reset_database():
    """Reset the database (drop all tables and recreate)"""
    app = create_app()
    with app.app_context():
        print("🗑️  Resetting Database")
        print("=" * 30)
        
        response = input("⚠️  This will delete ALL data. Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled")
            return
        
        db.drop_all()
        db.create_all()
        print("✅ Database reset successfully!")

def seed_full_database():
    """Seed database with sample data and create sample user"""
    print("🌱 Full Database Setup")
    print("=" * 30)
    
    # Seed basic data
    seed_database()
    
    # Create sample user
    print("\n" + "=" * 30)
    create_sample_user()
    
    print("\n🎉 Full database setup complete!")
    print("\n📋 Quick Start:")
    print("   1. Start the backend server: python app.py")
    print("   2. Start the frontend server: npm start")
    print("   3. Login with: test@thamani.com / password123")
    print("   4. Try searching for 'Samsung' to test web scraping")

def add_more_products():
    """Add more sample products to the database"""
    app = create_app()
    with app.app_context():
        print("📱 Adding More Sample Products")
        print("=" * 40)
        
        # Get existing categories and retailers
        smartphones = Category.query.filter_by(name="Smartphones").first()
        laptops = Category.query.filter_by(name="Laptops").first()
        audio = Category.query.filter_by(name="Audio").first()
        
        jumia = Retailer.query.filter_by(name="Jumia Kenya").first()
        kilimall = Retailer.query.filter_by(name="Kilimall").first()
        
        if not all([smartphones, laptops, audio, jumia, kilimall]):
            print("❌ Required categories or retailers not found. Run seed first.")
            return
        
        additional_products = [
            {
                "name": "Xiaomi Redmi Note 12",
                "description": "Affordable smartphone with great camera",
                "category_id": smartphones.category_id,
                "brand": "Xiaomi",
                "model": "Redmi Note 12",
                "retailers": [
                    {"retailer": jumia, "price": 25000.0},
                    {"retailer": kilimall, "price": 24500.0}
                ]
            },
            {
                "name": "HP Pavilion 15",
                "description": "Mid-range laptop for everyday use",
                "category_id": laptops.category_id,
                "brand": "HP",
                "model": "Pavilion 15",
                "retailers": [
                    {"retailer": jumia, "price": 65000.0},
                    {"retailer": kilimall, "price": 67000.0}
                ]
            },
            {
                "name": "Sony WH-1000XM4",
                "description": "Premium noise-cancelling headphones",
                "category_id": audio.category_id,
                "brand": "Sony",
                "model": "WH-1000XM4",
                "retailers": [
                    {"retailer": jumia, "price": 45000.0}
                ]
            }
        ]
        
        for prod_data in additional_products:
            product = Product(
                name=prod_data["name"],
                description=prod_data["description"],
                category_id=prod_data["category_id"],
                brand=prod_data["brand"],
                model=prod_data["model"]
            )
            db.session.add(product)
            db.session.flush()
            
            for ret_data in prod_data["retailers"]:
                product_retailer = ProductRetailer(
                    product_id=product.product_id,
                    retailer_id=ret_data["retailer"].retailer_id,
                    current_price=ret_data["price"],
                    currency_code="KES",
                    retailer_product_url=f"https://example.com/{product.name.lower().replace(' ', '-')}",
                    in_stock=True,
                    is_scrapable=True
                )
                db.session.add(product_retailer)
            
            print(f"  ✅ {product.name}")
        
        db.session.commit()
        print(f"\n✅ Added {len(additional_products)} more products!")

def main():
    parser = argparse.ArgumentParser(description="Thamani Database Management")
    parser.add_argument('command', choices=[
        'check', 'seed', 'reset', 'full-setup', 'add-products', 'add-user'
    ], help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'check':
        check_database()
    elif args.command == 'seed':
        seed_database()
    elif args.command == 'reset':
        reset_database()
    elif args.command == 'full-setup':
        seed_full_database()
    elif args.command == 'add-products':
        add_more_products()
    elif args.command == 'add-user':
        create_sample_user()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("🗄️  Thamani Database Management")
        print("=" * 40)
        print("Available commands:")
        print("  check       - Check current database content")
        print("  seed        - Seed database with sample data")
        print("  reset       - Reset database (delete all data)")
        print("  full-setup  - Complete setup (seed + sample user)")
        print("  add-products- Add more sample products")
        print("  add-user    - Create sample user")
        print("\nUsage: python manage_database.py <command>")
    else:
        main()
