#!/usr/bin/env python3
"""
Database seeding script for Thamani Price Tracker
Populates the database with initial categories, retailers, and sample products
"""

from app import create_app
from app.models.product import Category, Retailer, Product, ProductRetailer, PriceHistory
from app.models.user import User, UserPreference
from app.extensions.extensions import db
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

def seed_database():
    """Seed the database with initial data"""
    app = create_app()
    with app.app_context():
        print("🌱 Seeding Database")
        print("=" * 50)
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("🗑️  Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Seed Categories
        print("📁 Seeding Categories...")
        categories_data = [
            {"name": "Smartphones", "parent_id": None},
            {"name": "Laptops", "parent_id": None},
            {"name": "Tablets", "parent_id": None},
            {"name": "Audio", "parent_id": None},
            {"name": "Gaming", "parent_id": None},
            {"name": "Accessories", "parent_id": None},
            {"name": "Home & Garden", "parent_id": None},
            {"name": "Fashion", "parent_id": None},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category = Category(
                name=cat_data["name"],
                parent_category_id=cat_data["parent_id"]
            )
            db.session.add(category)
            db.session.flush()  # Get the ID
            categories[cat_data["name"]] = category
            print(f"  ✅ {category.name}")
        
        # Seed Retailers
        print("\n🏪 Seeding Retailers...")
        retailers_data = [
            {
                "name": "Jumia Kenya",
                "website_url": "https://www.jumia.co.ke",
                "logo_url": "https://www.jumia.co.ke/favicon.ico",
                "country_code": "KE"
            },
            {
                "name": "Kilimall",
                "website_url": "https://www.kilimall.co.ke",
                "logo_url": "https://www.kilimall.co.ke/favicon.ico",
                "country_code": "KE"
            },
            {
                "name": "Jiji Kenya",
                "website_url": "https://jiji.co.ke",
                "logo_url": "https://jiji.co.ke/favicon.ico",
                "country_code": "KE"
            },
            {
                "name": "Masoko",
                "website_url": "https://www.masoko.com",
                "logo_url": "https://www.masoko.com/favicon.ico",
                "country_code": "KE"
            }
        ]
        
        retailers = {}
        for ret_data in retailers_data:
            retailer = Retailer(
                name=ret_data["name"],
                website_url=ret_data["website_url"],
                logo_url=ret_data["logo_url"],
                country_code=ret_data["country_code"]
            )
            db.session.add(retailer)
            db.session.flush()  # Get the ID
            retailers[ret_data["name"]] = retailer
            print(f"  ✅ {retailer.name}")
        
        # Seed Sample Products
        print("\n📱 Seeding Sample Products...")
        products_data = [
            {
                "name": "Samsung Galaxy S23",
                "description": "Latest Samsung flagship smartphone with advanced camera and performance",
                "category": "Smartphones",
                "brand": "Samsung",
                "model": "Galaxy S23",
                "image_url": "/products/samsung-s23.jpg",
                "retailers": [
                    {"retailer": "Jumia Kenya", "price": 85827.0, "url": "https://www.jumia.co.ke/samsung-galaxy-s23"},
                    {"retailer": "Kilimall", "price": 90370.0, "url": "https://www.kilimall.co.ke/samsung-galaxy-s23"},
                    {"retailer": "Masoko", "price": 88500.0, "url": "https://www.masoko.com/samsung-galaxy-s23"}
                ]
            },
            {
                "name": "iPhone 14 Pro",
                "description": "Apple's premium smartphone with Pro camera system",
                "category": "Smartphones",
                "brand": "Apple",
                "model": "iPhone 14 Pro",
                "image_url": "/products/iphone-14-pro.jpg",
                "retailers": [
                    {"retailer": "Jumia Kenya", "price": 145000.0, "url": "https://www.jumia.co.ke/iphone-14-pro"},
                    {"retailer": "Masoko", "price": 142000.0, "url": "https://www.masoko.com/iphone-14-pro"}
                ]
            },
            {
                "name": "MacBook Air M2",
                "description": "Apple's lightweight laptop with M2 chip",
                "category": "Laptops",
                "brand": "Apple",
                "model": "MacBook Air M2",
                "image_url": "/products/macbook-air-m2.jpg",
                "retailers": [
                    {"retailer": "Jumia Kenya", "price": 165000.0, "url": "https://www.jumia.co.ke/macbook-air-m2"},
                    {"retailer": "Masoko", "price": 162000.0, "url": "https://www.masoko.com/macbook-air-m2"}
                ]
            },
            {
                "name": "Dell XPS 13",
                "description": "Premium ultrabook with Intel processors",
                "category": "Laptops",
                "brand": "Dell",
                "model": "XPS 13",
                "image_url": "/products/dell-xps-13.jpg",
                "retailers": [
                    {"retailer": "Jumia Kenya", "price": 125000.0, "url": "https://www.jumia.co.ke/dell-xps-13"},
                    {"retailer": "Kilimall", "price": 128000.0, "url": "https://www.kilimall.co.ke/dell-xps-13"}
                ]
            },
            {
                "name": "AirPods Pro 2nd Gen",
                "description": "Apple's premium wireless earbuds with noise cancellation",
                "category": "Audio",
                "brand": "Apple",
                "model": "AirPods Pro 2",
                "image_url": "/products/airpods-pro-2.jpg",
                "retailers": [
                    {"retailer": "Jumia Kenya", "price": 32000.0, "url": "https://www.jumia.co.ke/airpods-pro-2"},
                    {"retailer": "Masoko", "price": 31500.0, "url": "https://www.masoko.com/airpods-pro-2"}
                ]
            }
        ]
        
        for prod_data in products_data:
            # Create product
            product = Product(
                name=prod_data["name"],
                description=prod_data["description"],
                category_id=categories[prod_data["category"]].category_id,
                brand=prod_data["brand"],
                model=prod_data["model"],
                image_url=prod_data["image_url"]
            )
            db.session.add(product)
            db.session.flush()  # Get the ID
            
            print(f"  ✅ {product.name}")
            
            # Create product-retailer relationships
            for ret_data in prod_data["retailers"]:
                retailer = retailers[ret_data["retailer"]]
                
                product_retailer = ProductRetailer(
                    product_id=product.product_id,
                    retailer_id=retailer.retailer_id,
                    current_price=ret_data["price"],
                    currency_code="KES",
                    retailer_product_url=ret_data["url"],
                    in_stock=True,
                    is_scrapable=True
                )
                db.session.add(product_retailer)
                db.session.flush()
                
                # Create initial price history
                price_history = PriceHistory(
                    product_retailer_id=product_retailer.product_retailer_id,
                    price=ret_data["price"],
                    currency_code="KES",
                    timestamp=datetime.now(timezone.utc)
                )
                db.session.add(price_history)
                
                print(f"    💰 {retailer.name}: KES {ret_data['price']:,.0f}")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n✅ Database seeded successfully!")
        print(f"   📁 Categories: {len(categories_data)}")
        print(f"   🏪 Retailers: {len(retailers_data)}")
        print(f"   📱 Products: {len(products_data)}")
        
        # Print summary
        print(f"\n📊 Database Summary:")
        print(f"   Categories: {Category.query.count()}")
        print(f"   Retailers: {Retailer.query.count()}")
        print(f"   Products: {Product.query.count()}")
        print(f"   Product-Retailer Links: {ProductRetailer.query.count()}")
        print(f"   Price History Records: {PriceHistory.query.count()}")

if __name__ == '__main__':
    seed_database()
