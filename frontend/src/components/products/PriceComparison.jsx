import React, { useState, useEffect } from 'react';
import { productService, productUtils } from '../../services/products';
import { Button } from '../ui/button';
import LoadingSpinner from '../common/LoadingSpinner';
import { ExternalLink } from 'lucide-react';
import { useToast } from '../../context/ToastContext';

const PriceComparison = ({ retailers, product, enableRealTimeComparison = false }) => {
  const { showToast } = useToast();
  const [sortBy, setSortBy] = useState('price'); // 'price', 'retailer', 'stock'
  const [realTimeData, setRealTimeData] = useState(null);
  const [loadingComparison, setLoadingComparison] = useState(false);
  const [showRealTimeComparison, setShowRealTimeComparison] = useState(false);

  const formatPrice = (price) => {
    return productUtils.formatPrice(price, 'KES');
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString();
  };

  const sortedRetailers = [...(retailers || [])].sort((a, b) => {
    switch (sortBy) {
      case 'price':
        // In-stock items first, then by price
        if (a.in_stock && !b.in_stock) return -1;
        if (!a.in_stock && b.in_stock) return 1;
        return a.current_price - b.current_price;
      case 'retailer':
        return a.retailer_name.localeCompare(b.retailer_name);
      case 'stock':
        if (a.in_stock && !b.in_stock) return -1;
        if (!a.in_stock && b.in_stock) return 1;
        return 0;
      default:
        return 0;
    }
  });

  const bestPrice = productUtils.getLowestPrice(retailers);
  const worstPrice = productUtils.getHighestPrice(retailers);

  // Load real-time price comparison
  const loadRealTimeComparison = async () => {
    if (!product?.name) return;

    setLoadingComparison(true);
    try {
      const comparisonData = await productService.getPriceComparison(
        product.name,
        product.brand,
        10
      );
      setRealTimeData(comparisonData);
      setShowRealTimeComparison(true);
    } catch (error) {
      console.error('Error loading real-time price comparison:', error);
    } finally {
      setLoadingComparison(false);
    }
  };

  // Get all products from real-time data for display
  const getRealTimeProducts = () => {
    if (!realTimeData?.retailers) return [];

    const allProducts = [];
    Object.values(realTimeData.retailers).forEach(retailer => {
      if (retailer.products) {
        allProducts.push(...retailer.products);
      }
    });

    return allProducts.sort((a, b) => {
      if (a.in_stock && !b.in_stock) return -1;
      if (!a.in_stock && b.in_stock) return 1;
      return a.current_price - b.current_price;
    });
  };

  const realTimeProducts = getRealTimeProducts();

  if (!retailers || retailers.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Price Comparison
        </h3>
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <svg className="mx-auto h-12 w-12 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
          </svg>
          <p>No price information available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Price Comparison
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {showRealTimeComparison
                ? `Real-time comparison across ${Object.keys(realTimeData?.retailers || {}).length} retailers`
                : `Compare prices across ${retailers.length} retailers`
              }
            </p>
          </div>

          <div className="mt-4 sm:mt-0 flex items-center space-x-3">
            {/* Real-time Comparison Button */}
            {enableRealTimeComparison && product && (
              <Button
                onClick={loadRealTimeComparison}
                disabled={loadingComparison}
                variant="outline"
                size="sm"
              >
                {loadingComparison ? (
                  <div className="flex items-center">
                    <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mr-2"></div>
                    Loading...
                  </div>
                ) : (
                  showRealTimeComparison ? 'Refresh Prices' : 'Compare Live Prices'
                )}
              </Button>
            )}

            {/* Sort Options */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="price">Sort by Price</option>
              <option value="retailer">Sort by Retailer</option>
              <option value="stock">Sort by Stock</option>
            </select>
          </div>
        </div>

        {/* Price Summary */}
        {showRealTimeComparison && realTimeData?.summary ? (
          <div className="mt-4 grid grid-cols-3 gap-4">
            <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-sm text-green-600 dark:text-green-400 font-medium">
                Best Price
              </div>
              <div className="text-lg font-bold text-green-600 dark:text-green-400">
                {formatPrice(realTimeData.summary.min_price)}
              </div>
            </div>
            <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="text-sm text-blue-600 dark:text-blue-400 font-medium">
                Average Price
              </div>
              <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                {formatPrice(realTimeData.summary.avg_price)}
              </div>
            </div>
            <div className="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <div className="text-sm text-red-600 dark:text-red-400 font-medium">
                Highest Price
              </div>
              <div className="text-lg font-bold text-red-600 dark:text-red-400">
                {formatPrice(realTimeData.summary.max_price)}
              </div>
            </div>
          </div>
        ) : bestPrice && worstPrice && (
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-sm text-green-600 dark:text-green-400 font-medium">
                Best Price
              </div>
              <div className="text-lg font-bold text-green-600 dark:text-green-400">
                {formatPrice(bestPrice)}
              </div>
            </div>
            <div className="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <div className="text-sm text-red-600 dark:text-red-400 font-medium">
                Highest Price
              </div>
              <div className="text-lg font-bold text-red-600 dark:text-red-400">
                {formatPrice(worstPrice)}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Retailers List */}
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {showRealTimeComparison && realTimeProducts.length > 0 ? (
          // Show real-time comparison results
          realTimeProducts.map((product, index) => {
            const isBestPrice = product.in_stock && product.current_price === realTimeData.summary.min_price;
            const savings = realTimeData.summary.max_price && product.in_stock ?
              realTimeData.summary.max_price - product.current_price : 0;

            return (
              <div
                key={`${product.retailer_name}-${index}`}
                className={`p-6 ${isBestPrice ? 'bg-green-50 dark:bg-green-900/10' : ''}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      {product.image_url && (
                        <img
                          src={product.image_url}
                          alt={product.name}
                          className="w-12 h-12 object-cover rounded-lg"
                        />
                      )}
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white">
                          {product.retailer_name}
                        </h4>
                        <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
                          {product.name}
                        </p>
                        {product.brand && (
                          <p className="text-xs text-gray-400 dark:text-gray-500">
                            Brand: {product.brand}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="flex items-center space-x-2">
                      <div>
                        <div className={`text-lg font-bold ${
                          isBestPrice
                            ? 'text-green-600 dark:text-green-400'
                            : 'text-gray-900 dark:text-white'
                        }`}>
                          {formatPrice(product.current_price)}
                        </div>
                        {product.original_price && product.original_price > product.current_price && (
                          <div className="text-sm text-gray-500 dark:text-gray-400 line-through">
                            {formatPrice(product.original_price)}
                          </div>
                        )}
                        {savings > 0 && (
                          <div className="text-xs text-green-600 dark:text-green-400">
                            Save {formatPrice(savings)}
                          </div>
                        )}
                      </div>

                      <div className="flex flex-col items-end space-y-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          product.in_stock
                            ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
                            : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
                        }`}>
                          {product.in_stock ? 'In Stock' : 'Out of Stock'}
                        </span>

                        {isBestPrice && (
                          <span className="px-2 py-1 text-xs bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 rounded-full">
                            Best Price
                          </span>
                        )}

                        {product.retailer_product_url && (
                          <Button
                            size="sm"
                            onClick={() => {
                              console.log(`Opening ${product.retailer_name} product:`, product.retailer_product_url);
                              window.open(product.retailer_product_url, '_blank', 'noopener,noreferrer');
                              showToast(`Opening product on ${product.retailer_name}`, 'success');
                            }}
                            disabled={!product.in_stock}
                            className="bg-primary text-primary-foreground hover:bg-primary/90"
                          >
                            <span className="flex items-center gap-1">
                              View on {product.retailer_name}
                              <ExternalLink size={14} />
                            </span>
                          </Button>
                        )}

                        {!product.retailer_product_url && product.in_stock && (
                          <Button
                            size="sm"
                            variant="outline"
                            disabled
                          >
                            Link Unavailable
                          </Button>
                        )}
                      </div>
                    </div>

                    <div className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                      Updated: {formatDate(product.last_updated)}
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          // Show existing database retailers
          sortedRetailers.map((retailer, index) => {
            const isBestPrice = retailer.in_stock && retailer.current_price === bestPrice;
            const savings = worstPrice && retailer.in_stock ? worstPrice - retailer.current_price : 0;
          
          return (
            <div
              key={retailer.retailer_id}
              className={`p-6 ${isBestPrice ? 'bg-green-50 dark:bg-green-900/10' : ''}`}
            >
              <div className="flex items-center justify-between">
                {/* Retailer Info */}
                <div className="flex items-center space-x-4">
                  {/* Retailer Logo */}
                  <div className="flex-shrink-0">
                    {retailer.retailer_logo ? (
                      <img
                        src={retailer.retailer_logo}
                        alt={retailer.retailer_name}
                        className="w-12 h-12 object-contain rounded-lg bg-gray-100 dark:bg-gray-700 p-2"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <div className={`w-12 h-12 flex items-center justify-center bg-gray-100 dark:bg-gray-700 rounded-lg ${retailer.retailer_logo ? 'hidden' : 'flex'}`}>
                      <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                    </div>
                  </div>

                  {/* Retailer Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                        {retailer.retailer_name}
                      </h4>
                      {isBestPrice && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                          Best Price
                        </span>
                      )}
                    </div>
                    
                    {/* Stock Status */}
                    <div className="flex items-center mt-1">
                      <div className={`w-2 h-2 rounded-full mr-2 ${retailer.in_stock ? 'bg-green-500' : 'bg-red-500'}`}></div>
                      <span className={`text-sm ${retailer.in_stock ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                        {retailer.in_stock ? 'In Stock' : 'Out of Stock'}
                      </span>
                    </div>

                    {/* Last Updated */}
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Updated {formatDate(retailer.last_updated)}
                    </div>
                  </div>
                </div>

                {/* Price and Actions */}
                <div className="text-right">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                    {formatPrice(retailer.current_price)}
                  </div>
                  
                  {savings > 0 && retailer.in_stock && (
                    <div className="text-sm text-green-600 dark:text-green-400 mb-2">
                      Save {formatPrice(savings)}
                    </div>
                  )}

                  {retailer.in_stock && retailer.product_url && (
                    <Button
                      size="sm"
                      onClick={() => {
                        console.log(`Opening ${retailer.retailer_name} product:`, retailer.product_url);
                        window.open(retailer.product_url, '_blank', 'noopener,noreferrer');
                        showToast(`Opening product on ${retailer.retailer_name}`, 'success');
                      }}
                      className="min-w-[120px] bg-primary text-primary-foreground hover:bg-primary/90"
                    >
                      <span className="flex items-center gap-1">
                        View on {retailer.retailer_name}
                        <ExternalLink size={14} />
                      </span>
                    </Button>
                  )}

                  {retailer.in_stock && !retailer.product_url && (
                    <Button
                      variant="outline"
                      size="sm"
                      disabled
                      className="min-w-[120px]"
                    >
                      Link Unavailable
                    </Button>
                  )}

                  {!retailer.in_stock && (
                    <Button
                      variant="outline"
                      size="sm"
                      disabled
                      className="min-w-[120px]"
                    >
                      Out of Stock
                    </Button>
                  )}
                </div>
              </div>
            </div>
          );
        }))}
      </div>

      {/* Footer */}
      <div className="p-4 bg-gray-50 dark:bg-gray-700/50 text-center">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Prices are updated regularly. Click "View Deal" to see current prices on retailer websites.
        </p>
      </div>
    </div>
  );
};

export default PriceComparison;
