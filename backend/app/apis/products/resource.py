"""
Product API endpoints for search and discovery
"""
import logging
from flask import jsonify, request, Blueprint
from app.services.product_service import ProductService
from app.utils.request_utils import get_request_data
from app.extensions.extensions import db

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
products = Blueprint('products', __name__)


@products.route('/search', methods=['GET'])
def search_products():
    """
    Search for products using real-time web scraping from retailer websites
    """
    try:
        # Get query parameters
        query = request.args.get('q', '').strip()
        category_id = request.args.get('category_id', type=int)
        brand = request.args.get('brand', '').strip()
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        limit = min(request.args.get('limit', 20, type=int), 100)  # Max 100 results
        offset = max(request.args.get('offset', 0, type=int), 0)

        # Check if web scraping should be used (default: True for queries, False for empty queries)
        use_web_scraping = request.args.get('use_web_scraping', 'true' if query else 'false').lower() == 'true'

        # Validate price range
        if min_price is not None and max_price is not None and min_price > max_price:
            return jsonify({'error': 'min_price cannot be greater than max_price'}), 400

        logger.info(f"Product search: query='{query}', web_scraping={use_web_scraping}")

        results = ProductService.search_products(
            query=query,
            category_id=category_id,
            brand=brand or None,
            min_price=min_price,
            max_price=max_price,
            limit=limit,
            offset=offset,
            use_web_scraping=use_web_scraping
        )

        logger.info(f"Search completed: {results.get('total_count', 0)} products from {results.get('source', 'unknown')}")

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        return jsonify({'error': str(e)}), 500

@products.route('/search/web-scraping', methods=['GET'])
def search_products_web_scraping():
    """
    Force web scraping search for testing
    """
    try:
        query = request.args.get('q', '').strip()
        limit = min(request.args.get('limit', 5, type=int), 20)

        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400

        logger.info(f"Force web scraping search: {query}")

        results = ProductService.search_products(
            query=query,
            limit=limit,
            offset=0,
            use_web_scraping=True
        )

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Error in web scraping search: {str(e)}")
        return jsonify({'error': str(e)}), 500


@products.route('/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    """
    Get detailed information about a specific product
    """
    try:
        product_details = ProductService.get_product_details(product_id)
        return jsonify(product_details), 200
        
    except Exception as e:
        logger.error(f"Error getting product details: {str(e)}")
        return jsonify({'error': str(e)}), 500


@products.route('/categories', methods=['GET'])
def get_categories():
    """
    Get all product categories with hierarchy
    """
    try:
        categories = ProductService.get_categories()
        return jsonify({
            "categories": categories,
            "total_count": len(categories)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return jsonify({'error': str(e)}), 500


@products.route('/retailers', methods=['GET'])
def get_retailers():
    """
    Get all active retailers
    """
    try:
        retailers = ProductService.get_retailers()
        return jsonify({
            "retailers": retailers,
            "total_count": len(retailers)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting retailers: {str(e)}")
        return jsonify({'error': str(e)}), 500


@products.route('/popular', methods=['GET'])
def get_popular_products():
    """
    Get popular/trending products
    """
    try:
        limit = min(request.args.get('limit', 10, type=int), 50)  # Max 50 results
        
        popular_products = ProductService.get_popular_products(limit=limit)
        return jsonify({
            "products": popular_products,
            "total_count": len(popular_products)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting popular products: {str(e)}")
        return jsonify({'error': str(e)}), 500


@products.route('/recommendations/<user_id>', methods=['GET'])
def get_product_recommendations(user_id):
    """
    Get personalized product recommendations for a user
    (For now, returns popular products - can be enhanced with ML later)
    """
    try:
        limit = min(request.args.get('limit', 10, type=int), 20)
        
        # For now, just return popular products
        # TODO: Implement personalized recommendations based on user's tracking history
        recommendations = ProductService.get_popular_products(limit=limit)
        
        return jsonify({
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "recommendation_type": "popular"  # Can be "personalized", "similar", etc.
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500


@products.route('/brands', methods=['GET'])
def get_brands():
    """
    Get all available brands
    """
    try:
        from app.models.product import Product
        from sqlalchemy import func
        
        # Get distinct brands with product counts
        brands_query = db.session.query(
            Product.brand,
            func.count(Product.product_id).label('product_count')
        ).filter(
            Product.brand.isnot(None),
            Product.brand != ''
        ).group_by(Product.brand).order_by(Product.brand).all()
        
        brands = []
        for brand, count in brands_query:
            brands.append({
                "name": brand,
                "product_count": count
            })
        
        return jsonify({
            "brands": brands,
            "total_count": len(brands)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting brands: {str(e)}")
        return jsonify({'error': str(e)}), 500


@products.route('/price-ranges', methods=['GET'])
def get_price_ranges():
    """
    Get price range statistics for filtering
    """
    try:
        from app.models.product import ProductRetailer
        from sqlalchemy import func
        
        # Get price statistics
        price_stats = db.session.query(
            func.min(ProductRetailer.current_price).label('min_price'),
            func.max(ProductRetailer.current_price).label('max_price'),
            func.avg(ProductRetailer.current_price).label('avg_price')
        ).filter(ProductRetailer.in_stock == True).first()
        
        # Define common price ranges
        price_ranges = [
            {"label": "Under KES 10,000", "min": 0, "max": 10000},
            {"label": "KES 10,000 - 25,000", "min": 10000, "max": 25000},
            {"label": "KES 25,000 - 50,000", "min": 25000, "max": 50000},
            {"label": "KES 50,000 - 100,000", "min": 50000, "max": 100000},
            {"label": "Over KES 100,000", "min": 100000, "max": None}
        ]
        
        return jsonify({
            "price_statistics": {
                "min_price": float(price_stats.min_price) if price_stats.min_price else 0,
                "max_price": float(price_stats.max_price) if price_stats.max_price else 0,
                "avg_price": round(float(price_stats.avg_price), 2) if price_stats.avg_price else 0,
                "currency": "KES"
            },
            "price_ranges": price_ranges
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting price ranges: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Quick search endpoint for autocomplete
@products.route('/quick-search', methods=['GET'])
def quick_search():
    """
    Quick search for product names (for autocomplete)
    """
    try:
        query = request.args.get('q', '').strip()
        limit = min(request.args.get('limit', 10, type=int), 20)
        
        if not query or len(query) < 2:
            return jsonify({"suggestions": []}), 200
        
        from app.models.product import Product
        from sqlalchemy import or_
        
        # Search in product names and brands
        products = Product.query.filter(
            or_(
                Product.name.ilike(f'%{query}%'),
                Product.brand.ilike(f'%{query}%')
            )
        ).limit(limit).all()
        
        suggestions = []
        for product in products:
            suggestions.append({
                "product_id": product.product_id,
                "name": product.name,
                "brand": product.brand,
                "image_url": product.image_url
            })
        
        return jsonify({"suggestions": suggestions}), 200
        
    except Exception as e:
        logger.error(f"Error in quick search: {str(e)}")
        return jsonify({'error': str(e)}), 500
