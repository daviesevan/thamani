import React, { useState, useEffect } from 'react';
import { productUtils } from '../../services/products';
import { Button } from '../ui/button';

const TrackingModal = ({ product, existingTracking, onSave, onClose, loading }) => {
  const [formData, setFormData] = useState({
    target_price: '',
    notes: '',
    alert_threshold_percent: 10
  });

  useEffect(() => {
    if (existingTracking) {
      setFormData({
        target_price: existingTracking.tracking_info.target_price || '',
        notes: existingTracking.tracking_info.notes || '',
        alert_threshold_percent: existingTracking.tracking_info.alert_threshold_percent || 10
      });
    } else {
      // Set default target price to current lowest price
      const lowestPrice = productUtils.getLowestPrice(product.retailers);
      setFormData(prev => ({
        ...prev,
        target_price: lowestPrice || '',
        notes: `Tracking ${product.name}`
      }));
    }
  }, [existingTracking, product]);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const submitData = {
      target_price: formData.target_price ? parseFloat(formData.target_price) : null,
      notes: formData.notes.trim(),
      alert_threshold_percent: parseFloat(formData.alert_threshold_percent)
    };

    onSave(submitData);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const formatPrice = (price) => {
    return productUtils.formatPrice(price, 'KES');
  };

  const currentLowestPrice = productUtils.getLowestPrice(product.retailers);
  const currentHighestPrice = productUtils.getHighestPrice(product.retailers);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              {existingTracking ? 'Update Tracking' : 'Track Product'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Product Info */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
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
                  <svg className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white line-clamp-2">
                {product.name}
              </h3>
              {product.brand && (
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {product.brand}
                </p>
              )}
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Current: {currentLowestPrice ? formatPrice(currentLowestPrice) : 'N/A'}
                {currentHighestPrice && currentLowestPrice !== currentHighestPrice && (
                  <span> - {formatPrice(currentHighestPrice)}</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Target Price */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Target Price (KES)
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={formData.target_price}
              onChange={(e) => handleInputChange('target_price', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your target price"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              You'll be notified when the price drops to or below this amount
            </p>
          </div>

          {/* Alert Threshold */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Alert Threshold (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={formData.alert_threshold_percent}
              onChange={(e) => handleInputChange('alert_threshold_percent', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Get alerts when price changes by this percentage or more
            </p>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Notes (Optional)
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Add any notes about this product..."
            />
          </div>

          {/* Quick Target Price Options */}
          {currentLowestPrice && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Quick Options
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => handleInputChange('target_price', Math.round(currentLowestPrice * 0.9))}
                  className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
                >
                  10% below current
                </button>
                <button
                  type="button"
                  onClick={() => handleInputChange('target_price', Math.round(currentLowestPrice * 0.8))}
                  className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
                >
                  20% below current
                </button>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1"
              disabled={loading}
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>{existingTracking ? 'Updating...' : 'Adding...'}</span>
                </div>
              ) : (
                existingTracking ? 'Update Tracking' : 'Start Tracking'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TrackingModal;
