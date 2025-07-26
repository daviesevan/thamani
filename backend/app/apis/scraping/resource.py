"""
Web scraping API endpoints for testing and managing price updates
"""
import logging
from flask import jsonify, request, Blueprint
from app.services.price_update_service import PriceUpdateService
from app.services.scraping_service import ScrapingService
from app.models.product import ProductRetailer
from app.utils.request_utils import get_request_data

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
scraping = Blueprint('scraping', __name__)

@scraping.route('/test/<int:product_retailer_id>', methods=['POST'])
def test_scrape_product(product_retailer_id):
    """
    Test scraping for a specific product-retailer combination
    """
    try:
        product_retailer = ProductRetailer.query.get(product_retailer_id)
        if not product_retailer:
            return jsonify({'error': 'ProductRetailer not found'}), 404
        
        scraping_service = ScrapingService()
        result = scraping_service.scrape_product_price(product_retailer)
        
        return jsonify({
            'product_retailer_id': product_retailer_id,
            'product_name': product_retailer.product.name,
            'retailer_name': product_retailer.retailer.name,
            'url': product_retailer.retailer_product_url,
            'scraping_result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error testing scrape: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scraping.route('/update/<int:product_retailer_id>', methods=['POST'])
def update_single_price(product_retailer_id):
    """
    Update price for a single product-retailer combination
    """
    try:
        price_service = PriceUpdateService()
        result = price_service.update_product_price(product_retailer_id)
        
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"Error updating price: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scraping.route('/update/batch', methods=['POST'])
def update_batch_prices():
    """
    Update prices for multiple products
    """
    try:
        data = get_request_data(request)
        limit = data.get('limit', 10)  # Default to 10 products
        
        if limit > 100:  # Prevent too large batches
            return jsonify({'error': 'Limit cannot exceed 100'}), 400
        
        price_service = PriceUpdateService()
        result = price_service.update_all_prices(limit=limit)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in batch update: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scraping.route('/update/tracked', methods=['POST'])
def update_tracked_prices():
    """
    Update prices for tracked products
    """
    try:
        data = get_request_data(request)
        user_id = data.get('user_id')  # Optional: update for specific user
        
        price_service = PriceUpdateService()
        result = price_service.update_prices_for_tracked_products(user_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error updating tracked prices: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scraping.route('/stats', methods=['GET'])
def get_scraping_stats():
    """
    Get scraping performance statistics
    """
    try:
        price_service = PriceUpdateService()
        stats = price_service.get_scraping_stats()
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting scraping stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scraping.route('/stale', methods=['GET'])
def get_stale_products():
    """
    Get products that need price updates
    """
    try:
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        price_service = PriceUpdateService()
        stale_products = price_service.get_stale_products(hours=hours)
        
        # Limit results
        if limit:
            stale_products = stale_products[:limit]
        
        result = []
        for pr in stale_products:
            result.append({
                'product_retailer_id': pr.product_retailer_id,
                'product_name': pr.product.name,
                'retailer_name': pr.retailer.name,
                'last_updated': pr.last_updated.isoformat() if pr.last_updated else None,
                'last_scrape_attempt': pr.last_scrape_attempt.isoformat() if pr.last_scrape_attempt else None,
                'scraping_error': pr.scraping_error,
                'current_price': float(pr.current_price),
                'url': pr.retailer_product_url
            })
        
        return jsonify({
            'stale_products': result,
            'total_count': len(result),
            'hours_threshold': hours
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stale products: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scraping.route('/errors', methods=['GET'])
def get_scraping_errors():
    """
    Get products with scraping errors
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        
        products_with_errors = ProductRetailer.query.filter(
            ProductRetailer.scraping_error.isnot(None)
        ).order_by(ProductRetailer.last_scrape_attempt.desc()).limit(limit).all()
        
        result = []
        for pr in products_with_errors:
            result.append({
                'product_retailer_id': pr.product_retailer_id,
                'product_name': pr.product.name,
                'retailer_name': pr.retailer.name,
                'scraping_error': pr.scraping_error,
                'last_scrape_attempt': pr.last_scrape_attempt.isoformat() if pr.last_scrape_attempt else None,
                'scrape_count': pr.scrape_count,
                'url': pr.retailer_product_url
            })
        
        return jsonify({
            'products_with_errors': result,
            'total_count': len(result)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting scraping errors: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scraping.route('/test/url', methods=['POST'])
def test_scrape_url():
    """
    Test scraping a specific URL
    """
    try:
        data = get_request_data(request)
        url = data.get('url')
        retailer_name = data.get('retailer_name', 'generic')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Create a temporary ProductRetailer-like object for testing
        class TempProductRetailer:
            def __init__(self, url, retailer_name):
                self.retailer_product_url = url
                self.retailer = type('obj', (object,), {'name': retailer_name})()
        
        temp_pr = TempProductRetailer(url, retailer_name)
        
        scraping_service = ScrapingService()
        result = scraping_service.scrape_product_price(temp_pr)
        
        return jsonify({
            'url': url,
            'retailer_name': retailer_name,
            'scraping_result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error testing URL scrape: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scraping.route('/config', methods=['GET'])
def get_scraping_config():
    """
    Get current scraping configuration
    """
    try:
        from flask import current_app
        
        config = {
            'scraping_enabled': current_app.config.get('SCRAPING_ENABLED', True),
            'scraping_timeout': current_app.config.get('SCRAPING_TIMEOUT', 10),
            'scraping_delay_min': current_app.config.get('SCRAPING_DELAY_MIN', 1),
            'scraping_delay_max': current_app.config.get('SCRAPING_DELAY_MAX', 3),
            'scraping_max_retries': current_app.config.get('SCRAPING_MAX_RETRIES', 3),
            'scraping_batch_size': current_app.config.get('SCRAPING_BATCH_SIZE', 50),
            'chrome_headless': current_app.config.get('CHROME_HEADLESS', True)
        }
        
        return jsonify(config), 200
        
    except Exception as e:
        logger.error(f"Error getting scraping config: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scraping.route('/retailers/test', methods=['GET'])
def test_all_retailers():
    """
    Test scraping for one product from each retailer
    """
    try:
        from sqlalchemy import func
        
        # Get one product from each retailer
        test_products = ProductRetailer.query.join(
            ProductRetailer.retailer
        ).filter(
            ProductRetailer.retailer_product_url.isnot(None)
        ).group_by(ProductRetailer.retailer_id).all()
        
        scraping_service = ScrapingService()
        results = []
        
        for pr in test_products:
            # Add delay between requests
            scraping_service.add_random_delay(2, 4)
            
            result = scraping_service.scrape_product_price(pr)
            results.append({
                'retailer_name': pr.retailer.name,
                'product_name': pr.product.name,
                'url': pr.retailer_product_url,
                'scraping_result': result
            })
        
        return jsonify({
            'test_results': results,
            'total_retailers_tested': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error testing all retailers: {str(e)}")
        return jsonify({'error': str(e)}), 500
