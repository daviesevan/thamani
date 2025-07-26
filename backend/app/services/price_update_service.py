"""
Price update service for scheduling and managing price scraping tasks
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy import and_, or_
from celery import Celery
from app.extensions.extensions import db
from app.models.product import ProductRetailer, PriceHistory
from app.services.scraping_service import ScrapingService
from app.services.retailer_scrapers import get_scraper_config

# Set up logger
logger = logging.getLogger(__name__)

class PriceUpdateService:
    """
    Service for managing price updates and scraping schedules
    """
    
    def __init__(self):
        self.scraping_service = ScrapingService()
    
    def update_product_price(self, product_retailer_id: int) -> Dict[str, Any]:
        """
        Update price for a single product-retailer combination
        
        Args:
            product_retailer_id: ID of the ProductRetailer to update
            
        Returns:
            Dict containing update results
        """
        try:
            product_retailer = ProductRetailer.query.get(product_retailer_id)
            if not product_retailer:
                return {"success": False, "error": "ProductRetailer not found"}
            
            # Scrape the current price
            scrape_result = self.scraping_service.scrape_product_price(product_retailer)
            
            if not scrape_result.get("success"):
                # Update scraping error info
                product_retailer.last_scrape_attempt = datetime.now(timezone.utc)
                product_retailer.scraping_error = scrape_result.get("error", "Unknown error")
                db.session.commit()
                
                return {
                    "success": False,
                    "error": scrape_result.get("error"),
                    "product_retailer_id": product_retailer_id
                }
            
            # Extract scraped data
            new_price = scrape_result.get("price")
            in_stock = scrape_result.get("in_stock", True)
            currency = scrape_result.get("currency", "KES")
            scraped_at = scrape_result.get("scraped_at", datetime.now(timezone.utc))
            
            # Check if price has changed
            old_price = float(product_retailer.current_price) if product_retailer.current_price else None
            price_changed = old_price is None or abs(old_price - new_price) > 0.01
            
            # Update ProductRetailer
            product_retailer.current_price = Decimal(str(new_price))
            product_retailer.currency_code = currency
            product_retailer.in_stock = in_stock
            product_retailer.last_updated = scraped_at
            product_retailer.last_scrape_attempt = scraped_at
            product_retailer.scraping_error = None  # Clear any previous errors
            
            # Create price history entry if price changed
            if price_changed:
                price_history = PriceHistory(
                    product_retailer_id=product_retailer_id,
                    price=Decimal(str(new_price)),
                    currency_code=currency,
                    timestamp=scraped_at,
                    is_on_sale=False,  # TODO: Detect sales
                    original_price=None  # TODO: Detect original price if on sale
                )
                db.session.add(price_history)
                
                logger.info(f"Price updated for product {product_retailer.product.name} "
                           f"at {product_retailer.retailer.name}: "
                           f"{old_price} -> {new_price}")
            
            db.session.commit()
            
            return {
                "success": True,
                "product_retailer_id": product_retailer_id,
                "old_price": old_price,
                "new_price": new_price,
                "price_changed": price_changed,
                "in_stock": in_stock,
                "scraped_at": scraped_at.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating price for ProductRetailer {product_retailer_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "product_retailer_id": product_retailer_id
            }
    
    def update_all_prices(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Update prices for all products or a limited number
        
        Args:
            limit: Maximum number of products to update (None for all)
            
        Returns:
            Dict containing batch update results
        """
        try:
            # Get ProductRetailers that need updating
            query = ProductRetailer.query.filter(
                ProductRetailer.retailer_product_url.isnot(None)
            )
            
            # Prioritize products that haven't been updated recently
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=6)
            query = query.filter(
                or_(
                    ProductRetailer.last_updated.is_(None),
                    ProductRetailer.last_updated < cutoff_time
                )
            ).order_by(ProductRetailer.last_updated.asc().nullsfirst())
            
            if limit:
                query = query.limit(limit)
            
            product_retailers = query.all()
            
            results = {
                "total_attempted": len(product_retailers),
                "successful_updates": 0,
                "failed_updates": 0,
                "price_changes": 0,
                "errors": [],
                "updates": []
            }
            
            for pr in product_retailers:
                # Add delay between requests to be respectful
                self.scraping_service.add_random_delay(2, 5)
                
                update_result = self.update_product_price(pr.product_retailer_id)
                results["updates"].append(update_result)
                
                if update_result.get("success"):
                    results["successful_updates"] += 1
                    if update_result.get("price_changed"):
                        results["price_changes"] += 1
                else:
                    results["failed_updates"] += 1
                    results["errors"].append({
                        "product_retailer_id": pr.product_retailer_id,
                        "product_name": pr.product.name,
                        "retailer_name": pr.retailer.name,
                        "error": update_result.get("error")
                    })
            
            logger.info(f"Batch price update completed: {results['successful_updates']} successful, "
                       f"{results['failed_updates']} failed, {results['price_changes']} price changes")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch price update: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "total_attempted": 0,
                "successful_updates": 0,
                "failed_updates": 0,
                "price_changes": 0
            }
    
    def update_prices_for_tracked_products(self, user_id: str) -> Dict[str, Any]:
        """
        Update prices only for products that are being tracked by users
        
        Args:
            user_id: Optional user ID to update only their tracked products
            
        Returns:
            Dict containing update results
        """
        try:
            from app.models.tracking import UserTrackedProduct
            
            # Get ProductRetailers for tracked products
            query = db.session.query(ProductRetailer).join(
                UserTrackedProduct,
                ProductRetailer.product_id == UserTrackedProduct.product_id
            ).filter(
                UserTrackedProduct.is_archived == False,
                ProductRetailer.retailer_product_url.isnot(None)
            )
            
            if user_id:
                query = query.filter(UserTrackedProduct.user_id == user_id)
            
            # Prioritize recently tracked products
            query = query.order_by(UserTrackedProduct.added_at.desc())
            
            product_retailers = query.distinct().all()
            
            results = {
                "total_attempted": len(product_retailers),
                "successful_updates": 0,
                "failed_updates": 0,
                "price_changes": 0,
                "errors": [],
                "updates": []
            }
            
            for pr in product_retailers:
                # Add delay between requests
                self.scraping_service.add_random_delay(1, 3)
                
                update_result = self.update_product_price(pr.product_retailer_id)
                results["updates"].append(update_result)
                
                if update_result.get("success"):
                    results["successful_updates"] += 1
                    if update_result.get("price_changed"):
                        results["price_changes"] += 1
                else:
                    results["failed_updates"] += 1
                    results["errors"].append({
                        "product_retailer_id": pr.product_retailer_id,
                        "product_name": pr.product.name,
                        "retailer_name": pr.retailer.name,
                        "error": update_result.get("error")
                    })
            
            logger.info(f"Tracked products price update completed: {results['successful_updates']} successful, "
                       f"{results['failed_updates']} failed, {results['price_changes']} price changes")
            
            return results
            
        except Exception as e:
            logger.error(f"Error updating tracked product prices: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "total_attempted": 0,
                "successful_updates": 0,
                "failed_updates": 0,
                "price_changes": 0
            }
    
    def get_stale_products(self, hours: int = 24) -> List[ProductRetailer]:
        """
        Get products that haven't been updated in the specified number of hours
        
        Args:
            hours: Number of hours to consider a product stale
            
        Returns:
            List of ProductRetailer instances that need updating
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        return ProductRetailer.query.filter(
            and_(
                ProductRetailer.retailer_product_url.isnot(None),
                or_(
                    ProductRetailer.last_updated.is_(None),
                    ProductRetailer.last_updated < cutoff_time
                )
            )
        ).order_by(ProductRetailer.last_updated.asc().nullsfirst()).all()
    
    def get_scraping_stats(self) -> Dict[str, Any]:
        """
        Get statistics about scraping performance
        
        Returns:
            Dict containing scraping statistics
        """
        try:
            total_products = ProductRetailer.query.filter(
                ProductRetailer.retailer_product_url.isnot(None)
            ).count()
            
            # Products updated in last 24 hours
            last_24h = datetime.now(timezone.utc) - timedelta(hours=24)
            updated_24h = ProductRetailer.query.filter(
                and_(
                    ProductRetailer.retailer_product_url.isnot(None),
                    ProductRetailer.last_updated >= last_24h
                )
            ).count()
            
            # Products with scraping errors
            with_errors = ProductRetailer.query.filter(
                and_(
                    ProductRetailer.retailer_product_url.isnot(None),
                    ProductRetailer.scraping_error.isnot(None)
                )
            ).count()
            
            # Never scraped
            never_scraped = ProductRetailer.query.filter(
                and_(
                    ProductRetailer.retailer_product_url.isnot(None),
                    ProductRetailer.last_updated.is_(None)
                )
            ).count()
            
            return {
                "total_products": total_products,
                "updated_last_24h": updated_24h,
                "with_errors": with_errors,
                "never_scraped": never_scraped,
                "success_rate": round((updated_24h / total_products * 100), 2) if total_products > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting scraping stats: {str(e)}")
            return {
                "error": str(e),
                "total_products": 0,
                "updated_last_24h": 0,
                "with_errors": 0,
                "never_scraped": 0,
                "success_rate": 0
            }
