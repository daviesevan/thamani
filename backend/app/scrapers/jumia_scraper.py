"""
Real Jumia Kenya scraper for extracting actual product data
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)

class JumiaScraper:
    """
    Real scraper for Jumia Kenya e-commerce website
    """
    
    def __init__(self):
        self.base_url = "https://www.jumia.co.ke"
        self.session = requests.Session()

        # Realistic headers to avoid detection
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

        # Set cookies to bypass consent page
        self.session.cookies.update({
            'cookie_consent': 'accepted',
            'jumia_consent': '1',
            '_gcl_au': '1.1.1234567890.1234567890'
        })
    
    def search_products(self, query: str, max_pages: int = 3) -> List[Dict[str, Any]]:
        """
        Search for products on Jumia Kenya
        
        Args:
            query: Search term (e.g., "samsung galaxy", "iphone", "laptop")
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of product dictionaries with real data
        """
        products = []
        
        try:
            # Jumia search URL format
            search_url = f"{self.base_url}/catalog/?q={query.replace(' ', '+')}"
            
            for page in range(1, max_pages + 1):
                page_url = f"{search_url}&page={page}" if page > 1 else search_url
                
                logger.info(f"Scraping Jumia page {page}: {page_url}")
                
                # Add random delay to avoid being blocked
                time.sleep(random.uniform(2, 4))
                
                response = self.session.get(page_url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract products from current page
                page_products = self._extract_products_from_page(soup, page_url)
                
                if not page_products:
                    logger.info(f"No products found on page {page}, stopping")
                    break
                
                products.extend(page_products)
                logger.info(f"Found {len(page_products)} products on page {page}")
                
        except Exception as e:
            logger.error(f"Error scraping Jumia search: {str(e)}")
        
        return products
    
    def _extract_products_from_page(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """
        Extract product data from a Jumia search results page
        """
        products = []
        
        # Check if we hit a cookie consent page
        if soup.select('.cookie-consent, [class*="cookie"], [class*="consent"]'):
            logger.warning("Hit cookie consent page, trying to continue...")

        # Updated selectors for current Jumia structure (2024)
        product_selectors = [
            'article[data-catalog-id]',  # Main product articles
            '.prd._fb.col.c-prd',  # Updated product class
            '.prd',  # Product class
            '[data-id]',  # Products with data-id
            '.core',  # Core product container
            'article.prd',  # Article with prd class
            '.itm'  # Item class
        ]

        product_elements = []
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                product_elements = elements
                logger.info(f"Found {len(elements)} products using selector: {selector}")
                break

        if not product_elements:
            logger.warning(f"No products found on page: {page_url}")
            # Debug: log page structure
            logger.debug(f"Page title: {soup.title.string if soup.title else 'No title'}")
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
            # Product name and link - updated selectors for 2024 Jumia
            name_selectors = [
                '.name a',  # Name with link
                '.prd-name a',  # Product name with link
                'h3 a',  # H3 with link
                '.core a',  # Core with link
                '[data-catalog-id] a',  # Data catalog with link
                'a[href*="/"]',  # Any link with href
                '.info a'  # Info section with link
            ]

            name = None
            product_link = None

            # First try to find name and link together
            for selector in name_selectors:
                name_element = element.select_one(selector)
                if name_element:
                    name = name_element.get_text(strip=True)
                    href = name_element.get('href')
                    # Only accept direct product links (not login redirects)
                    if href and self._is_valid_product_url(href):
                        if href.startswith('/'):
                            product_link = urljoin(self.base_url, href)
                        elif href.startswith('http'):
                            product_link = href
                    if name and product_link:
                        break

            # If no name found, try name-only selectors
            if not name:
                name_only_selectors = [
                    '.name',
                    '.prd-name',
                    'h3',
                    '.info h3',
                    '.title'
                ]
                for selector in name_only_selectors:
                    name_element = element.select_one(selector)
                    if name_element:
                        name = name_element.get_text(strip=True)
                        break

            # If no link found, try link-only selectors
            if not product_link:
                link_selectors = [
                    'a[href*=".html"]',  # Direct product links
                    'a[href*="/"]',
                    'a[href*="jumia.co.ke"]'
                ]
                for selector in link_selectors:
                    link_element = element.select_one(selector)
                    if link_element:
                        href = link_element.get('href')
                        # Use the same validation as above
                        if href and self._is_valid_product_url(href):
                            if href.startswith('/'):
                                product_link = urljoin(self.base_url, href)
                            elif href.startswith('http'):
                                product_link = href
                            break

            # Clean up product name
            if name:
                # Remove price information and extra text
                name = re.sub(r'KSh\s*[\d,]+', '', name)  # Remove prices
                name = re.sub(r'\d+%', '', name)  # Remove percentages
                name = re.sub(r'\d+\s*out\s*of\s*\d+', '', name)  # Remove ratings
                name = re.sub(r'\(\d+\)', '', name)  # Remove review counts
                name = re.sub(r'\s+', ' ', name).strip()  # Clean whitespace
            
            if not name:
                return None
            
            # Price extraction
            price_selectors = [
                '.prc',
                '.price',
                '.prd-price',
                '.current-price',
                '.-b.-tal.-fs24'
            ]
            
            price = None
            original_price = None
            
            for selector in price_selectors:
                price_element = element.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    price = self._extract_price_from_text(price_text)
                    if price:
                        break
            
            # Original price (if on sale)
            original_price_selectors = [
                '.old-price',
                '.original-price',
                '.crossed-out-price',
                '.-tal.-gy5.-lthr'
            ]
            
            for selector in original_price_selectors:
                orig_element = element.select_one(selector)
                if orig_element:
                    orig_text = orig_element.get_text(strip=True)
                    original_price = self._extract_price_from_text(orig_text)
                    break
            
            # Product image
            image_selectors = [
                'img',
                '.image img',
                '.prd-image img'
            ]
            
            image_url = None
            for selector in image_selectors:
                img_element = element.select_one(selector)
                if img_element:
                    img_src = img_element.get('src') or img_element.get('data-src')
                    if img_src:
                        image_url = urljoin(self.base_url, img_src)
                        break
            
            # Rating
            rating = None
            rating_element = element.select_one('.stars, .rating, [data-rating]')
            if rating_element:
                rating_text = rating_element.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Discount percentage
            discount = None
            discount_element = element.select_one('.discount, .sale-flag, .-paxs')
            if discount_element:
                discount_text = discount_element.get_text(strip=True)
                discount_match = re.search(r'(\d+)%', discount_text)
                if discount_match:
                    discount = int(discount_match.group(1))
            
            # Reviews count
            reviews_count = None
            reviews_element = element.select_one('.rev, .reviews-count')
            if reviews_element:
                reviews_text = reviews_element.get_text(strip=True)
                reviews_match = re.search(r'(\d+)', reviews_text)
                if reviews_match:
                    reviews_count = int(reviews_match.group(1))
            
            # Build product data
            product_data = {
                'name': name,
                'price': price,
                'original_price': original_price,
                'currency': 'KES',
                'url': product_link,
                'image_url': image_url,
                'rating': rating,
                'reviews_count': reviews_count,
                'discount_percent': discount,
                'retailer': 'Jumia Kenya',
                'retailer_id': 'jumia_ke',
                'in_stock': True,  # Assume in stock if listed
                'scraped_at': time.time()
            }
            
            # Only return if we have essential data
            if product_data['name'] and product_data['price']:
                return product_data
            
        except Exception as e:
            logger.error(f"Error extracting single product: {str(e)}")

        return None

    def _is_valid_product_url(self, href: str) -> bool:
        """
        Check if a URL is a valid product URL (not a login redirect)
        """
        if not href:
            return False

        # Skip login/account/redirect URLs
        invalid_patterns = [
            'login', 'account', 'customer', 'auth', 'signin', 'signup',
            'tkWl=', 'return=', 'redirect'
        ]

        for pattern in invalid_patterns:
            if pattern in href.lower():
                return False

        # Prefer direct product URLs
        valid_patterns = [
            '.html',  # Direct product pages
            '/catalog/',  # Catalog pages
            '-\d+\.html',  # Product ID pattern
        ]

        for pattern in valid_patterns:
            if re.search(pattern, href):
                return True

        # If no specific pattern matches, check if it's a reasonable product path
        return href.startswith('/') and len(href) > 10
    
    def _extract_price_from_text(self, price_text: str) -> Optional[float]:
        """
        Extract numeric price from text like "KSh 45,000" or "45,000"
        """
        if not price_text:
            return None
        
        # Remove currency symbols and clean text
        cleaned = re.sub(r'[KSh\s,]', '', price_text)
        
        # Find numeric value
        price_match = re.search(r'(\d+\.?\d*)', cleaned)
        if price_match:
            try:
                return float(price_match.group(1))
            except ValueError:
                pass
        
        return None
    
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
            details = {
                'url': product_url,
                'retailer': 'Jumia Kenya'
            }
            
            # Product name
            name_element = soup.select_one('h1, .name, .-fs20.-pts.-pbxs')
            if name_element:
                details['name'] = name_element.get_text(strip=True)
            
            # Price
            price_element = soup.select_one('.prc, .-b.-tal.-fs24')
            if price_element:
                details['price'] = self._extract_price_from_text(price_element.get_text(strip=True))
            
            # Description
            desc_element = soup.select_one('.markup, .description, .-pvs')
            if desc_element:
                details['description'] = desc_element.get_text(strip=True)[:500]  # Limit length
            
            # Images
            img_elements = soup.select('.thumbs img, .gallery img')
            if img_elements:
                details['images'] = [urljoin(self.base_url, img.get('src') or img.get('data-src')) 
                                   for img in img_elements if img.get('src') or img.get('data-src')]
            
            # Specifications
            specs = {}
            spec_elements = soup.select('.key-features li, .specifications tr')
            for spec in spec_elements:
                spec_text = spec.get_text(strip=True)
                if ':' in spec_text:
                    key, value = spec_text.split(':', 1)
                    specs[key.strip()] = value.strip()
            
            if specs:
                details['specifications'] = specs
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting product details: {str(e)}")
            return None
    
    def search_category(self, category_url: str, max_pages: int = 2) -> List[Dict[str, Any]]:
        """
        Scrape products from a specific category page
        """
        products = []
        
        try:
            for page in range(1, max_pages + 1):
                page_url = f"{category_url}?page={page}" if page > 1 else category_url
                
                time.sleep(random.uniform(2, 4))
                
                response = self.session.get(page_url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                page_products = self._extract_products_from_page(soup, page_url)
                
                if not page_products:
                    break
                
                products.extend(page_products)
                
        except Exception as e:
            logger.error(f"Error scraping category: {str(e)}")
        
        return products
