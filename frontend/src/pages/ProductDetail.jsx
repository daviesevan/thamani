import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { productService, trackingService, productUtils } from '../services/products';
import wishlistService from '../services/wishlist';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import PriceComparison from '../components/products/PriceComparison';
import TrackingModal from '../components/products/TrackingModal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Button } from '../components/ui/button';

const ProductDetail = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isTracked, setIsTracked] = useState(false);
  const [trackingData, setTrackingData] = useState(null);
  const [showTrackingModal, setShowTrackingModal] = useState(false);
  const [trackingLoading, setTrackingLoading] = useState(false);
  const [isInWishlist, setIsInWishlist] = useState(false);
  const [wishlistLoading, setWishlistLoading] = useState(false);

  useEffect(() => {
    if (productId) {
      loadProductDetails();
      if (user?.user_id) {
        checkTrackingStatus();
        checkWishlistStatus();
      }
    }
  }, [productId, user?.user_id]);

  const loadProductDetails = async () => {
    try {
      // Handle both integer and string product IDs
      const productData = await productService.getProductDetails(productId);
      setProduct(productData);
    } catch (error) {
      console.error('Error loading product details:', error);
      showToast('Error loading product details', 'error');
      navigate('/dashboard/search');
    } finally {
      setLoading(false);
    }
  };

  const checkTrackingStatus = async () => {
    try {
      // Skip tracking check for scraped products
      if (product?.source === 'web_scraping') {
        setIsTracked(false);
        setTrackingData(null);
        return;
      }

      const trackedData = await trackingService.getTrackedProductDetails(user.user_id, productId);
      setIsTracked(true);
      setTrackingData(trackedData);
    } catch (error) {
      // Product is not tracked, which is fine
      setIsTracked(false);
      setTrackingData(null);
    }
  };

  const handleTrackProduct = async (trackingInfo) => {
    if (!user) {
      showToast('Please sign in to track products', 'error');
      return;
    }

    // Check if this is a scraped product
    if (product?.source === 'web_scraping') {
      showToast('Price tracking for live scraped products is coming soon! For now, bookmark this product or check back regularly for price updates.', 'info');
      setShowTrackingModal(false);
      return;
    }

    setTrackingLoading(true);
    try {
      await trackingService.addTrackedProduct(user.user_id, productId, trackingInfo);
      setIsTracked(true);
      showToast('Product added to tracking', 'success');
      setShowTrackingModal(false);
      checkTrackingStatus();
    } catch (error) {
      console.error('Error tracking product:', error);
      showToast('Error adding product to tracking', 'error');
    } finally {
      setTrackingLoading(false);
    }
  };

  const handleUpdateTracking = async (updateData) => {
    // Scraped products shouldn't be tracked anyway, but just in case
    if (product?.source === 'web_scraping') {
      setShowTrackingModal(false);
      return;
    }

    setTrackingLoading(true);
    try {
      await trackingService.updateTrackedProduct(user.user_id, productId, updateData);
      showToast('Tracking updated successfully', 'success');
      setShowTrackingModal(false);
      checkTrackingStatus();
    } catch (error) {
      console.error('Error updating tracking:', error);
      showToast('Error updating tracking', 'error');
    } finally {
      setTrackingLoading(false);
    }
  };

  const handleRemoveTracking = async () => {
    // Scraped products shouldn't be tracked anyway, but just in case
    if (product?.source === 'web_scraping') {
      return;
    }

    setTrackingLoading(true);
    try {
      await trackingService.removeTrackedProduct(user.user_id, productId);
      setIsTracked(false);
      setTrackingData(null);
      showToast('Product removed from tracking', 'success');
    } catch (error) {
      console.error('Error removing tracking:', error);
      showToast('Error removing tracking', 'error');
    } finally {
      setTrackingLoading(false);
    }
  };

  const checkWishlistStatus = async () => {
    try {
      const inWishlist = await wishlistService.isProductInWishlist(user.user_id, productId);
      setIsInWishlist(inWishlist);
    } catch (error) {
      console.error('Error checking wishlist status:', error);
    }
  };

  const handleWishlistToggle = async () => {
    if (!user?.user_id) {
      showToast('Please sign in to add products to wishlist', 'error');
      return;
    }

    setWishlistLoading(true);
    try {
      if (isInWishlist) {
        // Remove from wishlist
        const wishlistItem = await wishlistService.getWishlistItemForProduct(user.user_id, productId);
        if (wishlistItem) {
          await wishlistService.removeItemFromWishlist(
            user.user_id,
            wishlistItem.wishlist_id,
            wishlistItem.wishlist_item_id
          );
          setIsInWishlist(false);
          showToast('Product removed from wishlist', 'success');
        }
      } else {
        // Add to wishlist
        const currentPrice = product?.price_info?.min_price ||
          (product?.retailers && product.retailers.length > 0 ? product.retailers[0].current_price : null);

        await wishlistService.quickAddToWishlist(user.user_id, {
          product_id: productId,
          notes: `Added ${product?.name} to wishlist`,
          priority: 'medium',
          target_price: currentPrice
        });
        setIsInWishlist(true);
        showToast('Product added to wishlist', 'success');
      }
    } catch (error) {
      console.error('Error updating wishlist:', error);
      showToast('Error updating wishlist', 'error');
    } finally {
      setWishlistLoading(false);
    }
  };

  const formatPrice = (price) => {
    return productUtils.formatPrice(price, 'KES');
  };

  const getBestDeal = () => {
    if (!product?.retailers) return null;
    return productUtils.getBestDeal(product.retailers);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Product Not Found
          </h2>
          <Button onClick={() => navigate('/dashboard/search')}>
            Browse Products
          </Button>
        </div>
      </div>
    );
  }

  const bestDeal = getBestDeal();

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <nav className="flex items-center space-x-2 text-sm text-muted-foreground">
        <button
          onClick={() => navigate('/dashboard')}
          className="hover:text-foreground transition-colors"
        >
          Dashboard
        </button>
        <span>/</span>
        <button
          onClick={() => navigate('/dashboard/search')}
          className="hover:text-foreground transition-colors"
        >
          Search
        </button>
        <span>/</span>
        {product.category && (
          <>
            <span>{product.category.name}</span>
            <span>/</span>
          </>
        )}
        <span className="text-foreground font-medium">{product.name}</span>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Product Image */}
        <div className="aspect-square bg-background rounded-lg overflow-hidden border border-border">
            {product.image_url ? (
              <img
                src={product.image_url}
                alt={product.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
            ) : null}
            <div className={`w-full h-full flex items-center justify-center bg-muted ${product.image_url ? 'hidden' : 'flex'}`}>
              <svg className="h-24 w-24 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>

          {/* Product Info */}
          <div className="space-y-6">
            {/* Header */}
            <div>
              {product.category && (
                <div className="text-sm text-primary font-medium mb-2">
                  {product.category.name}
                </div>
              )}
              <h1 className="text-3xl font-bold text-foreground mb-2">
                {product.name}
              </h1>
              {product.brand && (
                <p className="text-lg text-muted-foreground">
                  by {product.brand}
                </p>
              )}
            </div>

            {/* Price Info */}
            <div className="bg-background rounded-lg p-6 border border-border">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Price Range</div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {product.price_info.min_price === product.price_info.max_price
                      ? formatPrice(product.price_info.min_price)
                      : `${formatPrice(product.price_info.min_price)} - ${formatPrice(product.price_info.max_price)}`
                    }
                  </div>
                </div>
                {bestDeal && (
                  <div className="text-right">
                    <div className="text-sm text-green-600 dark:text-green-400 font-medium">
                      Best Deal
                    </div>
                    <div className="text-lg font-bold text-green-600 dark:text-green-400">
                      {formatPrice(bestDeal.current_price)}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      at {bestDeal.retailer_name}
                    </div>
                  </div>
                )}
              </div>

              {/* Tracking Status */}
              {isTracked && trackingData && (
                <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-medium text-blue-900 dark:text-blue-100">
                        Currently Tracking
                      </div>
                      {trackingData.tracking_info.target_price && (
                        <div className="text-sm text-blue-700 dark:text-blue-300">
                          Target: {formatPrice(trackingData.tracking_info.target_price)}
                        </div>
                      )}
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowTrackingModal(true)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={handleRemoveTracking}
                        disabled={trackingLoading}
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-3">
                {/* Wishlist Button */}
                {user?.user_id && (
                  <Button
                    onClick={handleWishlistToggle}
                    disabled={wishlistLoading}
                    variant={isInWishlist ? "default" : "outline"}
                    className="flex-1"
                  >
                    {wishlistLoading ? (
                      <div className="flex items-center">
                        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
                        {isInWishlist ? 'Removing...' : 'Adding...'}
                      </div>
                    ) : (
                      <div className="flex items-center justify-center">
                        <span className="mr-2">
                          {isInWishlist ? '♥' : '♡'}
                        </span>
                        {isInWishlist ? 'In Wishlist' : 'Add to Wishlist'}
                      </div>
                    )}
                  </Button>
                )}

                {/* Tracking Button */}
                {!isTracked ? (
                  <Button
                    onClick={() => setShowTrackingModal(true)}
                    disabled={trackingLoading || product?.source === 'web_scraping'}
                    className="flex-1"
                    title={product?.source === 'web_scraping' ? 'Price tracking for live scraped products coming soon' : ''}
                  >
                    {trackingLoading ? 'Adding...' :
                     product?.source === 'web_scraping' ? 'Tracking Coming Soon' : 'Track This Product'}
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    onClick={() => setShowTrackingModal(true)}
                    className="flex-1"
                  >
                    Update Tracking
                  </Button>
                )}

                {bestDeal && (
                  <Button
                    variant="outline"
                    onClick={() => window.open(bestDeal.product_url, '_blank')}
                    className="flex-1"
                  >
                    View Best Deal
                  </Button>
                )}
              </div>
            </div>

            {/* Product Description */}
            {product.description && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                  Description
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {product.description}
                </p>
              </div>
            )}

            {/* Specifications */}
            {product.specifications && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                  Specifications
                </h3>
                <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {(() => {
                      try {
                        const specs = JSON.parse(product.specifications);
                        return (
                          <div className="space-y-2">
                            {Object.entries(specs).map(([key, value]) => (
                              <div key={key} className="flex justify-between">
                                <span className="font-medium capitalize">{key.replace('_', ' ')}:</span>
                                <span>{value}</span>
                              </div>
                            ))}
                          </div>
                        );
                      } catch {
                        return <span>{product.specifications}</span>;
                      }
                    })()}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

      {/* Price Comparison */}
      <div>
        <PriceComparison
          retailers={product.retailers}
          product={product}
          enableRealTimeComparison={true}
        />
      </div>

      {/* Tracking Modal */}
      {showTrackingModal && (
        <TrackingModal
          product={product}
          existingTracking={trackingData}
          onSave={isTracked ? handleUpdateTracking : handleTrackProduct}
          onClose={() => setShowTrackingModal(false)}
          loading={trackingLoading}
        />
      )}
    </div>
  );
};

export default ProductDetail;
