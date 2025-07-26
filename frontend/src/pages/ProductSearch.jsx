import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { productService } from '../services/products';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import SearchFilters from '../components/products/SearchFilters';
import ProductGrid from '../components/products/ProductGrid';
import SearchBar from '../components/products/SearchBar';
import LoadingSpinner from '../components/common/LoadingSpinner';

const ProductSearch = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();

  // State management
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [dataSource, setDataSource] = useState(null);
  const [retailersSearched, setRetailersSearched] = useState([]);

  // Search parameters
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category_id') || '');
  const [selectedBrand, setSelectedBrand] = useState(searchParams.get('brand') || '');
  const [minPrice, setMinPrice] = useState(searchParams.get('min_price') || '');
  const [maxPrice, setMaxPrice] = useState(searchParams.get('max_price') || '');
  const [currentPage, setCurrentPage] = useState(0);
  const [limit] = useState(20);

  // Load initial data
  useEffect(() => {
    loadCategories();
    loadBrands();
    setMounted(true);
  }, []);

  // Search when parameters change
  useEffect(() => {
    if (mounted) {
      searchProducts();
    }
  }, [searchQuery, selectedCategory, selectedBrand, minPrice, maxPrice, currentPage, mounted]);

  const loadCategories = async () => {
    try {
      const response = await productService.getCategories();
      setCategories(response.categories || []);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadBrands = async () => {
    try {
      const response = await productService.getBrands();
      setBrands(response.brands || []);
    } catch (error) {
      console.error('Error loading brands:', error);
    }
  };

  const searchProducts = async () => {
    setLoading(true);
    try {
      const params = {
        query: searchQuery,
        categoryId: selectedCategory,
        brand: selectedBrand,
        minPrice: minPrice ? parseFloat(minPrice) : undefined,
        maxPrice: maxPrice ? parseFloat(maxPrice) : undefined,
        limit,
        offset: currentPage * limit
      };

      const response = await productService.searchProducts(params);

      if (currentPage === 0) {
        setProducts(response.products || []);
      } else {
        setProducts(prev => [...prev, ...(response.products || [])]);
      }

      setTotalCount(response.total_count || 0);
      setHasMore(response.has_more || false);
      setDataSource(response.source || null);
      setRetailersSearched(response.retailers_searched || []);

      // Update URL parameters
      updateSearchParams(params);
    } catch (error) {
      console.error('Error searching products:', error);
      showToast('Error searching products. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const updateSearchParams = (params) => {
    const newParams = new URLSearchParams();
    if (params.query) newParams.set('q', params.query);
    if (params.categoryId) newParams.set('category_id', params.categoryId);
    if (params.brand) newParams.set('brand', params.brand);
    if (params.minPrice) newParams.set('min_price', params.minPrice.toString());
    if (params.maxPrice) newParams.set('max_price', params.maxPrice.toString());
    
    setSearchParams(newParams);
  };

  const handleSearch = useCallback((query) => {
    setSearchQuery(query);
    setCurrentPage(0);
  }, []);

  const handleFilterChange = useCallback((filterType, value) => {
    setCurrentPage(0);
    switch (filterType) {
      case 'category':
        setSelectedCategory(value);
        break;
      case 'brand':
        setSelectedBrand(value);
        break;
      case 'minPrice':
        setMinPrice(value);
        break;
      case 'maxPrice':
        setMaxPrice(value);
        break;
      default:
        break;
    }
  }, []);

  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedCategory('');
    setSelectedBrand('');
    setMinPrice('');
    setMaxPrice('');
    setCurrentPage(0);
    setSearchParams(new URLSearchParams());
  };

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      setCurrentPage(prev => prev + 1);
    }
  };

  const handleProductClick = (productId) => {
    navigate(`/products/${productId}`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Product Search
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Find and track products across multiple retailers
        </p>
      </div>

      {/* Search Bar */}
      <div>
          <SearchBar
            value={searchQuery}
            onChange={handleSearch}
            placeholder="Search for products, brands, or categories..."
          />

          {/* Data Source Indicator */}
          {dataSource && (
            <div className="mt-2 flex items-center justify-center">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                dataSource === 'web_scraping'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
              }`}>
                {dataSource === 'web_scraping' ? (
                  <>
                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Live data from {retailersSearched.length} retailer{retailersSearched.length !== 1 ? 's' : ''}
                    {retailersSearched.length > 0 && (
                      <span className="ml-1">({retailersSearched.join(', ')})</span>
                    )}
                  </>
                ) : (
                  <>
                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" clipRule="evenodd" />
                    </svg>
                    Database results
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
          {/* Filters Sidebar */}
          <div className="lg:w-1/4">
            <SearchFilters
              categories={categories}
              brands={brands}
              selectedCategory={selectedCategory}
              selectedBrand={selectedBrand}
              minPrice={minPrice}
              maxPrice={maxPrice}
              onFilterChange={handleFilterChange}
              onClearFilters={handleClearFilters}
            />
          </div>

          {/* Results */}
          <div className="lg:w-3/4">
            {/* Results Header */}
            <div className="flex justify-between items-center mb-4">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {loading && currentPage === 0 ? (
                  'Searching...'
                ) : (
                  `${totalCount} products found`
                )}
              </div>
            </div>

            {/* Loading State */}
            {loading && currentPage === 0 && (
              <div className="flex justify-center py-12">
                <LoadingSpinner size="lg" />
              </div>
            )}

            {/* No Results */}
            {!loading && products.length === 0 && (
              <div className="text-center py-12">
                <div className="text-gray-500 dark:text-gray-400 mb-4">
                  <svg className="mx-auto h-12 w-12 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <h3 className="text-lg font-medium mb-2">No products found</h3>
                  <p>Try adjusting your search criteria or filters</p>
                </div>
              </div>
            )}

            {/* Products Grid */}
            {products.length > 0 && (
              <>
                <ProductGrid
                  products={products}
                  onProductClick={handleProductClick}
                  userId={user?.user_id}
                />

                {/* Load More Button */}
                {hasMore && (
                  <div className="text-center mt-8">
                    <button
                      onClick={handleLoadMore}
                      disabled={loading}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                    >
                      {loading ? 'Loading...' : 'Load More Products'}
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductSearch;
