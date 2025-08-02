"""
Product service for searching and discovering products
"""
import logging
from typing import Dict, Any, List, Optional
from flask import abort
from sqlalchemy import or_, and_, desc
from app.extensions.extensions import db
from app.models.product import Product, ProductRetailer, Category, Retailer
import time
from datetime import datetime, timedelta

# Set up logger
logger = logging.getLogger(__name__)

# Simple in-memory cache for scraped products (expires after 1 hour)
_scraped_products_cache = {}
_cache_expiry_time = 3600  # 1 hour in seconds


def _is_relevant_product(product_name: str, search_product_name: str, brand: str = None) -> bool:
    """
    Check if a scraped product is relevant to the search query

    Args:
        product_name: Name of the scraped product
        search_product_name: Original product name being searched
        brand: Brand name (optional)

    Returns:
        bool: True if product is relevant, False otherwise
    """
    if not product_name or not search_product_name:
        return False

    # Convert to lowercase for comparison
    product_lower = product_name.lower()
    search_lower = search_product_name.lower()

    # Exclusion terms that indicate accessories or irrelevant products
    exclusion_terms = [
        'cover', 'case', 'screen protector', 'protector', 'tempered glass',
        'charger', 'cable', 'adapter', 'power bank', 'holder', 'stand',
        'pouch', 'sleeve', 'bag', 'wallet', 'flip cover', 'back cover',
        'bumper', 'skin', 'sticker', 'ring', 'mount', 'bracket',
        'earphone', 'headphone', 'speaker', 'bluetooth', 'wireless',
        'memory card', 'sd card', 'usb', 'otg', 'stylus', 'pen'
    ]

    # Check if product name contains any exclusion terms
    for term in exclusion_terms:
        if term in product_lower:
            return False

    # Extract key words from search product name
    search_words = search_lower.split()
    product_words = product_lower.split()

    # If brand is specified, it should be present in the product name
    if brand:
        brand_lower = brand.lower()
        if brand_lower not in product_lower:
            return False

    # Check if main product words are present
    # At least 60% of search words should be in product name
    matching_words = 0
    for word in search_words:
        if len(word) > 2:  # Skip very short words
            if word in product_lower:
                matching_words += 1

    # Calculate match percentage
    significant_words = [w for w in search_words if len(w) > 2]
    if not significant_words:
        return False

    match_percentage = matching_words / len(significant_words)

    # Require at least 60% match for relevance
    return match_percentage >= 0.6


def _calculate_relevance_score(product_name: str, search_product_name: str, brand: str = None) -> float:
    """
    Calculate relevance score for a product

    Args:
        product_name: Name of the scraped product
        search_product_name: Original product name being searched
        brand: Brand name (optional)

    Returns:
        float: Relevance score between 0 and 1
    """
    if not product_name or not search_product_name:
        return 0.0

    product_lower = product_name.lower()
    search_lower = search_product_name.lower()

    # Start with base score
    score = 0.0

    # Exact match gets highest score
    if product_lower == search_lower:
        return 1.0

    # Check word matches
    search_words = set(search_lower.split())
    product_words = set(product_lower.split())

    # Calculate word overlap
    common_words = search_words.intersection(product_words)
    if search_words:
        word_score = len(common_words) / len(search_words)
        score += word_score * 0.7

    # Brand match bonus
    if brand:
        brand_lower = brand.lower()
        if brand_lower in product_lower:
            score += 0.2

    # Length similarity bonus (prefer similar length products)
    length_diff = abs(len(product_lower) - len(search_lower))
    max_length = max(len(product_lower), len(search_lower))
    if max_length > 0:
        length_score = 1 - (length_diff / max_length)
        score += length_score * 0.1

    return min(score, 1.0)


