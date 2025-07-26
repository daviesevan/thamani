"""
Product tracking API endpoints
"""
import logging
from flask import jsonify, request, Blueprint
from app.services.product_tracking_service import ProductTrackingService
from app.utils.request_utils import get_request_data

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
tracking = Blueprint('tracking', __name__)


@tracking.route('/<user_id>/products', methods=['GET'])
def get_tracked_products(user_id):
    """
    Get all products tracked by a user
    """
    try:
        include_archived = request.args.get('include_archived', 'false').lower() == 'true'
        
        tracked_products = ProductTrackingService.get_user_tracked_products(
            user_id, include_archived=include_archived
        )
        
        return jsonify({
            "tracked_products": tracked_products,
            "total_count": len(tracked_products)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting tracked products: {str(e)}")
        return jsonify({'error': str(e)}), 500


@tracking.route('/<user_id>/products/<int:product_id>', methods=['POST'])
def add_tracked_product(user_id, product_id):
    """
    Add a product to user's tracking list
    """
    try:
        data = get_request_data(request)
        
        target_price = data.get('target_price')
        notes = data.get('notes')
        alert_threshold_percent = data.get('alert_threshold_percent', 10.0)
        
        # Validate alert threshold
        if not (0 <= alert_threshold_percent <= 100):
            return jsonify({'error': 'Alert threshold must be between 0 and 100'}), 400
        
        result = ProductTrackingService.add_tracked_product(
            user_id=user_id,
            product_id=product_id,
            target_price=target_price,
            notes=notes,
            alert_threshold_percent=alert_threshold_percent
        )
        
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Error adding tracked product: {str(e)}")
        return jsonify({'error': str(e)}), 500


@tracking.route('/<user_id>/products/<int:product_id>', methods=['GET'])
def get_tracked_product_details(user_id, product_id):
    """
    Get detailed information about a tracked product
    """
    try:
        result = ProductTrackingService.get_tracked_product_details(user_id, product_id)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting tracked product details: {str(e)}")
        return jsonify({'error': str(e)}), 500


@tracking.route('/<user_id>/products/<int:product_id>', methods=['PUT'])
def update_tracked_product(user_id, product_id):
    """
    Update tracking settings for a product
    """
    try:
        data = get_request_data(request)
        
        target_price = data.get('target_price')
        notes = data.get('notes')
        alert_threshold_percent = data.get('alert_threshold_percent')
        
        # Validate alert threshold if provided
        if alert_threshold_percent is not None and not (0 <= alert_threshold_percent <= 100):
            return jsonify({'error': 'Alert threshold must be between 0 and 100'}), 400
        
        result = ProductTrackingService.update_tracked_product(
            user_id=user_id,
            product_id=product_id,
            target_price=target_price,
            notes=notes,
            alert_threshold_percent=alert_threshold_percent
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error updating tracked product: {str(e)}")
        return jsonify({'error': str(e)}), 500


@tracking.route('/<user_id>/products/<int:product_id>', methods=['DELETE'])
def remove_tracked_product(user_id, product_id):
    """
    Remove a product from user's tracking list
    """
    try:
        result = ProductTrackingService.remove_tracked_product(user_id, product_id)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error removing tracked product: {str(e)}")
        return jsonify({'error': str(e)}), 500


@tracking.route('/<user_id>/summary', methods=['GET'])
def get_tracking_summary(user_id):
    """
    Get a summary of user's tracking activity
    """
    try:
        tracked_products = ProductTrackingService.get_user_tracked_products(user_id)
        
        # Calculate summary statistics
        total_tracked = len(tracked_products)
        products_with_target_price = sum(1 for p in tracked_products if p['tracking_info']['target_price'])
        
        # Find products with price drops
        price_drops = []
        price_increases = []
        
        for product in tracked_products:
            target_price = product['tracking_info']['target_price']
            lowest_price = product['price_info']['lowest_price']
            
            if target_price and lowest_price:
                if lowest_price <= target_price:
                    price_drops.append({
                        'product_id': product['product']['product_id'],
                        'product_name': product['product']['name'],
                        'target_price': target_price,
                        'current_lowest_price': lowest_price,
                        'savings': target_price - lowest_price
                    })
                elif lowest_price > target_price * 1.1:  # 10% increase threshold
                    price_increases.append({
                        'product_id': product['product']['product_id'],
                        'product_name': product['product']['name'],
                        'target_price': target_price,
                        'current_lowest_price': lowest_price,
                        'increase': lowest_price - target_price
                    })
        
        summary = {
            "total_tracked_products": total_tracked,
            "products_with_target_price": products_with_target_price,
            "price_drops_count": len(price_drops),
            "price_increases_count": len(price_increases),
            "recent_price_drops": price_drops[:5],  # Top 5 price drops
            "recent_price_increases": price_increases[:5]  # Top 5 price increases
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Error getting tracking summary: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Bulk operations
@tracking.route('/<user_id>/products/bulk', methods=['POST'])
def bulk_add_tracked_products(user_id):
    """
    Add multiple products to tracking list
    """
    try:
        data = get_request_data(request)
        product_ids = data.get('product_ids', [])
        
        if not product_ids or not isinstance(product_ids, list):
            return jsonify({'error': 'product_ids must be a non-empty list'}), 400
        
        results = []
        errors = []
        
        for product_id in product_ids:
            try:
                result = ProductTrackingService.add_tracked_product(
                    user_id=user_id,
                    product_id=product_id,
                    target_price=data.get('target_price'),
                    notes=data.get('notes'),
                    alert_threshold_percent=data.get('alert_threshold_percent', 10.0)
                )
                results.append(result)
            except Exception as e:
                errors.append({
                    'product_id': product_id,
                    'error': str(e)
                })
        
        response = {
            'successful_additions': len(results),
            'failed_additions': len(errors),
            'results': results
        }
        
        if errors:
            response['errors'] = errors
        
        status_code = 201 if results else 400
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Error bulk adding tracked products: {str(e)}")
        return jsonify({'error': str(e)}), 500


@tracking.route('/<user_id>/products/bulk', methods=['DELETE'])
def bulk_remove_tracked_products(user_id):
    """
    Remove multiple products from tracking list
    """
    try:
        data = get_request_data(request)
        product_ids = data.get('product_ids', [])
        
        if not product_ids or not isinstance(product_ids, list):
            return jsonify({'error': 'product_ids must be a non-empty list'}), 400
        
        results = []
        errors = []
        
        for product_id in product_ids:
            try:
                result = ProductTrackingService.remove_tracked_product(user_id, product_id)
                results.append(result)
            except Exception as e:
                errors.append({
                    'product_id': product_id,
                    'error': str(e)
                })
        
        response = {
            'successful_removals': len(results),
            'failed_removals': len(errors),
            'results': results
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error bulk removing tracked products: {str(e)}")
        return jsonify({'error': str(e)}), 500
