import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import wishlistService from '../services/wishlist';
import { trackingService } from '../services/products';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Button } from '../components/ui/button';

const Wishlist = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();
  
  const [wishlistItems, setWishlistItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [removingItems, setRemovingItems] = useState(new Set());
  const [trackingItems, setTrackingItems] = useState(new Set());

  useEffect(() => {
    if (user?.user_id) {
      loadWishlistItems();
    } else {
      navigate('/auth/login');
    }
  }, [user?.user_id, navigate]);

  const loadWishlistItems = async () => {
    try {
      const items = await wishlistService.getAllWishlistItems(user.user_id);
      setWishlistItems(items);
    } catch (error) {
      console.error('Error loading wishlist items:', error);
      showToast('Error loading wishlist items', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFromWishlist = async (item) => {
    setRemovingItems(prev => new Set(prev).add(item.wishlist_item_id));
    
    try {
      await wishlistService.removeItemFromWishlist(
        user.user_id,
        item.wishlist_id,
        item.wishlist_item_id
      );
      
      setWishlistItems(prev => 
        prev.filter(i => i.wishlist_item_id !== item.wishlist_item_id)
      );
      
      showToast('Product removed from wishlist', 'success');
    } catch (error) {
      console.error('Error removing from wishlist:', error);
      showToast('Error removing product from wishlist', 'error');
    } finally {
      setRemovingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(item.wishlist_item_id);
        return newSet;
      });
    }
  };

  const handleTrackProduct = async (item) => {
    setTrackingItems(prev => new Set(prev).add(item.wishlist_item_id));
    
    try {
      await trackingService.addTrackedProduct(user.user_id, item.product_id, {
        target_price: item.target_price || item.product?.price_info?.min_price,
        notes: `Tracking ${item.product?.name}`,
        alert_threshold_percent: 10
      });
      
      showToast('Product added to tracking', 'success');
    } catch (error) {
      console.error('Error tracking product:', error);
      showToast('Error adding product to tracking', 'error');
    } finally {
      setTrackingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(item.wishlist_item_id);
        return newSet;
      });
    }
  };

  const handleViewProduct = (productId) => {
    navigate(`/products/${productId}`);
  };

  const formatPrice = (price, currency = 'KES') => {
    if (!price) return 'Price not available';
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const getPriceDisplay = (product) => {
    if (!product?.price_info) return 'Price not available';
    
    const { min_price, max_price } = product.price_info;
    
    if (min_price && max_price && min_price !== max_price) {
      return `${formatPrice(min_price)} - ${formatPrice(max_price)}`;
    } else if (min_price) {
      return formatPrice(min_price);
    }
    
    return 'Price not available';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            My Wishlist
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            {wishlistItems.length} {wishlistItems.length === 1 ? 'item' : 'items'} in your wishlist
          </p>
        </div>

        {/* Wishlist Items */}
        {wishlistItems.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">♡</div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Your wishlist is empty
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Start adding products you love to keep track of them
            </p>
            <Button onClick={() => navigate('/dashboard/search')}>
              Browse Products
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {wishlistItems.map((item) => (
              <div
                key={item.wishlist_item_id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200"
              >
                {/* Product Image */}
                <div className="aspect-w-16 aspect-h-12 bg-gray-200 dark:bg-gray-700">
                  {item.product?.image_url ? (
                    <img
                      src={item.product.image_url}
                      alt={item.product.name}
                      className="w-full h-48 object-cover"
                    />
                  ) : (
                    <div className="w-full h-48 flex items-center justify-center text-gray-400">
                      <span className="text-4xl">📦</span>
                    </div>
                  )}
                </div>

                {/* Product Info */}
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
                    {item.product?.name || 'Product name not available'}
                  </h3>
                  
                  {item.product?.brand && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                      {item.product.brand}
                    </p>
                  )}

                  {/* Price */}
                  <div className="mb-3">
                    <div className="text-lg font-bold text-gray-900 dark:text-white">
                      {getPriceDisplay(item.product)}
                    </div>
                    {item.target_price && (
                      <div className="text-sm text-blue-600 dark:text-blue-400">
                        Target: {formatPrice(item.target_price)}
                      </div>
                    )}
                  </div>

                  {/* Wishlist Info */}
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                    Added {new Date(item.added_at).toLocaleDateString()}
                    {item.priority && item.priority !== 'medium' && (
                      <span className="ml-2 capitalize">• {item.priority} priority</span>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1 text-xs"
                      onClick={() => handleViewProduct(item.product_id)}
                    >
                      View Details
                    </Button>
                    
                    {/* Track Button - only show for database products */}
                    {item.source === 'database' && (
                      <Button
                        variant="default"
                        size="sm"
                        className="flex-1 text-xs"
                        onClick={() => handleTrackProduct(item)}
                        disabled={trackingItems.has(item.wishlist_item_id)}
                      >
                        {trackingItems.has(item.wishlist_item_id) ? 'Adding...' : 'Track Price'}
                      </Button>
                    )}
                    
                    {/* Remove Button */}
                    <Button
                      variant="destructive"
                      size="sm"
                      className="px-2 text-xs"
                      onClick={() => handleRemoveFromWishlist(item)}
                      disabled={removingItems.has(item.wishlist_item_id)}
                      title="Remove from wishlist"
                    >
                      {removingItems.has(item.wishlist_item_id) ? (
                        <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      ) : (
                        '×'
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Wishlist;
