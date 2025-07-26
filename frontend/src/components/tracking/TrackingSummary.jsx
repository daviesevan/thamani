import React from 'react';
import { productUtils } from '../../services/products';

const TrackingSummary = ({ summary }) => {
  const {
    total_tracked_products,
    products_with_target_price,
    price_drops_count,
    price_increases_count,
    recent_price_drops,
    recent_price_increases
  } = summary;

  const formatPrice = (price) => {
    return productUtils.formatPrice(price, 'KES');
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
        Tracking Summary
      </h2>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {total_tracked_products}
          </div>
          <div className="text-sm text-blue-600 dark:text-blue-400 font-medium">
            Products Tracked
          </div>
        </div>

        <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
          <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
            {products_with_target_price}
          </div>
          <div className="text-sm text-purple-600 dark:text-purple-400 font-medium">
            With Target Price
          </div>
        </div>

        <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {price_drops_count}
          </div>
          <div className="text-sm text-green-600 dark:text-green-400 font-medium">
            Price Drops
          </div>
        </div>

        <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
          <div className="text-2xl font-bold text-red-600 dark:text-red-400">
            {price_increases_count}
          </div>
          <div className="text-sm text-red-600 dark:text-red-400 font-medium">
            Price Increases
          </div>
        </div>
      </div>

      {/* Price Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Price Drops */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3 flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
            Recent Price Drops
          </h3>
          
          {recent_price_drops && recent_price_drops.length > 0 ? (
            <div className="space-y-3">
              {recent_price_drops.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800"
                >
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {item.product_name}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Target: {formatPrice(item.target_price)}
                    </div>
                  </div>
                  <div className="text-right ml-3">
                    <div className="text-sm font-bold text-green-600 dark:text-green-400">
                      {formatPrice(item.current_lowest_price)}
                    </div>
                    <div className="text-xs text-green-600 dark:text-green-400">
                      Save {formatPrice(item.savings)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6 text-gray-500 dark:text-gray-400">
              <svg className="mx-auto h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <div className="text-sm">No recent price drops</div>
            </div>
          )}
        </div>

        {/* Price Increases */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3 flex items-center">
            <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
            Recent Price Increases
          </h3>
          
          {recent_price_increases && recent_price_increases.length > 0 ? (
            <div className="space-y-3">
              {recent_price_increases.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800"
                >
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {item.product_name}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Target: {formatPrice(item.target_price)}
                    </div>
                  </div>
                  <div className="text-right ml-3">
                    <div className="text-sm font-bold text-red-600 dark:text-red-400">
                      {formatPrice(item.current_lowest_price)}
                    </div>
                    <div className="text-xs text-red-600 dark:text-red-400">
                      +{formatPrice(item.increase)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6 text-gray-500 dark:text-gray-400">
              <svg className="mx-auto h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
              <div className="text-sm">No recent price increases</div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      {total_tracked_products === 0 && (
        <div className="mt-6 text-center">
          <div className="text-gray-500 dark:text-gray-400 mb-4">
            <svg className="mx-auto h-12 w-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <div className="text-lg font-medium mb-2">Start tracking products</div>
            <div className="text-sm">Add products to your tracking list to monitor price changes and get alerts</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrackingSummary;
