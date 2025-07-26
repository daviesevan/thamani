import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { trackingService, productUtils } from '../services/products';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import TrackedProductCard from '../components/tracking/TrackedProductCard';
import TrackingSummary from '../components/tracking/TrackingSummary';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Button } from '../components/ui/button';

const TrackedProducts = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();

  const [trackedProducts, setTrackedProducts] = useState([]);
  const [trackingSummary, setTrackingSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [includeArchived, setIncludeArchived] = useState(false);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [bulkActionLoading, setBulkActionLoading] = useState(false);

  useEffect(() => {
    if (user?.user_id) {
      loadTrackedProducts();
      loadTrackingSummary();
    }
  }, [user?.user_id, includeArchived]);

  const loadTrackedProducts = async () => {
    try {
      const response = await trackingService.getTrackedProducts(user.user_id, includeArchived);
      setTrackedProducts(response.tracked_products || []);
    } catch (error) {
      console.error('Error loading tracked products:', error);
      showToast('Error loading tracked products', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadTrackingSummary = async () => {
    try {
      const summary = await trackingService.getTrackingSummary(user.user_id);
      setTrackingSummary(summary);
    } catch (error) {
      console.error('Error loading tracking summary:', error);
    }
  };

  const handleProductClick = (productId) => {
    navigate(`/products/${productId}`);
  };

  const handleUpdateProduct = async (productId, updateData) => {
    try {
      await trackingService.updateTrackedProduct(user.user_id, productId, updateData);
      showToast('Product tracking updated', 'success');
      loadTrackedProducts();
      loadTrackingSummary();
    } catch (error) {
      console.error('Error updating tracked product:', error);
      showToast('Error updating product tracking', 'error');
    }
  };

  const handleRemoveProduct = async (productId) => {
    try {
      await trackingService.removeTrackedProduct(user.user_id, productId);
      showToast('Product removed from tracking', 'success');
      loadTrackedProducts();
      loadTrackingSummary();
      setSelectedProducts(prev => prev.filter(id => id !== productId));
    } catch (error) {
      console.error('Error removing tracked product:', error);
      showToast('Error removing product from tracking', 'error');
    }
  };

  const handleSelectProduct = (productId, selected) => {
    if (selected) {
      setSelectedProducts(prev => [...prev, productId]);
    } else {
      setSelectedProducts(prev => prev.filter(id => id !== productId));
    }
  };

  const handleSelectAll = () => {
    if (selectedProducts.length === trackedProducts.length) {
      setSelectedProducts([]);
    } else {
      setSelectedProducts(trackedProducts.map(p => p.product.product_id));
    }
  };

  const handleBulkRemove = async () => {
    if (selectedProducts.length === 0) return;

    setBulkActionLoading(true);
    try {
      await trackingService.bulkRemoveTrackedProducts(user.user_id, selectedProducts);
      showToast(`${selectedProducts.length} products removed from tracking`, 'success');
      setSelectedProducts([]);
      loadTrackedProducts();
      loadTrackingSummary();
    } catch (error) {
      console.error('Error bulk removing products:', error);
      showToast('Error removing products from tracking', 'error');
    } finally {
      setBulkActionLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Sign In Required
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Please sign in to view your tracked products
          </p>
          <Button onClick={() => navigate('/signin')}>
            Sign In
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Tracked Products
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Monitor price changes and get alerts for your favorite products
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex space-x-3">
            <Button
              variant="outline"
              onClick={() => navigate('/dashboard/search')}
            >
              Add Products
            </Button>
          </div>
        </div>

        {/* Summary */}
        {trackingSummary && (
          <div className="mb-6">
            <TrackingSummary summary={trackingSummary} />
          </div>
        )}

        {/* Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 space-y-3 sm:space-y-0">
          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={includeArchived}
                onChange={(e) => setIncludeArchived(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Include archived products
              </span>
            </label>
          </div>

          {trackedProducts.length > 0 && (
            <div className="flex items-center space-x-3">
              <button
                onClick={handleSelectAll}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                {selectedProducts.length === trackedProducts.length ? 'Deselect All' : 'Select All'}
              </button>
              
              {selectedProducts.length > 0 && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleBulkRemove}
                  disabled={bulkActionLoading}
                >
                  {bulkActionLoading ? 'Removing...' : `Remove ${selectedProducts.length} Selected`}
                </Button>
              )}
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {/* Empty State */}
        {!loading && trackedProducts.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500 dark:text-gray-400 mb-4">
              <svg className="mx-auto h-12 w-12 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <h3 className="text-lg font-medium mb-2">No tracked products</h3>
              <p className="mb-6">Start tracking products to monitor price changes and get alerts</p>
              <Button onClick={() => navigate('/dashboard/search')}>
                Browse Products
              </Button>
            </div>
          </div>
        )}

        {/* Products Grid */}
        {!loading && trackedProducts.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {trackedProducts.map((trackedProduct) => (
              <TrackedProductCard
                key={trackedProduct.tracking_id}
                trackedProduct={trackedProduct}
                selected={selectedProducts.includes(trackedProduct.product.product_id)}
                onSelect={(selected) => handleSelectProduct(trackedProduct.product.product_id, selected)}
                onProductClick={() => handleProductClick(trackedProduct.product.product_id)}
                onUpdate={(updateData) => handleUpdateProduct(trackedProduct.product.product_id, updateData)}
                onRemove={() => handleRemoveProduct(trackedProduct.product.product_id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TrackedProducts;
