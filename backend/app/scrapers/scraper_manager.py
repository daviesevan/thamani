"""
Unified scraper manager for coordinating all retailer scrapers
"""
import logging
import time
import random
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .jumia_scraper import JumiaScraper
from .kilimall_scraper import KilimallScraper
from .jiji_scraper import JijiScraper
from .zurimall_scraper import ZurimallScraper
from .kenyatronics_scraper import KenyatronicsScraper

logger = logging.getLogger(__name__)

class ScraperManager:
    """
    Manages all retailer scrapers and coordinates scraping operations
    """
    
    def __init__(self):
        self.scrapers = {
            'jumia': JumiaScraper(),
            'kilimall': KilimallScraper(),
            'jiji': JijiScraper(),
            'zurimall': ZurimallScraper(),
            'kenyatronics': KenyatronicsScraper()
        }
        self.lock = threading.Lock()
    
    def search_all_retailers(self, query: str, max_pages_per_retailer: int = 2, 
                           max_workers: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for products across all retailers simultaneously
        
        Args:
            query: Search term
            max_pages_per_retailer: Maximum pages to scrape per retailer
            max_workers: Maximum concurrent scrapers
            
        Returns:
            Dictionary with retailer names as keys and product lists as values
        """
        results = {}
        
        # Use ThreadPoolExecutor for concurrent scraping
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit scraping tasks
            future_to_retailer = {}
            
            for retailer_name, scraper in self.scrapers.items():
                future = executor.submit(
                    self._safe_search_retailer, 
                    retailer_name, 
                    scraper, 
                    query, 
                    max_pages_per_retailer
                )
                future_to_retailer[future] = retailer_name
            
            # Collect results as they complete
            for future in as_completed(future_to_retailer):
                retailer_name = future_to_retailer[future]
                try:
                    products = future.result(timeout=60)  # 60 second timeout per retailer
                    results[retailer_name] = products
                    logger.info(f"Completed scraping {retailer_name}: {len(products)} products")
                except Exception as e:
                    logger.error(f"Error scraping {retailer_name}: {str(e)}")
                    results[retailer_name] = []
        
        return results
    
    def _safe_search_retailer(self, retailer_name: str, scraper, query: str, 
                            max_pages: int) -> List[Dict[str, Any]]:
        """
        Safely search a single retailer with error handling
        """
        try:
            logger.info(f"Starting {retailer_name} scraping for query: {query}")
            
            # Add random delay to stagger requests
            time.sleep(random.uniform(0, 3))
            
            products = scraper.search_products(query, max_pages)
            
            logger.info(f"Completed {retailer_name} scraping: {len(products)} products found")
            return products
            
        except Exception as e:
            logger.error(f"Error in {retailer_name} scraper: {str(e)}")
            return []
    
    def search_specific_retailers(self, query: str, retailer_names: List[str], 
                                max_pages: int = 2) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search specific retailers only
        
        Args:
            query: Search term
            retailer_names: List of retailer names to search
            max_pages: Maximum pages per retailer
            
        Returns:
            Dictionary with results from specified retailers
        """
        results = {}
        
        for retailer_name in retailer_names:
            if retailer_name.lower() in self.scrapers:
                scraper = self.scrapers[retailer_name.lower()]
                try:
                    products = scraper.search_products(query, max_pages)
                    results[retailer_name] = products
                    logger.info(f"Scraped {retailer_name}: {len(products)} products")
                    
                    # Add delay between retailers
                    time.sleep(random.uniform(2, 5))
                    
                except Exception as e:
                    logger.error(f"Error scraping {retailer_name}: {str(e)}")
                    results[retailer_name] = []
            else:
                logger.warning(f"Scraper not available for {retailer_name}")
                results[retailer_name] = []
        
        return results
    
    def get_product_details(self, product_url: str, retailer_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed product information from a specific retailer
        
        Args:
            product_url: URL of the product
            retailer_name: Name of the retailer
            
        Returns:
            Detailed product information or None
        """
        retailer_key = retailer_name.lower()
        
        if retailer_key in self.scrapers:
            try:
                scraper = self.scrapers[retailer_key]
                return scraper.get_product_details(product_url)
            except Exception as e:
                logger.error(f"Error getting product details from {retailer_name}: {str(e)}")
                return None
        else:
            logger.warning(f"No scraper available for {retailer_name}")
            return None
    
    def aggregate_results(self, search_results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Aggregate and deduplicate results from multiple retailers
        
        Args:
            search_results: Results from search_all_retailers
            
        Returns:
            Combined and deduplicated product list
        """
        all_products = []
        
        for retailer_name, products in search_results.items():
            for product in products:
                # Add retailer info if not present
                if 'retailer' not in product:
                    product['retailer'] = retailer_name
                
                all_products.append(product)
        
        # Sort by price (lowest first), handling None values
        all_products.sort(key=lambda x: x.get('price') or float('inf'))
        
        return all_products
    
    def find_similar_products(self, search_results: Dict[str, List[Dict[str, Any]]], 
                            similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Find similar products across retailers for price comparison
        
        Args:
            search_results: Results from multiple retailers
            similarity_threshold: Minimum similarity score to consider products similar
            
        Returns:
            List of product groups with similar items from different retailers
        """
        from difflib import SequenceMatcher
        
        all_products = self.aggregate_results(search_results)
        similar_groups = []
        processed_indices = set()
        
        for i, product1 in enumerate(all_products):
            if i in processed_indices:
                continue
            
            similar_group = [product1]
            processed_indices.add(i)
            
            for j, product2 in enumerate(all_products[i+1:], i+1):
                if j in processed_indices:
                    continue
                
                # Calculate name similarity
                similarity = SequenceMatcher(None, 
                                           product1['name'].lower(), 
                                           product2['name'].lower()).ratio()
                
                if similarity >= similarity_threshold:
                    similar_group.append(product2)
                    processed_indices.add(j)
            
            # Only include groups with products from multiple retailers
            if len(similar_group) > 1:
                retailers_in_group = set(p['retailer'] for p in similar_group)
                if len(retailers_in_group) > 1:
                    similar_groups.append({
                        'products': similar_group,
                        'retailers': list(retailers_in_group),
                        'price_range': {
                            'min': min(p['price'] for p in similar_group if p.get('price')),
                            'max': max(p['price'] for p in similar_group if p.get('price'))
                        }
                    })
        
        return similar_groups
    
    def scrape_categories(self, categories: Dict[str, str], max_pages: int = 2) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrape specific categories from retailers
        
        Args:
            categories: Dict mapping retailer names to category URLs/paths
            max_pages: Maximum pages to scrape per category
            
        Returns:
            Results from category scraping
        """
        results = {}
        
        for retailer_name, category_path in categories.items():
            retailer_key = retailer_name.lower()
            
            if retailer_key in self.scrapers:
                try:
                    scraper = self.scrapers[retailer_key]
                    products = scraper.search_category(category_path, max_pages)
                    results[retailer_name] = products
                    
                    logger.info(f"Scraped {retailer_name} category: {len(products)} products")
                    
                    # Add delay between categories
                    time.sleep(random.uniform(3, 6))
                    
                except Exception as e:
                    logger.error(f"Error scraping {retailer_name} category: {str(e)}")
                    results[retailer_name] = []
            else:
                logger.warning(f"No scraper available for {retailer_name}")
                results[retailer_name] = []
        
        return results
    
    def get_scraper_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status information for all scrapers
        
        Returns:
            Status information for each scraper
        """
        status = {}
        
        for retailer_name, scraper in self.scrapers.items():
            try:
                # Test basic connectivity
                test_response = scraper.session.get(scraper.base_url, timeout=10)
                
                status[retailer_name] = {
                    'available': test_response.status_code == 200,
                    'base_url': scraper.base_url,
                    'status_code': test_response.status_code,
                    'response_time': test_response.elapsed.total_seconds()
                }
                
            except Exception as e:
                status[retailer_name] = {
                    'available': False,
                    'base_url': scraper.base_url,
                    'error': str(e)
                }
        
        return status
    
    def search_with_pagination_control(self, query: str, total_products_limit: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search with intelligent pagination control to limit total products scraped
        
        Args:
            query: Search term
            total_products_limit: Maximum total products to scrape across all retailers
            
        Returns:
            Search results with controlled pagination
        """
        results = {}
        products_per_retailer = total_products_limit // len(self.scrapers)
        
        for retailer_name, scraper in self.scrapers.items():
            try:
                logger.info(f"Scraping {retailer_name} with limit of {products_per_retailer} products")
                
                products = []
                page = 1
                
                while len(products) < products_per_retailer:
                    page_products = scraper.search_products(query, max_pages=1)
                    
                    if not page_products:
                        break
                    
                    products.extend(page_products)
                    page += 1
                    
                    # Add delay between pages
                    time.sleep(random.uniform(2, 4))
                
                # Limit to desired number
                results[retailer_name] = products[:products_per_retailer]
                
                logger.info(f"Collected {len(results[retailer_name])} products from {retailer_name}")
                
            except Exception as e:
                logger.error(f"Error in controlled scraping for {retailer_name}: {str(e)}")
                results[retailer_name] = []
        
        return results
