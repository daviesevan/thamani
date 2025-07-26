/**
 * Product API service functions
 */
import api from "./api";

/**
 * Product Search and Discovery
 */
export const productService = {
  // Search products with filters using real-time web scraping
  searchProducts: async (params = {}) => {
    try {
      const queryParams = new URLSearchParams();

      if (params.query) queryParams.append("q", params.query);
      if (params.categoryId)
        queryParams.append("category_id", params.categoryId);
      if (params.brand) queryParams.append("brand", params.brand);
      if (params.minPrice) queryParams.append("min_price", params.minPrice);
      if (params.maxPrice) queryParams.append("max_price", params.maxPrice);
      if (params.limit) queryParams.append("limit", params.limit);
      if (params.offset) queryParams.append("offset", params.offset);

      // Force web scraping for queries with actual search terms
      if (params.query && params.query.trim()) {
        queryParams.append("use_web_scraping", "true");
      }

      console.log("🔍 Searching with params:", Object.fromEntries(queryParams));

      const response = await api.get(
        `/products/search?${queryParams.toString()}`
      );

      console.log("📊 Search results:", {
        total: response.data.total_count,
        source: response.data.source,
        retailers: response.data.retailers_searched,
      });

      return response.data;
    } catch (error) {
      console.error("Error searching products:", error);
      throw error;
    }
  },

  // Get product details
  getProductDetails: async (productId) => {
    try {
      const response = await api.get(`/products/${productId}`);
      return response.data;
    } catch (error) {
      console.error("Error getting product details:", error);
      throw error;
    }
  },

  // Get all categories
  getCategories: async () => {
    try {
      const response = await api.get("/products/categories");
      return response.data;
    } catch (error) {
      console.error("Error getting categories:", error);
      throw error;
    }
  },

  // Get all retailers
  getRetailers: async () => {
    try {
      const response = await api.get("/products/retailers");
      return response.data;
    } catch (error) {
      console.error("Error getting retailers:", error);
      throw error;
    }
  },

  // Get popular products
  getPopularProducts: async (limit = 10) => {
    try {
      const response = await api.get(`/products/popular?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error("Error getting popular products:", error);
      throw error;
    }
  },

  // Quick search for autocomplete
  quickSearch: async (query, limit = 10) => {
    try {
      const response = await api.get(
        `/products/quick-search?q=${encodeURIComponent(query)}&limit=${limit}`
      );
      return response.data;
    } catch (error) {
      console.error("Error in quick search:", error);
      throw error;
    }
  },

  // Get product recommendations
  getRecommendations: async (userId, limit = 10) => {
    try {
      const response = await api.get(
        `/products/recommendations/${userId}?limit=${limit}`
      );
      return response.data;
    } catch (error) {
      console.error("Error getting recommendations:", error);
      throw error;
    }
  },

  // Get brands
  getBrands: async () => {
    try {
      const response = await api.get("/products/brands");
      return response.data;
    } catch (error) {
      console.error("Error getting brands:", error);
      throw error;
    }
  },

  // Get price ranges
  getPriceRanges: async () => {
    try {
      const response = await api.get("/products/price-ranges");
      return response.data;
    } catch (error) {
      console.error("Error getting price ranges:", error);
      throw error;
    }
  },
};

/**
 * Product Tracking Service
 */
export const trackingService = {
  // Get user's tracked products
  getTrackedProducts: async (userId, includeArchived = false) => {
    try {
      const params = includeArchived ? "?include_archived=true" : "";
      const response = await api.get(`/tracking/${userId}/products${params}`);
      return response.data;
    } catch (error) {
      console.error("Error getting tracked products:", error);
      throw error;
    }
  },

  // Add product to tracking
  addTrackedProduct: async (userId, productId, trackingData = {}) => {
    try {
      const response = await api.post(
        `/tracking/${userId}/products/${productId}`,
        trackingData
      );
      return response.data;
    } catch (error) {
      console.error("Error adding tracked product:", error);
      throw error;
    }
  },

  // Get tracked product details
  getTrackedProductDetails: async (userId, productId) => {
    try {
      const response = await api.get(
        `/tracking/${userId}/products/${productId}`
      );
      return response.data;
    } catch (error) {
      console.error("Error getting tracked product details:", error);
      throw error;
    }
  },

  // Update tracked product
  updateTrackedProduct: async (userId, productId, updateData) => {
    try {
      const response = await api.put(
        `/tracking/${userId}/products/${productId}`,
        updateData
      );
      return response.data;
    } catch (error) {
      console.error("Error updating tracked product:", error);
      throw error;
    }
  },

  // Remove product from tracking
  removeTrackedProduct: async (userId, productId) => {
    try {
      const response = await api.delete(
        `/tracking/${userId}/products/${productId}`
      );
      return response.data;
    } catch (error) {
      console.error("Error removing tracked product:", error);
      throw error;
    }
  },

  // Get tracking summary
  getTrackingSummary: async (userId) => {
    try {
      const response = await api.get(`/tracking/${userId}/summary`);
      return response.data;
    } catch (error) {
      console.error("Error getting tracking summary:", error);
      throw error;
    }
  },

  // Bulk add products to tracking
  bulkAddTrackedProducts: async (userId, productIds, trackingData = {}) => {
    try {
      const response = await api.post(`/tracking/${userId}/products/bulk`, {
        product_ids: productIds,
        ...trackingData,
      });
      return response.data;
    } catch (error) {
      console.error("Error bulk adding tracked products:", error);
      throw error;
    }
  },

  // Bulk remove products from tracking
  bulkRemoveTrackedProducts: async (userId, productIds) => {
    try {
      const response = await api.delete(`/tracking/${userId}/products/bulk`, {
        data: { product_ids: productIds },
      });
      return response.data;
    } catch (error) {
      console.error("Error bulk removing tracked products:", error);
      throw error;
    }
  },
};

/**
 * Utility functions for product data
 */
export const productUtils = {
  // Format price with currency
  formatPrice: (price, currency = "KES") => {
    if (price === null || price === undefined) return "N/A";
    return new Intl.NumberFormat("en-KE", {
      style: "currency",
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  },

  // Calculate savings
  calculateSavings: (originalPrice, currentPrice) => {
    if (!originalPrice || !currentPrice) return 0;
    return originalPrice - currentPrice;
  },

  // Calculate savings percentage
  calculateSavingsPercentage: (originalPrice, currentPrice) => {
    if (!originalPrice || !currentPrice) return 0;
    return Math.round(((originalPrice - currentPrice) / originalPrice) * 100);
  },

  // Get price status (drop, increase, stable)
  getPriceStatus: (targetPrice, currentPrice, threshold = 5) => {
    if (!targetPrice || !currentPrice) return "unknown";

    const percentageDiff = ((currentPrice - targetPrice) / targetPrice) * 100;

    if (percentageDiff <= -threshold) return "drop";
    if (percentageDiff >= threshold) return "increase";
    return "stable";
  },

  // Get lowest price from retailers
  getLowestPrice: (retailers) => {
    if (!retailers || retailers.length === 0) return null;

    const inStockRetailers = retailers.filter((r) => r.in_stock);
    if (inStockRetailers.length === 0) return null;

    return Math.min(...inStockRetailers.map((r) => r.current_price));
  },

  // Get highest price from retailers
  getHighestPrice: (retailers) => {
    if (!retailers || retailers.length === 0) return null;

    const inStockRetailers = retailers.filter((r) => r.in_stock);
    if (inStockRetailers.length === 0) return null;

    return Math.max(...inStockRetailers.map((r) => r.current_price));
  },

  // Get best deal (lowest price retailer)
  getBestDeal: (retailers) => {
    if (!retailers || retailers.length === 0) return null;

    const inStockRetailers = retailers.filter((r) => r.in_stock);
    if (inStockRetailers.length === 0) return null;

    return inStockRetailers.reduce((best, current) =>
      current.current_price < best.current_price ? current : best
    );
  },
};
