"""
Celery tasks for price scraping and updates
"""
import logging
from celery import Celery
from app import create_app
from app.services.price_update_service import PriceUpdateService

# Set up logger
logger = logging.getLogger(__name__)

# Create Celery instance
celery = Celery('thamani_price_scraper')

# Configure Celery
celery.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'app.tasks.price_tasks.update_single_product_price': {'queue': 'price_updates'},
        'app.tasks.price_tasks.update_all_prices': {'queue': 'batch_updates'},
        'app.tasks.price_tasks.update_tracked_products_prices': {'queue': 'tracked_updates'},
    },
    # Schedule periodic tasks
    beat_schedule={
        'update-tracked-products-every-hour': {
            'task': 'app.tasks.price_tasks.update_tracked_products_prices',
            'schedule': 3600.0,  # Every hour
        },
        'update-all-prices-daily': {
            'task': 'app.tasks.price_tasks.update_all_prices',
            'schedule': 86400.0,  # Every 24 hours
            'kwargs': {'limit': 100}  # Limit to 100 products per day
        },
    },
)

@celery.task(bind=True, max_retries=3)
def update_single_product_price(self, product_retailer_id):
    """
    Update price for a single product-retailer combination
    
    Args:
        product_retailer_id: ID of the ProductRetailer to update
        
    Returns:
        Dict containing update results
    """
    try:
        app = create_app()
        with app.app_context():
            price_service = PriceUpdateService()
            result = price_service.update_product_price(product_retailer_id)
            
            if not result.get("success"):
                # Retry on failure with exponential backoff
                if self.request.retries < self.max_retries:
                    logger.warning(f"Retrying price update for ProductRetailer {product_retailer_id}, "
                                 f"attempt {self.request.retries + 1}")
                    raise self.retry(countdown=60 * (2 ** self.request.retries))
                else:
                    logger.error(f"Failed to update price for ProductRetailer {product_retailer_id} "
                               f"after {self.max_retries} retries")
            
            return result
            
    except Exception as e:
        logger.error(f"Error in update_single_product_price task: {str(e)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        return {"success": False, "error": str(e), "product_retailer_id": product_retailer_id}

@celery.task(bind=True)
def update_all_prices(self, limit=None):
    """
    Update prices for all products or a limited number
    
    Args:
        limit: Maximum number of products to update (None for all)
        
    Returns:
        Dict containing batch update results
    """
    try:
        app = create_app()
        with app.app_context():
            price_service = PriceUpdateService()
            result = price_service.update_all_prices(limit=limit)
            
            logger.info(f"Batch price update completed: {result.get('successful_updates', 0)} successful, "
                       f"{result.get('failed_updates', 0)} failed")
            
            return result
            
    except Exception as e:
        logger.error(f"Error in update_all_prices task: {str(e)}")
        return {"success": False, "error": str(e)}

@celery.task(bind=True)
def update_tracked_products_prices(self, user_id=None):
    """
    Update prices for tracked products
    
    Args:
        user_id: Optional user ID to update only their tracked products
        
    Returns:
        Dict containing update results
    """
    try:
        app = create_app()
        with app.app_context():
            price_service = PriceUpdateService()
            result = price_service.update_prices_for_tracked_products(user_id)
            
            logger.info(f"Tracked products price update completed: {result.get('successful_updates', 0)} successful, "
                       f"{result.get('failed_updates', 0)} failed")
            
            # Send notifications for significant price changes
            if result.get('price_changes', 0) > 0:
                send_price_change_notifications.delay(result.get('updates', []))
            
            return result
            
    except Exception as e:
        logger.error(f"Error in update_tracked_products_prices task: {str(e)}")
        return {"success": False, "error": str(e)}

@celery.task(bind=True)
def send_price_change_notifications(self, price_updates):
    """
    Send notifications for price changes
    
    Args:
        price_updates: List of price update results
    """
    try:
        app = create_app()
        with app.app_context():
            from app.services.notification_service import NotificationService
            
            notification_service = NotificationService()
            
            for update in price_updates:
                if update.get('success') and update.get('price_changed'):
                    # Send notification for this price change
                    notification_service.send_price_change_notification(
                        product_retailer_id=update.get('product_retailer_id'),
                        old_price=update.get('old_price'),
                        new_price=update.get('new_price')
                    )
            
            logger.info(f"Sent notifications for {len(price_updates)} price changes")
            
    except Exception as e:
        logger.error(f"Error sending price change notifications: {str(e)}")

@celery.task(bind=True)
def cleanup_old_price_history(self, days_to_keep=90):
    """
    Clean up old price history entries
    
    Args:
        days_to_keep: Number of days of price history to keep
    """
    try:
        app = create_app()
        with app.app_context():
            from app.models.product import PriceHistory
            from datetime import datetime, timezone, timedelta
            from app.extensions.extensions import db
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
            
            deleted_count = PriceHistory.query.filter(
                PriceHistory.timestamp < cutoff_date
            ).delete()
            
            db.session.commit()
            
            logger.info(f"Cleaned up {deleted_count} old price history entries")
            return {"deleted_count": deleted_count}
            
    except Exception as e:
        logger.error(f"Error cleaning up price history: {str(e)}")
        return {"success": False, "error": str(e)}

@celery.task(bind=True)
def generate_scraping_report(self):
    """
    Generate a report on scraping performance
    
    Returns:
        Dict containing scraping statistics
    """
    try:
        app = create_app()
        with app.app_context():
            price_service = PriceUpdateService()
            stats = price_service.get_scraping_stats()
            
            logger.info(f"Scraping report: {stats}")
            return stats
            
    except Exception as e:
        logger.error(f"Error generating scraping report: {str(e)}")
        return {"success": False, "error": str(e)}

# Utility functions for manual task execution
def schedule_price_update(product_retailer_id):
    """Schedule a price update for a specific product-retailer"""
    return update_single_product_price.delay(product_retailer_id)

def schedule_batch_update(limit=None):
    """Schedule a batch price update"""
    return update_all_prices.delay(limit=limit)

def schedule_tracked_products_update(user_id=None):
    """Schedule price updates for tracked products"""
    return update_tracked_products_prices.delay(user_id=user_id)

# Task monitoring functions
def get_task_status(task_id):
    """Get the status of a Celery task"""
    result = celery.AsyncResult(task_id)
    return {
        'task_id': task_id,
        'status': result.status,
        'result': result.result if result.ready() else None,
        'traceback': result.traceback if result.failed() else None
    }

def get_active_tasks():
    """Get list of active tasks"""
    inspect = celery.control.inspect()
    active_tasks = inspect.active()
    return active_tasks

def cancel_task(task_id):
    """Cancel a running task"""
    celery.control.revoke(task_id, terminate=True)
    return {"cancelled": task_id}