class ProductService:
    """
    Service for product search and discovery
    """

    @classmethod
    def _cache_scraped_products(cls, products: List[Dict[str, Any]]) -> None:
        """
        Cache scraped products temporarily

        Args:
            products: List of scraped products to cache
        """
        current_time = time.time()
        for product in products:
            product_id = product.get('product_id')
            if product_id:
                _scraped_products_cache[product_id] = {
                    'product': product,
                    'cached_at': current_time
                }

    @classmethod
    def _get_cached_scraped_product(cls, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a cached scraped product

        Args:
            product_id: Product ID to retrieve

        Returns:
            Cached product data or None if not found/expired
        """
        if product_id not in _scraped_products_cache:
            return None

        cached_item = _scraped_products_cache[product_id]
        current_time = time.time()

        # Check if cache has expired
        if current_time - cached_item['cached_at'] > _cache_expiry_time:
            del _scraped_products_cache[product_id]
            return None

        return cached_item['product']

    @classmethod
    def search_products(cls, query: str = "", category_id: Optional[int] = None,
                       brand: Optional[str] = None, min_price: Optional[float] = None,
                       max_price: Optional[float] = None, limit: int = 20, offset: int = 0,
                       use_web_scraping: bool = True) -> Dict[str, Any]:
        """
        Search for products using real-time web scraping or database

        Args:
            query: Search query for product name/description
            category_id: Filter by category
            brand: Filter by brand
            min_price: Minimum price filter
            max_price: Maximum price filter
            limit: Number of results to return
            offset: Number of results to skip
            use_web_scraping: Whether to use real-time web scraping

        Returns:
            Dict containing search results and metadata
        """
        try:
            logger.info(f"Search request: query='{query}', use_web_scraping={use_web_scraping}")

            if use_web_scraping and query:
                # Use real-time web scraping for live results
                logger.info("Using web scraping for search")
                return cls._search_with_web_scraping(query, min_price, max_price, limit, offset)
            else:
                # Fallback to database search
                logger.info("Using database search")
                return cls._search_database(query, category_id, brand, min_price, max_price, limit, offset)

        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            abort(500, description="Internal server error")

    @classmethod
    def _search_with_web_scraping(cls, query: str, min_price: Optional[float] = None,
                                 max_price: Optional[float] = None, limit: int = 20,
                                 offset: int = 0) -> Dict[str, Any]:
        """
        Search products using real-time web scraping
        """
        try:
            from app.scrapers.scraper_manager import ScraperManager
            from app.scrapers.product_comparison import ProductComparison

            logger.info(f"Starting real-time web scraping search for: {query}")

            # Initialize scraping components
            scraper_manager = ScraperManager()
            product_comparison = ProductComparison()

            # Perform real-time scraping across all retailers
            max_pages = 1  # Limit to 1 page per retailer for performance
            search_results = scraper_manager.search_all_retailers(
                query=query,
                max_pages_per_retailer=max_pages,
                max_workers=3
            )

            # Aggregate and format results
            all_products = []
            for retailer, products in search_results.items():
                for product in products:
                    # Convert scraped product to our format
                    formatted_product = cls._format_scraped_product(product, retailer)

                    # Apply price filters
                    if min_price is not None and formatted_product.get('min_price', 0) < min_price:
                        continue
                    if max_price is not None and formatted_product.get('max_price', float('inf')) > max_price:
                        continue

                    all_products.append(formatted_product)

            # Sort by relevance and price
            all_products.sort(key=lambda x: (
                -cls._calculate_relevance_score(x['name'], query),
                x.get('min_price', float('inf'))
            ))

            # Apply pagination
            total_count = len(all_products)
            paginated_products = all_products[offset:offset + limit]

            # Cache the scraped products for later retrieval
            cls._cache_scraped_products(all_products)

            logger.info(f"Web scraping search completed: {total_count} products found, {len(all_products)} cached")

            return {
                "products": paginated_products,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count,
                "source": "web_scraping",
                "retailers_searched": list(search_results.keys()),
                "search_query": query
            }

        except Exception as e:
            logger.error(f"Error in web scraping search: {str(e)}")
            # Fallback to database search if scraping fails
            logger.info("Falling back to database search")
            return cls._search_database(query, None, None, min_price, max_price, limit, offset)

    @classmethod
    def _search_database(cls, query: str = "", category_id: Optional[int] = None,
                        brand: Optional[str] = None, min_price: Optional[float] = None,
                        max_price: Optional[float] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Search products in local database (fallback method)
        """
        try:
            # Start with base query
            products_query = Product.query

            # Apply text search
            if query:
                search_filter = or_(
                    Product.name.ilike(f'%{query}%'),
                    Product.description.ilike(f'%{query}%'),
                    Product.brand.ilike(f'%{query}%'),
                    Product.model.ilike(f'%{query}%')
                )
                products_query = products_query.filter(search_filter)

            # Apply category filter
            if category_id:
                products_query = products_query.filter(Product.category_id == category_id)

            # Apply brand filter
            if brand:
                products_query = products_query.filter(Product.brand.ilike(f'%{brand}%'))

            # Apply price filters (need to join with ProductRetailer)
            if min_price is not None or max_price is not None:
                products_query = products_query.join(ProductRetailer)
                if min_price is not None:
                    products_query = products_query.filter(ProductRetailer.current_price >= min_price)
                if max_price is not None:
                    products_query = products_query.filter(ProductRetailer.current_price <= max_price)
                # Remove duplicates from join
                products_query = products_query.distinct()

            # Get total count before pagination
            total_count = products_query.count()

            # Apply pagination and ordering
            products = products_query.order_by(desc(Product.created_at)).offset(offset).limit(limit).all()

            # Format results
            results = []
            for product in products:
                product_data = cls._format_product_summary(product)
                results.append(product_data)

            return {
                "products": results,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count,
                "source": "database"
            }

        except Exception as e:
            logger.error(f"Error in database search: {str(e)}")
            raise
    
    @classmethod
    def get_product_details(cls, product_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific product

        Args:
            product_id: Product ID

        Returns:
            Dict containing detailed product information
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                abort(404, description="Product not found")

            return cls._format_product_details(product)

        except Exception as e:
            logger.error(f"Error getting product details: {str(e)}")
            abort(500, description="Internal server error")

    @classmethod
    def get_price_comparison(cls, product_name: str, brand: str = None, limit: int = 10) -> Dict[str, Any]:
        """
        Get real-time price comparison for a product across multiple retailers

        Args:
            product_name: Name of the product to compare
            brand: Brand of the product (optional)
            limit: Maximum number of results per retailer

        Returns:
            Dict containing price comparison data from multiple retailers
        """
        try:
            from app.scrapers.scraper_manager import ScraperManager

            # Create search query with better specificity
            search_query = product_name
            if brand:
                # Check if brand is already in product name to avoid duplication
                if brand.lower() not in product_name.lower():
                    search_query = f"{brand} {product_name}"

            # Add exclusion terms to avoid accessories
            exclusion_terms = ['cover', 'case', 'screen protector', 'charger', 'cable', 'adapter', 'holder', 'stand', 'pouch', 'sleeve']

            logger.info(f"Getting price comparison for: {search_query}")

            # Initialize scraper manager
            scraper_manager = ScraperManager()

            # Get results from all retailers
            comparison_results = {
                'product_name': product_name,
                'brand': brand,
                'search_query': search_query,
                'retailers': {},
                'summary': {
                    'total_results': 0,
                    'min_price': None,
                    'max_price': None,
                    'avg_price': None,
                    'retailers_count': 0
                },
                'last_updated': datetime.now().isoformat()
            }

            # Search all retailers at once
            logger.info(f"Searching all retailers for: {search_query}")
            search_results = scraper_manager.search_all_retailers(
                query=search_query,
                max_pages_per_retailer=1,
                max_workers=3
            )

            all_prices = []

            # Process results from each retailer
            for retailer, products in search_results.items():
                try:
                    logger.info(f"Processing {len(products)} products from {retailer}")

                    # Format products for comparison with relevance filtering
                    formatted_products = []
                    product_scores = []

                    for product in products:
                        product_name_scraped = product.get('name', '')
                        price = product.get('price', 0)

                        # Skip products without price or name
                        if not price or price <= 0 or not product_name_scraped:
                            continue

                        # Check if product is relevant to search query
                        if not _is_relevant_product(product_name_scraped, product_name, brand):
                            logger.debug(f"Skipping irrelevant product: {product_name_scraped}")
                            continue

                        # Calculate relevance score
                        relevance_score = _calculate_relevance_score(product_name_scraped, product_name, brand)

                        formatted_product = {
                            'product_id': product.get('id', ''),
                            'name': product_name_scraped,
                            'brand': product.get('brand', ''),
                            'image_url': product.get('image_url', ''),
                            'description': product.get('description', ''),
                            'current_price': price,
                            'original_price': product.get('original_price'),
                            'currency_code': product.get('currency', 'KES'),
                            'retailer_product_url': product.get('url', ''),
                            'in_stock': product.get('in_stock', True),
                            'retailer_name': retailer.title(),
                            'last_updated': datetime.now().isoformat(),
                            'relevance_score': relevance_score
                        }

                        product_scores.append((formatted_product, relevance_score))

                    # Sort by relevance score (highest first) and take top results
                    product_scores.sort(key=lambda x: x[1], reverse=True)
                    formatted_products = [product for product, score in product_scores[:limit]]

                    # Add prices to overall list
                    for product in formatted_products:
                        all_prices.append(product['current_price'])

                    comparison_results['retailers'][retailer] = {
                        'name': retailer.title(),
                        'products': formatted_products,
                        'count': len(formatted_products),
                        'status': 'success' if formatted_products else 'no_results',
                        'total_scraped': len(products),
                        'filtered_count': len(products) - len(formatted_products)
                    }

                    logger.info(f"Found {len(formatted_products)} relevant products from {retailer} (filtered {len(products) - len(formatted_products)} irrelevant items)")

                except Exception as retailer_error:
                    logger.error(f"Error processing {retailer}: {str(retailer_error)}")
                    comparison_results['retailers'][retailer] = {
                        'name': retailer.title(),
                        'products': [],
                        'count': 0,
                        'status': 'error',
                        'error': str(retailer_error)
                    }

            # Calculate summary statistics
            if all_prices:
                comparison_results['summary'] = {
                    'total_results': len(all_prices),
                    'min_price': min(all_prices),
                    'max_price': max(all_prices),
                    'avg_price': sum(all_prices) / len(all_prices),
                    'retailers_count': len([r for r in comparison_results['retailers'].values() if r['count'] > 0])
                }

            logger.info(f"Price comparison completed. Found {len(all_prices)} total results")
            return comparison_results

        except Exception as e:
            logger.error(f"Error getting price comparison: {str(e)}")
            abort(500, description="Failed to get price comparison")

    @classmethod
    def get_scraped_product_details(cls, product_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a scraped product

        Args:
            product_id: String-based product ID from web scraping

        Returns:
            Dict containing detailed product information
        """
        try:
            # Try to get the product from cache first
            cached_product = cls._get_cached_scraped_product(product_id)

            if cached_product:
                logger.info(f"Retrieved scraped product {product_id} from cache")
                return cached_product

            # If not in cache, the product might be from an older search
            # In this case, we'll return a helpful error message
            logger.warning(f"Scraped product {product_id} not found in cache")
            abort(404, description="Product not found. This may be because the search results have expired. Please search for the product again.")

        except Exception as e:
            logger.error(f"Error getting scraped product details: {str(e)}")
            abort(500, description="Internal server error")

    @classmethod
    def _format_scraped_product(cls, scraped_product: Dict[str, Any], retailer: str) -> Dict[str, Any]:
        """
        Format a scraped product to match our API format
        """
        try:
            # Generate a unique ID for the scraped product
            import hashlib
            product_id = hashlib.md5(f"{retailer}_{scraped_product.get('name', '')}_{scraped_product.get('url', '')}".encode()).hexdigest()[:16]

            # Extract price information
            price = scraped_product.get('price', 0)
            original_price = scraped_product.get('original_price')

            # Calculate discount if available
            discount_percent = scraped_product.get('discount_percent')
            if not discount_percent and original_price and price and original_price > price:
                discount_percent = int(((original_price - price) / original_price) * 100)

            return {
                "product_id": product_id,
                "name": scraped_product.get('name', ''),
                "description": scraped_product.get('description', ''),
                "brand": cls._extract_brand_from_name(scraped_product.get('name', '')),
                "model": "",
                "image_url": scraped_product.get('image_url'),
                "category": {
                    "category_id": None,
                    "name": cls._guess_category_from_name(scraped_product.get('name', ''))
                },
                "price_info": {
                    "min_price": price,
                    "max_price": original_price or price,
                    "currency": scraped_product.get('currency', 'KES'),
                    "discount_percent": discount_percent
                },
                "retailers": [{
                    "retailer_id": retailer.lower().replace(' ', '_'),
                    "name": retailer,
                    "retailer_name": retailer.title(),  # Add retailer_name field for frontend compatibility
                    "current_price": price,
                    "original_price": original_price,
                    "currency_code": scraped_product.get('currency', 'KES'),
                    "retailer_product_url": scraped_product.get('url'),
                    "in_stock": scraped_product.get('in_stock', True),
                    "last_updated": scraped_product.get('scraped_at'),
                    "rating": scraped_product.get('rating'),
                    "reviews_count": scraped_product.get('reviews_count')
                }],
                "tracking_info": {
                    "is_tracked": False,
                    "tracked_count": 0
                },
                "created_at": None,
                "updated_at": None,
                "source": "web_scraping",
                "scraped_at": scraped_product.get('scraped_at')
            }

        except Exception as e:
            logger.error(f"Error formatting scraped product: {str(e)}")
            return {}

    @classmethod
    def _extract_brand_from_name(cls, name: str) -> str:
        """
        Extract brand from product name
        """
        if not name:
            return ""

        name_lower = name.lower()
        brands = [
            'samsung', 'apple', 'iphone', 'huawei', 'xiaomi', 'oppo', 'tecno',
            'infinix', 'nokia', 'lg', 'sony', 'hp', 'dell', 'lenovo', 'asus',
            'acer', 'macbook', 'ipad', 'airpods'
        ]

        for brand in brands:
            if brand in name_lower:
                return brand.title()

        # Try to extract first word as brand
        words = name.split()
        if words:
            return words[0]

        return ""

    @classmethod
    def _guess_category_from_name(cls, name: str) -> str:
        """
        Guess product category from name
        """
        if not name:
            return "Other"

        name_lower = name.lower()

        if any(word in name_lower for word in ['phone', 'smartphone', 'mobile', 'iphone', 'galaxy']):
            return "Smartphones"
        elif any(word in name_lower for word in ['laptop', 'macbook', 'notebook', 'computer']):
            return "Laptops"
        elif any(word in name_lower for word in ['tablet', 'ipad']):
            return "Tablets"
        elif any(word in name_lower for word in ['headphone', 'earphone', 'airpods', 'earbuds']):
            return "Audio"
        elif any(word in name_lower for word in ['tv', 'television', 'monitor']):
            return "Electronics"
        elif any(word in name_lower for word in ['charger', 'cable', 'adapter', 'case', 'cover']):
            return "Accessories"
        else:
            return "Other"

    @classmethod
    def _calculate_relevance_score(cls, product_name: str, query: str) -> float:
        """
        Calculate relevance score for search results
        """
        if not product_name or not query:
            return 0.0

        product_name_lower = product_name.lower()
        query_lower = query.lower()

        # Exact match gets highest score
        if query_lower == product_name_lower:
            return 1.0

        # Check if query is contained in product name
        if query_lower in product_name_lower:
            return 0.8

        # Check word matches
        query_words = query_lower.split()
        product_words = product_name_lower.split()

        matching_words = sum(1 for word in query_words if word in product_words)
        if matching_words > 0:
            return 0.6 * (matching_words / len(query_words))

        # Partial word matches
        partial_matches = 0
        for query_word in query_words:
            for product_word in product_words:
                if query_word in product_word or product_word in query_word:
                    partial_matches += 1
                    break

        if partial_matches > 0:
            return 0.4 * (partial_matches / len(query_words))

        return 0.0
    
    @classmethod
    def get_categories(cls) -> List[Dict[str, Any]]:
        """
        Get all product categories
        
        Returns:
            List of categories with hierarchy
        """
        try:
            categories = Category.query.order_by(Category.name).all()
            
            # Build category tree
            category_dict = {}
            root_categories = []
            
            for category in categories:
                category_data = {
                    "category_id": category.category_id,
                    "name": category.name,
                    "image_url": category.image_url,
                    "parent_category_id": category.parent_category_id,
                    "subcategories": []
                }
                category_dict[category.category_id] = category_data
                
                if category.parent_category_id is None:
                    root_categories.append(category_data)
            
            # Build hierarchy
            for category in categories:
                if category.parent_category_id:
                    parent = category_dict.get(category.parent_category_id)
                    if parent:
                        parent["subcategories"].append(category_dict[category.category_id])
            
            return root_categories
            
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            abort(500, description="Internal server error")
    
    @classmethod
    def get_retailers(cls) -> List[Dict[str, Any]]:
        """
        Get all active retailers
        
        Returns:
            List of retailers
        """
        try:
            retailers = Retailer.query.filter_by(is_active=True).order_by(Retailer.name).all()
            
            result = []
            for retailer in retailers:
                retailer_data = {
                    "retailer_id": retailer.retailer_id,
                    "name": retailer.name,
                    "website_url": retailer.website_url,
                    "logo_url": retailer.logo_url,
                    "country_code": retailer.country_code
                }
                result.append(retailer_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting retailers: {str(e)}")
            abort(500, description="Internal server error")
    
    @classmethod
    def get_popular_products(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular products (for now, just recent products)
        
        Args:
            limit: Number of products to return
            
        Returns:
            List of popular products
        """
        try:
            products = Product.query.order_by(desc(Product.created_at)).limit(limit).all()
            
            result = []
            for product in products:
                product_data = cls._format_product_summary(product)
                result.append(product_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting popular products: {str(e)}")
            abort(500, description="Internal server error")
    
    @classmethod
    def _format_product_summary(cls, product: Product) -> Dict[str, Any]:
        """
        Format product data for summary view
        
        Args:
            product: Product instance
            
        Returns:
            Dict containing formatted product summary
        """
        # Get price information
        in_stock_retailers = [pr for pr in product.product_retailers if pr.in_stock]
        prices = [float(pr.current_price) for pr in in_stock_retailers]
        
        min_price = min(prices) if prices else None
        max_price = max(prices) if prices else None
        avg_price = sum(prices) / len(prices) if prices else None
        
        return {
            "product_id": product.product_id,
            "name": product.name,
            "description": product.description,
            "brand": product.brand,
            "model": product.model,
            "image_url": product.image_url,
            "category": {
                "category_id": product.category.category_id,
                "name": product.category.name
            } if product.category else None,
            "price_info": {
                "min_price": min_price,
                "max_price": max_price,
                "avg_price": round(avg_price, 2) if avg_price else None,
                "currency": "KES",
                "retailers_count": len(in_stock_retailers),
                "total_retailers": len(product.product_retailers)
            }
        }
    
    @classmethod
    def _format_product_details(cls, product: Product) -> Dict[str, Any]:
        """
        Format detailed product data
        
        Args:
            product: Product instance
            
        Returns:
            Dict containing detailed product information
        """
        # Get retailer information
        retailers_data = []
        for pr in product.product_retailers:
            retailer_data = {
                "retailer_id": pr.retailer.retailer_id,
                "retailer_name": pr.retailer.name,
                "retailer_logo": pr.retailer.logo_url,
                "current_price": float(pr.current_price),
                "currency": pr.currency_code,
                "in_stock": pr.in_stock,
                "product_url": pr.retailer_product_url,
                "last_updated": pr.last_updated.isoformat()
            }
            retailers_data.append(retailer_data)
        
        # Calculate price statistics
        in_stock_prices = [float(pr.current_price) for pr in product.product_retailers if pr.in_stock]
        
        return {
            "product_id": product.product_id,
            "name": product.name,
            "description": product.description,
            "brand": product.brand,
            "model": product.model,
            "image_url": product.image_url,
            "specifications": product.specifications,
            "category": {
                "category_id": product.category.category_id,
                "name": product.category.name,
                "image_url": product.category.image_url
            } if product.category else None,
            "price_info": {
                "min_price": min(in_stock_prices) if in_stock_prices else None,
                "max_price": max(in_stock_prices) if in_stock_prices else None,
                "avg_price": round(sum(in_stock_prices) / len(in_stock_prices), 2) if in_stock_prices else None,
                "currency": "KES"
            },
            "retailers": retailers_data,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat()
        }
