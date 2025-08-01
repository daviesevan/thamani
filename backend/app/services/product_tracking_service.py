"""
Product tracking service for managing user tracked products and price alerts
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from decimal import Decimal
from flask import abort
from sqlalchemy import desc, and_
from app.extensions.extensions import db
from app.models.product import Product, ProductRetailer, PriceHistory, Category, Retailer
from app.models.tracking import UserTrackedProduct, PriceAlert, UserNotification
from app.models.user import User

# Set up logger
logger = logging.getLogger(__name__)


class ProductTrackingService:
    """
    Service for managing product tracking and price monitoring
    """

    @classmethod
    def _ensure_product_in_database(cls, product_id) -> int:
        """
        Ensure a product exists in the database, creating it if it's a scraped product

        Args:
            product_id: Product ID (int for database products, str for scraped products)

        Returns:
            Integer product ID for database operations
        """
        try:
            # If it's already an integer, check if it exists in database
            if isinstance(product_id, int) or (isinstance(product_id, str) and product_id.isdigit()):
                int_product_id = int(product_id)
                product = Product.query.get(int_product_id)
                if product:
                    return int_product_id
                else:
                    abort(404, description="Product not found")

            # If it's a string ID, it's a scraped product - get it from cache
            from app.services.product_service import ProductService
            cached_product = ProductService._get_cached_scraped_product(str(product_id))

            if not cached_product:
                abort(404, description="Scraped product not found in cache. Please search for the product again.")

            # Create a database entry for the scraped product
            return cls._create_database_product_from_scraped(cached_product)

        except Exception as e:
            logger.error(f"Error ensuring product in database: {str(e)}")
            raise

    @classmethod
    def _create_database_product_from_scraped(cls, scraped_product: Dict[str, Any]) -> int:
        """
        Create a database product entry from scraped product data

        Args:
            scraped_product: Scraped product data

        Returns:
            Integer product ID for the created database product
        """
        try:
            # Check if a similar product already exists
            existing_product = Product.query.filter_by(
                name=scraped_product.get('name', ''),
                brand=scraped_product.get('brand', '')
            ).first()

            if existing_product:
                return existing_product.product_id

            # Create new product
            product = Product(
                name=scraped_product.get('name', ''),
                brand=scraped_product.get('brand', ''),
                model=scraped_product.get('model', ''),
                description=scraped_product.get('description', ''),
                image_url=scraped_product.get('image_url', ''),
                category_id=None,  # We'll handle category mapping later
                created_at=datetime.now(timezone.utc)
            )

            db.session.add(product)
            db.session.flush()  # Get the product_id without committing

            # Create retailer entries for the scraped product
            for retailer_data in scraped_product.get('retailers', []):
                # Find or create retailer
                retailer = Retailer.query.filter_by(name=retailer_data.get('retailer_name', retailer_data.get('name', ''))).first()
                if not retailer:
                    retailer = Retailer(
                        name=retailer_data.get('retailer_name', retailer_data.get('name', '')),
                        website_url=retailer_data.get('retailer_product_url', ''),
                        is_active=True,
                        created_at=datetime.now(timezone.utc)
                    )
                    db.session.add(retailer)
                    db.session.flush()

                # Create product-retailer relationship
                product_retailer = ProductRetailer(
                    product_id=product.product_id,
                    retailer_id=retailer.retailer_id,
                    retailer_product_url=retailer_data.get('retailer_product_url', ''),
                    current_price=retailer_data.get('current_price', 0),
                    original_price=retailer_data.get('original_price'),
                    currency_code=retailer_data.get('currency_code', 'KES'),
                    in_stock=retailer_data.get('in_stock', True),
                    last_updated=datetime.now(timezone.utc)
                )
                db.session.add(product_retailer)

            db.session.commit()
            logger.info(f"Created database product {product.product_id} from scraped data")
            return product.product_id

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating database product from scraped data: {str(e)}")
            raise

    @classmethod
    def add_tracked_product(cls, user_id: str, product_id, target_price: Optional[float] = None,
                          notes: Optional[str] = None, alert_threshold_percent: float = 10.0) -> Dict[str, Any]:
        """
        Add a product to user's tracking list
        
        Args:
            user_id: User's ID
            product_id: Product ID to track
            target_price: Optional target price for alerts
            notes: Optional user notes
            alert_threshold_percent: Percentage threshold for price alerts
            
        Returns:
            Dict containing tracking information
        """
        try:
            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                abort(404, description="User not found")

            # Ensure product exists in database (handles both DB and scraped products)
            db_product_id = cls._ensure_product_in_database(product_id)

            # Check if already tracking
            existing_tracking = UserTrackedProduct.query.filter_by(
                user_id=user_id, product_id=db_product_id
            ).first()
            
            if existing_tracking:
                if existing_tracking.is_archived:
                    # Reactivate archived tracking
                    existing_tracking.is_archived = False
                    existing_tracking.tracking_status = 'active'
                    existing_tracking.added_at = datetime.now(timezone.utc)
                    if target_price:
                        existing_tracking.target_price = Decimal(str(target_price))
                    if notes:
                        existing_tracking.notes = notes
                    existing_tracking.alert_threshold_percent = Decimal(str(alert_threshold_percent))
                    
                    db.session.commit()
                    logger.info(f"Reactivated tracking for user {user_id}, product {db_product_id}")
                else:
                    abort(400, description="Product is already being tracked")
            else:
                # Create new tracking
                tracked_product = UserTrackedProduct(
                    user_id=user_id,
                    product_id=db_product_id,
                    target_price=Decimal(str(target_price)) if target_price else None,
                    notes=notes,
                    alert_threshold_percent=Decimal(str(alert_threshold_percent))
                )

                db.session.add(tracked_product)
                db.session.commit()
                logger.info(f"Added tracking for user {user_id}, product {db_product_id}")

            # Get the tracking with product details
            return cls.get_tracked_product_details(user_id, db_product_id)
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding tracked product: {str(e)}")
            abort(500, description="Internal server error")
    
    @classmethod
    def remove_tracked_product(cls, user_id: str, product_id) -> Dict[str, Any]:
        """
        Remove a product from user's tracking list
        
        Args:
            user_id: User's ID
            product_id: Product ID to stop tracking
            
        Returns:
            Dict containing removal confirmation
        """
        try:
            # Convert to database product ID if needed
            db_product_id = cls._ensure_product_in_database(product_id)

            tracked_product = UserTrackedProduct.query.filter_by(
                user_id=user_id, product_id=db_product_id
            ).first()
            
            if not tracked_product:
                abort(404, description="Tracked product not found")
            
            # Archive instead of delete to preserve history
            tracked_product.is_archived = True
            tracked_product.tracking_status = 'archived'
            
            # Also deactivate related price alerts
            PriceAlert.query.filter_by(user_id=user_id).filter(
                PriceAlert.product_retailer.has(product_id=product_id)
            ).update({'is_active': False})
            
            db.session.commit()
            logger.info(f"Removed tracking for user {user_id}, product {product_id}")
            
            return {
                "message": "Product removed from tracking list",
                "product_id": product_id
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing tracked product: {str(e)}")
            abort(500, description="Internal server error")
    
    @classmethod
    def get_user_tracked_products(cls, user_id: str, include_archived: bool = False) -> List[Dict[str, Any]]:
        """
        Get all products tracked by a user
        
        Args:
            user_id: User's ID
            include_archived: Whether to include archived products
            
        Returns:
            List of tracked products with details
        """
        try:
            query = UserTrackedProduct.query.filter_by(user_id=user_id)
            
            if not include_archived:
                query = query.filter_by(is_archived=False)
            
            tracked_products = query.order_by(desc(UserTrackedProduct.added_at)).all()
            
            result = []
            for tracked in tracked_products:
                product_data = cls._format_tracked_product(tracked)
                result.append(product_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting tracked products: {str(e)}")
            abort(500, description="Internal server error")
    
    @classmethod
    def get_tracked_product_details(cls, user_id: str, product_id) -> Dict[str, Any]:
        """
        Get detailed information about a tracked product

        Args:
            user_id: User's ID
            product_id: Product ID (int for database products, str for scraped products)

        Returns:
            Dict containing detailed product and tracking information
        """
        try:
            # Convert to database product ID if needed
            db_product_id = cls._ensure_product_in_database(product_id)

            tracked_product = UserTrackedProduct.query.filter_by(
                user_id=user_id, product_id=db_product_id, is_archived=False
            ).first()
            
            if not tracked_product:
                abort(404, description="Tracked product not found")
            
            return cls._format_tracked_product(tracked_product, include_price_history=True)
            
        except Exception as e:
            logger.error(f"Error getting tracked product details: {str(e)}")
            abort(500, description="Internal server error")
    
    @classmethod
    def update_tracked_product(cls, user_id: str, product_id: int, 
                             target_price: Optional[float] = None,
                             notes: Optional[str] = None,
                             alert_threshold_percent: Optional[float] = None) -> Dict[str, Any]:
        """
        Update tracking settings for a product
        
        Args:
            user_id: User's ID
            product_id: Product ID
            target_price: New target price
            notes: New notes
            alert_threshold_percent: New alert threshold
            
        Returns:
            Dict containing updated tracking information
        """
        try:
            tracked_product = UserTrackedProduct.query.filter_by(
                user_id=user_id, product_id=product_id, is_archived=False
            ).first()
            
            if not tracked_product:
                abort(404, description="Tracked product not found")
            
            # Update fields if provided
            if target_price is not None:
                tracked_product.target_price = Decimal(str(target_price)) if target_price > 0 else None
            
            if notes is not None:
                tracked_product.notes = notes
            
            if alert_threshold_percent is not None:
                tracked_product.alert_threshold_percent = Decimal(str(alert_threshold_percent))
            
            db.session.commit()
            logger.info(f"Updated tracking for user {user_id}, product {product_id}")
            
            return cls._format_tracked_product(tracked_product)
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating tracked product: {str(e)}")
            abort(500, description="Internal server error")
    
    @classmethod
    def _format_tracked_product(cls, tracked_product: UserTrackedProduct, 
                               include_price_history: bool = False) -> Dict[str, Any]:
        """
        Format tracked product data for API response
        
        Args:
            tracked_product: UserTrackedProduct instance
            include_price_history: Whether to include price history
            
        Returns:
            Dict containing formatted product data
        """
        product = tracked_product.product
        
        # Get current prices from all retailers
        retailers_data = []
        lowest_price = None
        highest_price = None
        
        for product_retailer in product.product_retailers:
            retailer_data = {
                "retailer_id": product_retailer.retailer.retailer_id,
                "retailer_name": product_retailer.retailer.name,
                "retailer_logo": product_retailer.retailer.logo_url,
                "current_price": float(product_retailer.current_price),
                "currency": product_retailer.currency_code,
                "in_stock": product_retailer.in_stock,
                "product_url": product_retailer.retailer_product_url,
                "last_updated": product_retailer.last_updated.isoformat()
            }
            retailers_data.append(retailer_data)
            
            # Track lowest and highest prices
            price = float(product_retailer.current_price)
            if product_retailer.in_stock:
                if lowest_price is None or price < lowest_price:
                    lowest_price = price
                if highest_price is None or price > highest_price:
                    highest_price = price
        
        result = {
            "tracking_id": tracked_product.tracking_id,
            "product": {
                "product_id": product.product_id,
                "name": product.name,
                "description": product.description,
                "brand": product.brand,
                "model": product.model,
                "image_url": product.image_url,
                "category": {
                    "category_id": product.category.category_id,
                    "name": product.category.name
                } if product.category else None
            },
            "tracking_info": {
                "added_at": tracked_product.added_at.isoformat(),
                "target_price": float(tracked_product.target_price) if tracked_product.target_price else None,
                "notes": tracked_product.notes,
                "alert_threshold_percent": float(tracked_product.alert_threshold_percent),
                "tracking_status": tracked_product.tracking_status,
                "last_notification_sent": tracked_product.last_notification_sent.isoformat() if tracked_product.last_notification_sent else None
            },
            "price_info": {
                "lowest_price": lowest_price,
                "highest_price": highest_price,
                "retailers": retailers_data
            }
        }
        
        if include_price_history:
            # Get recent price history (last 30 days)
            from datetime import timedelta
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            
            price_history = []
            for product_retailer in product.product_retailers:
                history = PriceHistory.query.filter(
                    and_(
                        PriceHistory.product_retailer_id == product_retailer.product_retailer_id,
                        PriceHistory.timestamp >= thirty_days_ago
                    )
                ).order_by(PriceHistory.timestamp).all()
                
                for entry in history:
                    price_history.append({
                        "retailer_name": product_retailer.retailer.name,
                        "price": float(entry.price),
                        "currency": entry.currency_code,
                        "timestamp": entry.timestamp.isoformat(),
                        "is_on_sale": entry.is_on_sale,
                        "original_price": float(entry.original_price) if entry.original_price else None
                    })
            
            result["price_history"] = sorted(price_history, key=lambda x: x["timestamp"])
        
        return result
