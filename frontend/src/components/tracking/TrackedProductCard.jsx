import React, { useState } from 'react';
import { productUtils } from '../../services/products';
import { Button } from '../ui/button';

const TrackedProductCard = ({
  trackedProduct,
  selected,
  onSelect,
  onProductClick,
  onUpdate,
  onRemove
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    target_price: trackedProduct.tracking_info.target_price || '',
    notes: trackedProduct.tracking_info.notes || '',
    alert_threshold_percent: trackedProduct.tracking_info.alert_threshold_percent || 10
  });

  const { product, tracking_info, price_info } = trackedProduct;
  const lowestPrice = price_info.lowest_price;
  const targetPrice = tracking_info.target_price;

  const getPriceStatus = () => {
    if (!targetPrice || !lowestPrice) return 'unknown';
    return productUtils.getPriceStatus(targetPrice, lowestPrice, 5);
  };

  const getPriceStatusColor = () => {
    const status = getPriceStatus();
    switch (status) {
      case 'drop':
        return 'text-green-600 bg-green-50 border-green-200 dark:text-green-400 dark:bg-green-900/20 dark:border-green-800';
      case 'increase':
        return 'text-red-600 bg-red-50 border-red-200 dark:text-red-400 dark:bg-red-900/20 dark:border-red-800';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200 dark:text-gray-400 dark:bg-gray-800 dark:border-gray-700';
    }
  };

  const getPriceStatusText = () => {
    const status = getPriceStatus();
    if (!targetPrice || !lowestPrice) return 'No target set';
    
    const diff = targetPrice - lowestPrice;
    const percentage = Math.abs(Math.round((diff / targetPrice) * 100));
    
    switch (status) {
      case 'drop':
        return `${percentage}% below target`;
      case 'increase':
        return `${percentage}% above target`;
      default:
        return 'Near target price';
    }
  };

  const handleSaveEdit = () => {
    const updateData = {
      target_price: editData.target_price ? parseFloat(editData.target_price) : null,
      notes: editData.notes,
      alert_threshold_percent: parseFloat(editData.alert_threshold_percent)
    };
    
    onUpdate(updateData);
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditData({
      target_price: tracking_info.target_price || '',
      notes: tracking_info.notes || '',
      alert_threshold_percent: tracking_info.alert_threshold_percent || 10
    });
    setIsEditing(false);
  };

  const formatPrice = (price) => {
    return productUtils.formatPrice(price, 'KES');
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Header with checkbox */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3">
            <input
              type="checkbox"
              checked={selected}
              onChange={(e) => onSelect(e.target.checked)}
              className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <div className="flex-1 min-w-0">
              <h3
                onClick={onProductClick}
                className="text-lg font-medium text-gray-900 dark:text-white cursor-pointer hover:text-blue-600 dark:hover:text-blue-400 line-clamp-2"
              >
                {product.name}
              </h3>
              {product.brand && (
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {product.brand}
                </p>
              )}
            </div>
          </div>
          
          {/* Price Status Badge */}
          <div className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriceStatusColor()}`}>
            {getPriceStatusText()}
          </div>
        </div>
      </div>

      {/* Product Image and Price Info */}
      <div className="p-4">
        <div className="flex space-x-4">
          {/* Product Image */}
          <div className="flex-shrink-0">
            <div className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
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

          {/* Price Information */}
          <div className="flex-1 min-w-0">
            <div className="space-y-2">
              <div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Current Price</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  {lowestPrice ? formatPrice(lowestPrice) : 'N/A'}
                </div>
              </div>
              
              {targetPrice && (
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Target Price</div>
                  <div className="text-md font-medium text-gray-700 dark:text-gray-300">
                    {formatPrice(targetPrice)}
                  </div>
                </div>
              )}
              
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Available at {price_info.retailers?.filter(r => r.in_stock).length || 0} retailers
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tracking Details */}
      {!isEditing ? (
        <div className="px-4 pb-4">
          {tracking_info.notes && (
            <div className="mb-3">
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Notes</div>
              <div className="text-sm text-gray-700 dark:text-gray-300">
                {tracking_info.notes}
              </div>
            </div>
          )}
          
          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-3">
            <span>Added {formatDate(tracking_info.added_at)}</span>
            <span>Alert threshold: {tracking_info.alert_threshold_percent}%</span>
          </div>

          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditing(true)}
              className="flex-1"
            >
              Edit
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={onRemove}
              className="flex-1"
            >
              Remove
            </Button>
          </div>
        </div>
      ) : (
        /* Edit Form */
        <div className="px-4 pb-4 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Target Price (KES)
            </label>
            <input
              type="number"
              value={editData.target_price}
              onChange={(e) => setEditData(prev => ({ ...prev, target_price: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter target price"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Notes
            </label>
            <textarea
              value={editData.notes}
              onChange={(e) => setEditData(prev => ({ ...prev, notes: e.target.value }))}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Add notes about this product"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Alert Threshold (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={editData.alert_threshold_percent}
              onChange={(e) => setEditData(prev => ({ ...prev, alert_threshold_percent: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div className="flex space-x-2">
            <Button
              variant="default"
              size="sm"
              onClick={handleSaveEdit}
              className="flex-1"
            >
              Save
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleCancelEdit}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrackedProductCard;
