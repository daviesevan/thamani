"""
Wishlist service for managing user wishlists and wishlist items
"""
import logging
from typing import Dict, List, Any, Optional
from flask import abort
from sqlalchemy import or_, and_, desc
from app.extensions.extensions import db
from app.models.user import User
from app.models.product import Product, ProductRetailer, Retailer
from app.models.tracking import UserWishlist, WishlistItem
from datetime import datetime, timezone
from decimal import Decimal

# Set up logger
logger = logging.getLogger(__name__)


class WishlistService:
    """
    Service for managing user wishlists and wishlist items
    """
    
    @classmethod
    def get_user_wishlists(cls, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all wishlists for a user
        
        Args:
            user_id: User's ID
            
        Returns:
            List of user's wishlists
        """
        try:
            user = User.query.get(user_id)
            if not user:
                abort(404, description="User not found")
            
            wishlists = UserWishlist.query.filter_by(user_id=user_id).order_by(
                desc(UserWishlist.is_default), UserWishlist.created_at
            ).all()
            
            return [wishlist.to_dict() for wishlist in wishlists]
            
        except Exception as e:
            logger.error(f"Error getting user wishlists: {str(e)}")
            raise
    
    @classmethod
    def create_wishlist(cls, user_id: str, name: str, description: str = '', 
                       is_default: bool = False) -> Dict[str, Any]:
        """
        Create a new wishlist for a user
        
        Args:
            user_id: User's ID
            name: Wishlist name
            description: Wishlist description
            is_default: Whether this is the default wishlist
            
        Returns:
            Created wishlist data
        """
        try:
            user = User.query.get(user_id)
            if not user:
                abort(404, description="User not found")
            
            # If this is set as default, unset other default wishlists
            if is_default:
                UserWishlist.query.filter_by(user_id=user_id, is_default=True).update(
                    {'is_default': False}
                )
            
            wishlist = UserWishlist(
                user_id=user_id,
                name=name,
                description=description,
                is_default=is_default
            )
            
            db.session.add(wishlist)
            db.session.commit()
            
            logger.info(f"Created wishlist {wishlist.wishlist_id} for user {user_id}")
            return wishlist.to_dict()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating wishlist: {str(e)}")
            raise
    
    @classmethod
    def get_wishlist_details(cls, user_id: str, wishlist_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific wishlist
        
        Args:
            user_id: User's ID
            wishlist_id: Wishlist ID
            
        Returns:
            Detailed wishlist information with items
        """
        try:
            wishlist = UserWishlist.query.filter_by(
                wishlist_id=wishlist_id, user_id=user_id
            ).first()
            
            if not wishlist:
                abort(404, description="Wishlist not found")
            
            # Get wishlist items with product details
            items = []
            for item in wishlist.items:
                item_data = item.to_dict()
                if item.product:
                    item_data['product'] = cls._format_product_for_wishlist(item.product)
                items.append(item_data)
            
            wishlist_data = wishlist.to_dict()
            wishlist_data['items'] = items
            
            return wishlist_data
            
        except Exception as e:
            logger.error(f"Error getting wishlist details: {str(e)}")
            raise
    
    @classmethod
    def add_item_to_wishlist(cls, user_id: str, wishlist_id: int, product_id, 
                           notes: str = '', priority: str = 'medium', 
                           target_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Add a product to a wishlist
        Supports both database products (int IDs) and scraped products (string IDs)
        
        Args:
            user_id: User's ID
            wishlist_id: Wishlist ID
            product_id: Product ID (int for database products, str for scraped products)
            notes: User notes
            priority: Priority level
            target_price: Target price for the product
            
        Returns:
            Created wishlist item data
        """
        try:
            # Verify wishlist exists and belongs to user
            wishlist = UserWishlist.query.filter_by(
                wishlist_id=wishlist_id, user_id=user_id
            ).first()
            
            if not wishlist:
                abort(404, description="Wishlist not found")
            
            # Handle both database and scraped products
            db_product_id, source, original_scraped_id, price_when_added = cls._ensure_product_in_database(product_id)
            
            # Check if item already exists in wishlist
            existing_item = WishlistItem.query.filter_by(
                wishlist_id=wishlist_id, product_id=db_product_id
            ).first()
            
            if existing_item:
                abort(400, description="Product is already in this wishlist")
            
            # Create wishlist item
            wishlist_item = WishlistItem(
                wishlist_id=wishlist_id,
                product_id=db_product_id,
                notes=notes,
                priority=priority,
                target_price=Decimal(str(target_price)) if target_price else None,
                source=source,
                original_scraped_id=original_scraped_id,
                price_when_added=price_when_added
            )
            
            db.session.add(wishlist_item)
            db.session.commit()
            
            logger.info(f"Added product {db_product_id} to wishlist {wishlist_id}")
            
            # Return item with product details
            item_data = wishlist_item.to_dict()
            if wishlist_item.product:
                item_data['product'] = cls._format_product_for_wishlist(wishlist_item.product)
            
            return item_data
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding item to wishlist: {str(e)}")
            raise

    @classmethod
    def remove_item_from_wishlist(cls, user_id: str, wishlist_id: int, item_id: int) -> Dict[str, Any]:
        """
        Remove an item from a wishlist

        Args:
            user_id: User's ID
            wishlist_id: Wishlist ID
            item_id: Wishlist item ID

        Returns:
            Removal confirmation
        """
        try:
            # Verify wishlist belongs to user
            wishlist = UserWishlist.query.filter_by(
                wishlist_id=wishlist_id, user_id=user_id
            ).first()

            if not wishlist:
                abort(404, description="Wishlist not found")

            # Find and remove the item
            item = WishlistItem.query.filter_by(
                wishlist_item_id=item_id, wishlist_id=wishlist_id
            ).first()

            if not item:
                abort(404, description="Wishlist item not found")

            db.session.delete(item)
            db.session.commit()

            logger.info(f"Removed item {item_id} from wishlist {wishlist_id}")

            return {
                'message': 'Item removed from wishlist successfully',
                'wishlist_item_id': item_id
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing item from wishlist: {str(e)}")
            raise

    @classmethod
    def update_wishlist_item(cls, user_id: str, wishlist_id: int, item_id: int,
                           notes: Optional[str] = None, priority: Optional[str] = None,
                           target_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Update a wishlist item

        Args:
            user_id: User's ID
            wishlist_id: Wishlist ID
            item_id: Wishlist item ID
            notes: Updated notes
            priority: Updated priority
            target_price: Updated target price

        Returns:
            Updated wishlist item data
        """
        try:
            # Verify wishlist belongs to user
            wishlist = UserWishlist.query.filter_by(
                wishlist_id=wishlist_id, user_id=user_id
            ).first()

            if not wishlist:
                abort(404, description="Wishlist not found")

            # Find the item
            item = WishlistItem.query.filter_by(
                wishlist_item_id=item_id, wishlist_id=wishlist_id
            ).first()

            if not item:
                abort(404, description="Wishlist item not found")

            # Update fields if provided
            if notes is not None:
                item.notes = notes
            if priority is not None:
                item.priority = priority
            if target_price is not None:
                item.target_price = Decimal(str(target_price)) if target_price else None

            db.session.commit()

            logger.info(f"Updated wishlist item {item_id}")

            # Return updated item with product details
            item_data = item.to_dict()
            if item.product:
                item_data['product'] = cls._format_product_for_wishlist(item.product)

            return item_data

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating wishlist item: {str(e)}")
            raise

    @classmethod
    def get_all_user_wishlist_items(cls, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all wishlist items for a user across all wishlists

        Args:
            user_id: User's ID

        Returns:
            List of all user's wishlist items
        """
        try:
            user = User.query.get(user_id)
            if not user:
                abort(404, description="User not found")

            # Get all wishlist items for the user
            items = db.session.query(WishlistItem).join(UserWishlist).filter(
                UserWishlist.user_id == user_id
            ).order_by(desc(WishlistItem.added_at)).all()

            result = []
            for item in items:
                item_data = item.to_dict()
                if item.product:
                    item_data['product'] = cls._format_product_for_wishlist(item.product)
                if item.wishlist:
                    item_data['wishlist'] = {
                        'wishlist_id': item.wishlist.wishlist_id,
                        'name': item.wishlist.name,
                        'is_default': item.wishlist.is_default
                    }
                result.append(item_data)

            return result

        except Exception as e:
            logger.error(f"Error getting all user wishlist items: {str(e)}")
            raise

    @classmethod
    def quick_add_to_wishlist(cls, user_id: str, product_id, notes: str = '',
                            priority: str = 'medium', target_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Quick add a product to the user's default wishlist
        Creates a default wishlist if none exists

        Args:
            user_id: User's ID
            product_id: Product ID (int for database products, str for scraped products)
            notes: User notes
            priority: Priority level
            target_price: Target price for the product

        Returns:
            Created wishlist item data
        """
        try:
            user = User.query.get(user_id)
            if not user:
                abort(404, description="User not found")

            # Get or create default wishlist
            default_wishlist = UserWishlist.query.filter_by(
                user_id=user_id, is_default=True
            ).first()

            if not default_wishlist:
                # Create default wishlist
                default_wishlist = cls.create_wishlist(
                    user_id=user_id,
                    name="My Wishlist",
                    description="Default wishlist",
                    is_default=True
                )
                # Convert to object for consistency
                default_wishlist = UserWishlist.query.get(default_wishlist['wishlist_id'])

            # Add item to default wishlist
            return cls.add_item_to_wishlist(
                user_id=user_id,
                wishlist_id=default_wishlist.wishlist_id,
                product_id=product_id,
                notes=notes,
                priority=priority,
                target_price=target_price
            )

        except Exception as e:
            logger.error(f"Error quick adding to wishlist: {str(e)}")
            raise

    @classmethod
    def _ensure_product_in_database(cls, product_id):
        """
        Ensure a product exists in the database, creating it if it's a scraped product

        Args:
            product_id: Product ID (int for database products, str for scraped products)

        Returns:
            Tuple of (db_product_id, source, original_scraped_id, price_when_added)
        """
        try:
            # If it's already an integer, check if it exists in database
            if isinstance(product_id, int) or (isinstance(product_id, str) and product_id.isdigit()):
                int_product_id = int(product_id)
                product = Product.query.get(int_product_id)
                if product:
                    return int_product_id, 'database', None, None
                else:
                    abort(404, description="Product not found")

            # If it's a string ID, it's a scraped product - get it from cache
            from app.services.product_service import ProductService
            cached_product = ProductService._get_cached_scraped_product(str(product_id))

            if not cached_product:
                abort(404, description="Scraped product not found in cache. Please search for the product again.")

            # Create a database entry for the scraped product
            db_product_id = cls._create_database_product_from_scraped(cached_product)

            # Get the price when added (from the first retailer)
            price_when_added = None
            if cached_product.get('retailers') and len(cached_product['retailers']) > 0:
                price_when_added = cached_product['retailers'][0].get('current_price')

            return db_product_id, 'web_scraping', str(product_id), price_when_added

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

            # Create new product (we'll need to handle category_id properly)
            # For now, we'll use a default category or None
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
                retailer = Retailer.query.filter_by(
                    name=retailer_data.get('retailer_name', retailer_data.get('name', ''))
                ).first()

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
    def _format_product_for_wishlist(cls, product: Product) -> Dict[str, Any]:
        """
        Format a product for wishlist display

        Args:
            product: Product object

        Returns:
            Formatted product data
        """
        try:
            # Get current pricing information
            retailers = []
            min_price = None
            max_price = None

            for pr in product.product_retailers:
                retailer_data = {
                    'retailer_id': pr.retailer.retailer_id,
                    'retailer_name': pr.retailer.name,
                    'current_price': float(pr.current_price) if pr.current_price else None,
                    'original_price': float(pr.original_price) if pr.original_price else None,
                    'currency_code': pr.currency_code,
                    'retailer_product_url': pr.retailer_product_url,
                    'in_stock': pr.in_stock,
                    'last_updated': pr.last_updated.isoformat() if pr.last_updated else None
                }
                retailers.append(retailer_data)

                # Track min/max prices
                if pr.current_price and pr.in_stock:
                    price = float(pr.current_price)
                    if min_price is None or price < min_price:
                        min_price = price
                    if max_price is None or price > max_price:
                        max_price = price

            return {
                'product_id': product.product_id,
                'name': product.name,
                'description': product.description,
                'brand': product.brand,
                'model': product.model,
                'image_url': product.image_url,
                'category': {
                    'category_id': product.category.category_id,
                    'name': product.category.name
                } if product.category else None,
                'price_info': {
                    'min_price': min_price,
                    'max_price': max_price,
                    'currency_code': 'KES',
                    'retailers_count': len([r for r in retailers if r['in_stock']])
                },
                'retailers': retailers,
                'created_at': product.created_at.isoformat() if product.created_at else None,
                'updated_at': product.updated_at.isoformat() if product.updated_at else None
            }

        except Exception as e:
            logger.error(f"Error formatting product for wishlist: {str(e)}")
            # Return basic product info if formatting fails
            return {
                'product_id': product.product_id,
                'name': product.name,
                'description': product.description,
                'brand': product.brand,
                'image_url': product.image_url
            }
