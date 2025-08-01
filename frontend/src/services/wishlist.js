import api from './api';

/**
 * Wishlist service for managing user wishlists and wishlist items
 */
class WishlistService {
  /**
   * Get all wishlists for a user
   * @param {string} userId - User ID
   * @returns {Promise<Array>} Array of user's wishlists
   */
  async getUserWishlists(userId) {
    try {
      const response = await api.get(`/wishlist/${userId}/wishlists`);
      return response.data;
    } catch (error) {
      console.error('Error getting user wishlists:', error);
      throw error;
    }
  }

  /**
   * Create a new wishlist
   * @param {string} userId - User ID
   * @param {Object} wishlistData - Wishlist data
   * @param {string} wishlistData.name - Wishlist name
   * @param {string} wishlistData.description - Wishlist description
   * @param {boolean} wishlistData.is_default - Whether this is the default wishlist
   * @returns {Promise<Object>} Created wishlist data
   */
  async createWishlist(userId, wishlistData) {
    try {
      const response = await api.post(`/wishlist/${userId}/wishlists`, wishlistData);
      return response.data;
    } catch (error) {
      console.error('Error creating wishlist:', error);
      throw error;
    }
  }

  /**
   * Get detailed information about a specific wishlist
   * @param {string} userId - User ID
   * @param {number} wishlistId - Wishlist ID
   * @returns {Promise<Object>} Detailed wishlist information with items
   */
  async getWishlistDetails(userId, wishlistId) {
    try {
      const response = await api.get(`/wishlist/${userId}/wishlists/${wishlistId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting wishlist details:', error);
      throw error;
    }
  }

  /**
   * Add a product to a wishlist
   * @param {string} userId - User ID
   * @param {number} wishlistId - Wishlist ID
   * @param {Object} itemData - Item data
   * @param {string|number} itemData.product_id - Product ID (supports both database and scraped products)
   * @param {string} itemData.notes - User notes
   * @param {string} itemData.priority - Priority level (low, medium, high)
   * @param {number} itemData.target_price - Target price for the product
   * @returns {Promise<Object>} Created wishlist item data
   */
  async addItemToWishlist(userId, wishlistId, itemData) {
    try {
      const response = await api.post(`/wishlist/${userId}/wishlists/${wishlistId}/items`, itemData);
      return response.data;
    } catch (error) {
      console.error('Error adding item to wishlist:', error);
      throw error;
    }
  }

  /**
   * Remove an item from a wishlist
   * @param {string} userId - User ID
   * @param {number} wishlistId - Wishlist ID
   * @param {number} itemId - Wishlist item ID
   * @returns {Promise<Object>} Removal confirmation
   */
  async removeItemFromWishlist(userId, wishlistId, itemId) {
    try {
      const response = await api.delete(`/wishlist/${userId}/wishlists/${wishlistId}/items/${itemId}`);
      return response.data;
    } catch (error) {
      console.error('Error removing item from wishlist:', error);
      throw error;
    }
  }

  /**
   * Update a wishlist item
   * @param {string} userId - User ID
   * @param {number} wishlistId - Wishlist ID
   * @param {number} itemId - Wishlist item ID
   * @param {Object} updateData - Update data
   * @param {string} updateData.notes - Updated notes
   * @param {string} updateData.priority - Updated priority
   * @param {number} updateData.target_price - Updated target price
   * @returns {Promise<Object>} Updated wishlist item data
   */
  async updateWishlistItem(userId, wishlistId, itemId, updateData) {
    try {
      const response = await api.put(`/wishlist/${userId}/wishlists/${wishlistId}/items/${itemId}`, updateData);
      return response.data;
    } catch (error) {
      console.error('Error updating wishlist item:', error);
      throw error;
    }
  }

  /**
   * Get all wishlist items for a user across all wishlists
   * @param {string} userId - User ID
   * @returns {Promise<Array>} Array of all user's wishlist items
   */
  async getAllWishlistItems(userId) {
    try {
      const response = await api.get(`/wishlist/${userId}/items`);
      return response.data;
    } catch (error) {
      console.error('Error getting all wishlist items:', error);
      throw error;
    }
  }

  /**
   * Quick add a product to the user's default wishlist
   * Creates a default wishlist if none exists
   * @param {string} userId - User ID
   * @param {Object} itemData - Item data
   * @param {string|number} itemData.product_id - Product ID (supports both database and scraped products)
   * @param {string} itemData.notes - User notes
   * @param {string} itemData.priority - Priority level (low, medium, high)
   * @param {number} itemData.target_price - Target price for the product
   * @returns {Promise<Object>} Created wishlist item data
   */
  async quickAddToWishlist(userId, itemData) {
    try {
      const response = await api.post(`/wishlist/${userId}/items/quick-add`, itemData);
      return response.data;
    } catch (error) {
      console.error('Error quick adding to wishlist:', error);
      throw error;
    }
  }

  /**
   * Check if a product is in any of the user's wishlists
   * @param {string} userId - User ID
   * @param {string|number} productId - Product ID
   * @returns {Promise<boolean>} True if product is in wishlist
   */
  async isProductInWishlist(userId, productId) {
    try {
      const items = await this.getAllWishlistItems(userId);
      return items.some(item => 
        item.product_id === productId || 
        item.original_scraped_id === productId
      );
    } catch (error) {
      console.error('Error checking if product is in wishlist:', error);
      return false;
    }
  }

  /**
   * Get wishlist item for a specific product
   * @param {string} userId - User ID
   * @param {string|number} productId - Product ID
   * @returns {Promise<Object|null>} Wishlist item or null if not found
   */
  async getWishlistItemForProduct(userId, productId) {
    try {
      const items = await this.getAllWishlistItems(userId);
      return items.find(item => 
        item.product_id === productId || 
        item.original_scraped_id === productId
      ) || null;
    } catch (error) {
      console.error('Error getting wishlist item for product:', error);
      return null;
    }
  }
}

export default new WishlistService();
