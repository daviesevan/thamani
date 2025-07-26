import React, { useState } from 'react';
import { Button } from '../ui/button';

const SearchFilters = ({
  categories,
  brands,
  selectedCategory,
  selectedBrand,
  minPrice,
  maxPrice,
  onFilterChange,
  onClearFilters
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleCategoryChange = (e) => {
    onFilterChange('category', e.target.value);
  };

  const handleBrandChange = (e) => {
    onFilterChange('brand', e.target.value);
  };

  const handleMinPriceChange = (e) => {
    onFilterChange('minPrice', e.target.value);
  };

  const handleMaxPriceChange = (e) => {
    onFilterChange('maxPrice', e.target.value);
  };

  const hasActiveFilters = selectedCategory || selectedBrand || minPrice || maxPrice;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Mobile Toggle */}
      <div className="lg:hidden">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full px-4 py-3 text-left font-medium text-gray-900 dark:text-white flex items-center justify-between"
        >
          <span>Filters</span>
          <svg
            className={`h-5 w-5 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      {/* Filters Content */}
      <div className={`${isExpanded ? 'block' : 'hidden'} lg:block p-4 space-y-6`}>
        {/* Header */}
        <div className="hidden lg:flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Filters</h3>
          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClearFilters}
              className="text-blue-600 hover:text-blue-700"
            >
              Clear All
            </Button>
          )}
        </div>

        {/* Category Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Category
          </label>
          <select
            value={selectedCategory}
            onChange={handleCategoryChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Categories</option>
            {categories.map((category) => (
              <optgroup key={category.category_id} label={category.name}>
                <option value={category.category_id}>{category.name}</option>
                {category.subcategories?.map((sub) => (
                  <option key={sub.category_id} value={sub.category_id}>
                    &nbsp;&nbsp;{sub.name}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        {/* Brand Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Brand
          </label>
          <select
            value={selectedBrand}
            onChange={handleBrandChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Brands</option>
            {brands.map((brand) => (
              <option key={brand.name} value={brand.name}>
                {brand.name} ({brand.product_count})
              </option>
            ))}
          </select>
        </div>

        {/* Price Range Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Price Range (KES)
          </label>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <input
                type="number"
                placeholder="Min"
                value={minPrice}
                onChange={handleMinPriceChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <input
                type="number"
                placeholder="Max"
                value={maxPrice}
                onChange={handleMaxPriceChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Quick Price Filters */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Quick Filters
          </label>
          <div className="grid grid-cols-1 gap-2">
            <button
              onClick={() => {
                onFilterChange('minPrice', '');
                onFilterChange('maxPrice', '10000');
              }}
              className={`px-3 py-2 text-sm rounded-md border transition-colors ${
                maxPrice === '10000' && !minPrice
                  ? 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/20 dark:border-blue-700 dark:text-blue-300'
                  : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              Under KES 10,000
            </button>
            <button
              onClick={() => {
                onFilterChange('minPrice', '10000');
                onFilterChange('maxPrice', '50000');
              }}
              className={`px-3 py-2 text-sm rounded-md border transition-colors ${
                minPrice === '10000' && maxPrice === '50000'
                  ? 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/20 dark:border-blue-700 dark:text-blue-300'
                  : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              KES 10,000 - 50,000
            </button>
            <button
              onClick={() => {
                onFilterChange('minPrice', '50000');
                onFilterChange('maxPrice', '100000');
              }}
              className={`px-3 py-2 text-sm rounded-md border transition-colors ${
                minPrice === '50000' && maxPrice === '100000'
                  ? 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/20 dark:border-blue-700 dark:text-blue-300'
                  : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              KES 50,000 - 100,000
            </button>
            <button
              onClick={() => {
                onFilterChange('minPrice', '100000');
                onFilterChange('maxPrice', '');
              }}
              className={`px-3 py-2 text-sm rounded-md border transition-colors ${
                minPrice === '100000' && !maxPrice
                  ? 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/20 dark:border-blue-700 dark:text-blue-300'
                  : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              Over KES 100,000
            </button>
          </div>
        </div>

        {/* Mobile Clear Button */}
        <div className="lg:hidden">
          {hasActiveFilters && (
            <Button
              variant="outline"
              onClick={onClearFilters}
              className="w-full"
            >
              Clear All Filters
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchFilters;
