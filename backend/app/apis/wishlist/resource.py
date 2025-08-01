"""
Wishlist API endpoints
"""
import logging
from flask import request, jsonify
from app.apis.wishlist import wishlist
from app.services.wishlist_service import WishlistService
from app.utils.request_utils import get_request_data

# Set up logger
logger = logging.getLogger(__name__)


@wishlist.route('/<user_id>/wishlists', methods=['GET'])
def get_user_wishlists(user_id):
    """
    Get all wishlists for a user
    """
    try:
        wishlists = WishlistService.get_user_wishlists(user_id)
        return jsonify(wishlists), 200
        
    except Exception as e:
        logger.error(f"Error getting user wishlists: {str(e)}")
        return jsonify({'error': str(e)}), 500


@wishlist.route('/<user_id>/wishlists', methods=['POST'])
def create_wishlist(user_id):
    """
    Create a new wishlist for a user
    """
    try:
        data = get_request_data(request)
        name = data.get('name', 'My Wishlist')
        description = data.get('description', '')
        is_default = data.get('is_default', False)
        
        wishlist_data = WishlistService.create_wishlist(
            user_id=user_id,
            name=name,
            description=description,
            is_default=is_default
        )
        
        return jsonify(wishlist_data), 201
        
    except Exception as e:
        logger.error(f"Error creating wishlist: {str(e)}")
        return jsonify({'error': str(e)}), 500


@wishlist.route('/<user_id>/wishlists/<int:wishlist_id>', methods=['GET'])
def get_wishlist_details(user_id, wishlist_id):
    """
    Get detailed information about a specific wishlist
    """
    try:
        wishlist_data = WishlistService.get_wishlist_details(user_id, wishlist_id)
        return jsonify(wishlist_data), 200
        
    except Exception as e:
        logger.error(f"Error getting wishlist details: {str(e)}")
        return jsonify({'error': str(e)}), 500


@wishlist.route('/<user_id>/wishlists/<int:wishlist_id>/items', methods=['POST'])
def add_item_to_wishlist(user_id, wishlist_id):
    """
    Add a product to a wishlist
    Supports both database products (int IDs) and scraped products (string IDs)
    """
    try:
        data = get_request_data(request)
        product_id = data.get('product_id')
        notes = data.get('notes', '')
        priority = data.get('priority', 'medium')
        target_price = data.get('target_price')
        
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400
        
        wishlist_item = WishlistService.add_item_to_wishlist(
            user_id=user_id,
            wishlist_id=wishlist_id,
            product_id=product_id,
            notes=notes,
            priority=priority,
            target_price=target_price
        )
        
        return jsonify(wishlist_item), 201
        
    except Exception as e:
        logger.error(f"Error adding item to wishlist: {str(e)}")
        return jsonify({'error': str(e)}), 500


@wishlist.route('/<user_id>/wishlists/<int:wishlist_id>/items/<int:item_id>', methods=['DELETE'])
def remove_item_from_wishlist(user_id, wishlist_id, item_id):
    """
    Remove an item from a wishlist
    """
    try:
        result = WishlistService.remove_item_from_wishlist(user_id, wishlist_id, item_id)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error removing item from wishlist: {str(e)}")
        return jsonify({'error': str(e)}), 500


@wishlist.route('/<user_id>/wishlists/<int:wishlist_id>/items/<int:item_id>', methods=['PUT'])
def update_wishlist_item(user_id, wishlist_id, item_id):
    """
    Update a wishlist item
    """
    try:
        data = get_request_data(request)
        
        result = WishlistService.update_wishlist_item(
            user_id=user_id,
            wishlist_id=wishlist_id,
            item_id=item_id,
            notes=data.get('notes'),
            priority=data.get('priority'),
            target_price=data.get('target_price')
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error updating wishlist item: {str(e)}")
        return jsonify({'error': str(e)}), 500


@wishlist.route('/<user_id>/items', methods=['GET'])
def get_all_wishlist_items(user_id):
    """
    Get all wishlist items for a user across all wishlists
    """
    try:
        items = WishlistService.get_all_user_wishlist_items(user_id)
        return jsonify(items), 200
        
    except Exception as e:
        logger.error(f"Error getting all wishlist items: {str(e)}")
        return jsonify({'error': str(e)}), 500


@wishlist.route('/<user_id>/items/quick-add', methods=['POST'])
def quick_add_to_wishlist(user_id):
    """
    Quick add a product to the user's default wishlist
    Creates a default wishlist if none exists
    """
    try:
        data = get_request_data(request)
        product_id = data.get('product_id')
        notes = data.get('notes', '')
        priority = data.get('priority', 'medium')
        target_price = data.get('target_price')
        
        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400
        
        wishlist_item = WishlistService.quick_add_to_wishlist(
            user_id=user_id,
            product_id=product_id,
            notes=notes,
            priority=priority,
            target_price=target_price
        )
        
        return jsonify(wishlist_item), 201
        
    except Exception as e:
        logger.error(f"Error quick adding to wishlist: {str(e)}")
        return jsonify({'error': str(e)}), 500
