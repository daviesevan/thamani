"""
Real Zurimall scraper for extracting actual product data
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

class ZurimallScraper:
    """
    Real scraper for Zurimall e-commerce website
    """
    
    def __init__(self):
        self.base_url = "https://zurimall.co.ke"
        self.session = requests.Session()
        
        # Headers to avoid detection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        self.session.headers.update(self.headers)
    
    def search_products(self, query: str, max_pages: int = 3) -> List[Dict[str, Any]]:
        """
        Search for products on Zurimall
        
        Args:
            query: Search term
            max_pages: Maximum pages to scrape
            
        Returns:
            List of product data dictionaries
        """
        products = []
        
        try:
            logger.info(f"Searching Zurimall for: {query}")
            
            for page in range(1, max_pages + 1):
                # Zurimall search URL format - updated to match current structure
                search_url = f"{self.base_url}/shop"
                params = {
                    's': query,
                    'product_cat': 'mobile-phones',  # Focus on phones category
                    'post_type': 'product',
                    'paged': page
                }
                
                logger.info(f"Scraping Zurimall page {page}: {search_url}")
                
                # Add random delay to avoid being blocked
                time.sleep(random.uniform(2, 4))
                
                response = self.session.get(search_url, params=params, timeout=15)
                response.raise_for_status()
                
                # Check if we got a valid response
                if 'no products were found' in response.text.lower():
                    logger.info("No products found on this page")
                    break
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract products from current page
                page_products = self._extract_products_from_page(soup)
                products.extend(page_products)
                
                # If no products found on this page, stop
                if not page_products:
                    break
            
            logger.info(f"Found {len(products)} products from Zurimall")
            
        except Exception as e:
            logger.error(f"Error searching Zurimall: {str(e)}")
        
        return products[:20]  # Return max 20 products
    
    def _extract_products_from_page(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract product data from Zurimall search results page
        """
        products = []
        
        # Updated Zurimall product selectors
        product_selectors = [
            'li.product-type-simple',     # Simple product type
            'li.type-product',            # Standard product type
            '.products .product',         # Products in grid
            '.product-grid-item',         # Grid items
            '.product-small'              # Small product cards
        ]
        
        product_elements = []
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                product_elements = elements
                logger.info(f"Found {len(elements)} products using selector: {selector}")
                break
        
        if not product_elements:
            logger.warning("No product elements found with any selector")
            return products
        
        for element in product_elements:
            try:
                product_data = self._extract_single_product(element)
                if product_data:
                    products.append(product_data)
            except Exception as e:
                logger.error(f"Error extracting product: {str(e)}")
                continue
        
        return products
    
    def _extract_single_product(self, element) -> Optional[Dict[str, Any]]:
        """
        Extract data from a single product element
        """
        try:
            # Product name and link - updated selectors
            name_selectors = [
                'h2.woocommerce-loop-product__title',    # Main product title
                '.product-title',                        # Alternative title class
                '.name',                                 # Generic name class
                '.product-name a',                       # Product name with link
                '.product_title',                        # Single product title
                'h1.product_title',                      # Main product page title
                '.product-info h3'                       # Product info title
            ]
            
            name = None
            link = None
            product_link = None
            
            # First try to find name and link together
            for selector in name_selectors:
                name_element = element.select_one(selector)
                if name_element:
                    name = name_element.get_text(strip=True)
                    href = name_element.get('href')
                    if name and href and self._is_valid_zurimall_url(href):
                        if href.startswith('/'):
                            product_link = urljoin(self.base_url, href)
                        elif href.startswith('http'):
                            product_link = href
                        break
            
            # If no name found, try name-only selectors
            if not name:
                name_only_selectors = [
                    '.woocommerce-loop-product__title',
                    '.product-title',
                    'h3',
                    'h2',
                    '.entry-title'
                ]
                for selector in name_only_selectors:
                    name_element = element.select_one(selector)
                    if name_element:
                        name = name_element.get_text(strip=True)
                        if name:
                            break
            
            # If no link found, try link-only selectors
            if not product_link:
                link_selectors = [
                    'a[href*="/product/"]',
                    'a[href*="zurimall.co.ke"]',
                    'a'  # Any link as fallback
                ]
                for selector in link_selectors:
                    link_element = element.select_one(selector)
                    if link_element:
                        href = link_element.get('href')
                        if href and self._is_valid_zurimall_url(href):
                            if href.startswith('/'):
                                product_link = urljoin(self.base_url, href)
                            elif href.startswith('http'):
                                product_link = href
                            break
            
            if not name:
                return None
            
            # Updated price selectors
            price_selectors = [
                'span.price .amount',                   # Standard price amount
                '.price ins .amount',                   # Sale price
                'p.price span.amount',                  # Paragraph price
                '.product-price .amount',               # Product price
                '.summary .price .amount',              # Summary price
                '.regular-price',                       # Regular price
                'span[data-price]'                      # Data attribute price
            ]
            
            price = None
            original_price = None
            
            for selector in price_selectors:
                price_element = element.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    extracted_price = self._extract_price_from_text(price_text)
                    if extracted_price:
                        price = extracted_price
                        break
            
            # Check for original price (crossed out)
            original_price_selectors = [
                '.price del .woocommerce-Price-amount',  # Deleted price
                '.price .was',                           # Was price
                'del .amount'                            # Deleted amount
            ]
            
            for selector in original_price_selectors:
                orig_element = element.select_one(selector)
                if orig_element:
                    orig_text = orig_element.get_text(strip=True)
                    original_price = self._extract_price_from_text(orig_text)
                    break
            
            # Updated image selectors
            image_url = None
            img_selectors = [
                '.product-gallery-image img',            # Main product gallery
                '.product-image img[srcset]',           # Responsive images
                '.attachment-woocommerce_thumbnail',    # WooCommerce thumbnail
                '.product-thumb img',                   # Product thumbnail
                '.wp-post-image',                      # WordPress featured image
                'img.lazy-load'                        # Lazy loaded images
            ]
            
            for selector in img_selectors:
                img_element = element.select_one(selector)
                if img_element:
                    img_src = img_element.get('src') or img_element.get('data-src') or img_element.get('data-lazy-src')
                    if img_src and 'http' in img_src:
                        image_url = img_src
                        break
                    elif img_src:
                        image_url = urljoin(self.base_url, img_src)
                        break
            
            # Build product data
            product_data = {
                'name': name,
                'price': price,
                'original_price': original_price,
                'currency': 'KES',
                'url': product_link,
                'image_url': image_url,
                'retailer': 'Zurimall',
                'retailer_id': 'zurimall_ke',
                'in_stock': True,  # Assume in stock if listed
                'scraped_at': time.time()
            }
            
            # Only return if we have essential data
            if product_data['name'] and product_data['price']:
                return product_data
            
        except Exception as e:
            logger.error(f"Error extracting single product: {str(e)}")
        
        return None
    
    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """
        Extract price from text string
        """
        if not text:
            return None
        
        # Remove currency symbols and clean text
        cleaned_text = re.sub(r'[KSh,\s]', '', text)
        
        # Find price pattern
        price_match = re.search(r'(\d+(?:\.\d{2})?)', cleaned_text)
        if price_match:
            try:
                return float(price_match.group(1))
            except ValueError:
                pass
        
        return None
    
    def _is_valid_zurimall_url(self, href: str) -> bool:
        """
        Check if a URL is a valid Zurimall product URL
        """
        if not href:
            return False
        
        # Valid Zurimall product URL patterns
        valid_patterns = [
            '/product/',
            'zurimall.co.ke/product/',
            'zurimall.co.ke'
        ]
        
        return any(pattern in href for pattern in valid_patterns)
    
    def get_product_details(self, product_url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific product
        """
        try:
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(product_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract detailed product information
            details = {}
            
            # Product description
            desc_selectors = [
                '.woocommerce-product-details__short-description',
                '.product-description',
                '.entry-content'
            ]
            
            for selector in desc_selectors:
                desc_element = soup.select_one(selector)
                if desc_element:
                    details['description'] = desc_element.get_text(strip=True)
                    break
            
            # Product specifications
            spec_selectors = [
                '.woocommerce-product-attributes',
                '.product-specs',
                '.specifications'
            ]
            
            for selector in spec_selectors:
                spec_element = soup.select_one(selector)
                if spec_element:
                    details['specifications'] = spec_element.get_text(strip=True)
                    break
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting product details: {str(e)}")
            return None 