import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Search, TrendingUp, TrendingDown, Clock, AlertCircle, Plus, Eye } from 'lucide-react';
import { trackingService, productService, productUtils } from '../services/products';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import LoadingSpinner from '../components/common/LoadingSpinner';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();

  const [isLoading, setIsLoading] = useState(true);
  const [trackingSummary, setTrackingSummary] = useState(null);
  const [recentProducts, setRecentProducts] = useState([]);
  const [popularProducts, setPopularProducts] = useState([]);

  useEffect(() => {
    if (user?.user_id) {
      loadDashboardData();
    } else {
      setIsLoading(false);
    }
  }, [user?.user_id]);

  const loadDashboardData = async () => {
    try {
      // Load tracking summary
      const summary = await trackingService.getTrackingSummary(user.user_id);
      setTrackingSummary(summary);

      // Load recent tracked products (first 3)
      const trackedResponse = await trackingService.getTrackedProducts(user.user_id);
      setRecentProducts(trackedResponse.tracked_products?.slice(0, 3) || []);

      // Load popular products for recommendations
      const popularResponse = await productService.getPopularProducts(4);
      setPopularProducts(popularResponse.products || []);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatPrice = (price) => {
    return productUtils.formatPrice(price, 'KES');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-serif font-bold">
          Welcome{user?.full_name ? `, ${user.full_name}` : ''}
        </h1>
        <p className="text-muted-foreground mt-2">
          Track prices, set alerts, and save money on your favorite products.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          className="bg-background border border-border p-4 rounded-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <div className="flex items-center justify-between">
            <h3 className="font-serif font-medium">Tracked Products</h3>
            <div className="p-2 bg-primary/10 rounded-full">
              <Search size={18} className="text-primary" />
            </div>
          </div>
          <p className="text-3xl font-serif font-bold mt-2">
            {trackingSummary?.total_tracked_products || 0}
          </p>
          <p className="text-sm text-muted-foreground mt-1">Products you're tracking</p>
        </motion.div>

        <motion.div
          className="bg-background border border-border p-4 rounded-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <div className="flex items-center justify-between">
            <h3 className="font-serif font-medium">Price Drops</h3>
            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-full">
              <TrendingDown size={18} className="text-green-600 dark:text-green-400" />
            </div>
          </div>
          <p className="text-3xl font-serif font-bold mt-2">
            {trackingSummary?.price_drops_count || 0}
          </p>
          <p className="text-sm text-muted-foreground mt-1">Products with price drops</p>
        </motion.div>

        <motion.div
          className="bg-background border border-border p-4 rounded-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <div className="flex items-center justify-between">
            <h3 className="font-serif font-medium">Price Increases</h3>
            <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-full">
              <TrendingUp size={18} className="text-red-600 dark:text-red-400" />
            </div>
          </div>
          <p className="text-3xl font-serif font-bold mt-2">
            {trackingSummary?.price_increases_count || 0}
          </p>
          <p className="text-sm text-muted-foreground mt-1">Products with price increases</p>
        </motion.div>

        <motion.div
          className="bg-background border border-border p-4 rounded-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
        >
          <div className="flex items-center justify-between">
            <h3 className="font-serif font-medium">Active Alerts</h3>
            <div className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-full">
              <AlertCircle size={18} className="text-amber-600 dark:text-amber-400" />
            </div>
          </div>
          <p className="text-3xl font-serif font-bold mt-2">
            {trackingSummary?.products_with_target_price || 0}
          </p>
          <p className="text-sm text-muted-foreground mt-1">Price alerts you've set</p>
        </motion.div>
      </div>

      {/* Recent Tracked Products */}
      <motion.div
        className="bg-background border border-border p-6 rounded-md"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.5 }}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-serif font-bold">Your Tracked Products</h2>
          <div className="flex space-x-2">
            <button
              onClick={() => navigate('/dashboard/products')}
              className="px-3 py-1 text-sm bg-primary/10 text-primary hover:bg-primary/20 transition-colors rounded-md flex items-center space-x-1"
            >
              <Eye size={14} />
              <span>View All</span>
            </button>
            <button
              onClick={() => navigate('/dashboard/search')}
              className="px-3 py-1 text-sm bg-primary text-white dark:text-black hover:bg-primary/90 transition-colors rounded-md flex items-center space-x-1"
            >
              <Plus size={14} />
              <span>Add Product</span>
            </button>
          </div>
        </div>

        {recentProducts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recentProducts.map((trackedProduct) => {
              const { product, price_info, tracking_info } = trackedProduct;
              const priceStatus = tracking_info.target_price && price_info.lowest_price
                ? productUtils.getPriceStatus(tracking_info.target_price, price_info.lowest_price, 5)
                : 'unknown';

              return (
                <div
                  key={trackedProduct.tracking_id}
                  onClick={() => navigate(`/products/${product.product_id}`)}
                  className="border border-border rounded-md p-4 hover:bg-accent/50 transition-colors cursor-pointer"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-muted rounded-md flex items-center justify-center">
                      {product.image_url ? (
                        <img
                          src={product.image_url}
                          alt={product.name}
                          className="w-full h-full object-cover rounded-md"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                      ) : null}
                      <div className={`w-full h-full flex items-center justify-center ${product.image_url ? 'hidden' : 'flex'}`}>
                        <Search size={16} className="text-muted-foreground" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-sm truncate">{product.name}</h3>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-sm font-bold">
                          {price_info.lowest_price ? formatPrice(price_info.lowest_price) : 'N/A'}
                        </span>
                        {priceStatus === 'drop' && (
                          <span className="text-xs text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30 px-2 py-1 rounded-full">
                            Price Drop
                          </span>
                        )}
                        {priceStatus === 'increase' && (
                          <span className="text-xs text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30 px-2 py-1 rounded-full">
                            Price Up
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8">
            <Search size={48} className="mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground">No tracked products yet.</p>
            <p className="text-sm text-muted-foreground mt-2">
              Start tracking products to monitor price changes and get alerts.
            </p>
            <button
              onClick={() => navigate('/dashboard/search')}
              className="mt-4 px-4 py-2 bg-primary text-white dark:text-black font-serif hover:bg-primary/90 transition-colors rounded-md"
            >
              Browse Products
            </button>
          </div>
        )}
      </motion.div>

      {/* Popular Products */}
      <motion.div
        className="bg-background border border-border p-6 rounded-md"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.6 }}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-serif font-bold">Popular Products</h2>
          <button
            onClick={() => navigate('/dashboard/search')}
            className="text-sm text-primary hover:text-primary/80 transition-colors"
          >
            View All →
          </button>
        </div>

        {popularProducts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {popularProducts.map((product) => (
              <div
                key={product.product_id}
                onClick={() => navigate(`/products/${product.product_id}`)}
                className="border border-border rounded-md p-4 hover:bg-accent/50 transition-colors cursor-pointer"
              >
                <div className="aspect-square bg-muted rounded-md mb-3 overflow-hidden">
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
                  <div className={`w-full h-full flex items-center justify-center ${product.image_url ? 'hidden' : 'flex'}`}>
                    <Search size={24} className="text-muted-foreground" />
                  </div>
                </div>
                <h3 className="font-medium text-sm truncate mb-1">{product.name}</h3>
                <p className="text-xs text-muted-foreground mb-2">{product.brand}</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold">
                    {product.price_info?.min_price ? formatPrice(product.price_info.min_price) : 'N/A'}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {product.price_info?.retailers_count || 0} stores
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Clock size={48} className="mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground">No popular products available.</p>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default Dashboard;
