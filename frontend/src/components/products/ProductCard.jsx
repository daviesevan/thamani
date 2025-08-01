import React, { useState } from 'react';
import { trackingService, productUtils } from '../../services/products';
import { useToast } from '../../context/ToastContext';
import { Button } from '../ui/button';

const ProductCard = ({ product, onClick, userId }) => {
  const [isTracking, setIsTracking] = useState(false);
  const [isTracked, setIsTracked] = useState(false);
  const { showToast } = useToast();

  const {
    product_id,
    name,
    brand,
    image_url,
    price_info,
    category,
    retailers,
    source
  } = product;

  const handleTrackProduct = async (e) => {
    e.stopPropagation(); // Prevent card click

    if (!userId) {
      showToast('Please sign in to track products', 'error');
      return;
    }

    // Check if this is a scraped product
    if (source === 'web_scraping') {
      showToast('Price tracking for live scraped products is coming soon! For now, bookmark this product or check back regularly for price updates.', 'info');
      return;
    }

    setIsTracking(true);
    try {
      if (isTracked) {
        await trackingService.removeTrackedProduct(userId, product_id);
        setIsTracked(false);
        showToast('Product removed from tracking', 'success');
      } else {
        await trackingService.addTrackedProduct(userId, product_id, {
          target_price: price_info?.min_price,
          notes: `Tracking ${name}`,
          alert_threshold_percent: 10
        });
        setIsTracked(true);
        showToast('Product added to tracking', 'success');
      }
    } catch (error) {
      console.error('Error tracking product:', error);
      showToast('Error updating product tracking', 'error');
    } finally {
      setIsTracking(false);
    }
  };

  const formatPrice = (price) => {
    return productUtils.formatPrice(price, 'KES');
  };

  const getPriceDisplay = () => {
    if (!price_info) return 'Price not available';
    
    const { min_price, max_price, retailers_count } = price_info;
    
    if (min_price === max_price) {
      return formatPrice(min_price);
    }
    
    return `${formatPrice(min_price)} - ${formatPrice(max_price)}`;
  };

  const getRetailerInfo = () => {
    // For scraped products, show actual retailer names
    if (source === 'web_scraping' && retailers && retailers.length > 0) {
      const inStockRetailers = retailers.filter(r => r.in_stock);
      if (inStockRetailers.length === 0) {
        return 'Out of stock';
      }

      if (inStockRetailers.length === 1) {
        return `Available at ${inStockRetailers[0].retailer_name || inStockRetailers[0].name}`;
      } else {
        const retailerNames = inStockRetailers.map(r => r.retailer_name || r.name).join(', ');
        return `Available at ${retailerNames}`;
      }
    }

    // For database products, use the original logic
    if (!price_info) return '';

    const { retailers_count, total_retailers } = price_info;

    if (retailers_count === 0) {
      return 'Out of stock';
    }

    return `Available at ${retailers_count} retailer${retailers_count > 1 ? 's' : ''}`;
  };

  return (
    <div
      onClick={onClick}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer group"
    >
      {/* Product Image */}
      <div className="aspect-square bg-gray-100 dark:bg-gray-700 rounded-t-lg overflow-hidden">
        {image_url ? (
          <img
            src={image_url}
            alt={name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div
          className={`w-full h-full flex items-center justify-center ${image_url ? 'hidden' : 'flex'}`}
        >
          <svg
            className="h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
      </div>

      {/* Product Info */}
      <div className="p-4">
        {/* Category */}
        {category && (
          <div className="text-xs text-blue-600 dark:text-blue-400 font-medium mb-1">
            {category.name}
          </div>
        )}

        {/* Product Name */}
        <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-1 line-clamp-2">
          {name}
        </h3>

        {/* Brand */}
        {brand && (
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
            {brand}
          </p>
        )}

        {/* Price */}
        <div className="mb-2">
          <div className="text-lg font-bold text-gray-900 dark:text-white">
            {getPriceDisplay()}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {getRetailerInfo()}
          </div>
        </div>

        {/* Price Status Indicator */}
        {price_info?.retailers_count > 0 && (
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs text-green-600 dark:text-green-400">
                In Stock
              </span>
            </div>
            {price_info.retailers_count > 1 && (
              <span className="text-xs text-blue-600 dark:text-blue-400">
                Compare prices
              </span>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1 text-xs"
            onClick={(e) => {
              e.stopPropagation();
              onClick();
            }}
          >
            View Details
          </Button>
          
          {userId && (
            <Button
              variant={isTracked ? "destructive" : "default"}
              size="sm"
              className="flex-1 text-xs"
              onClick={handleTrackProduct}
              disabled={isTracking || source === 'web_scraping'}
              title={source === 'web_scraping' ? 'Price tracking for live scraped products coming soon' : ''}
            >
              {isTracking ? (
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>...</span>
                </div>
              ) : isTracked ? (
                'Untrack'
              ) : source === 'web_scraping' ? (
                'Track Soon'
              ) : (
                'Track Price'
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
