"""
Real Jiji Kenya scraper for extracting actual classified ad data
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

class JijiScraper:
    """
    Real scraper for Jiji Kenya classified ads website
    """
    
    def __init__(self):
        self.base_url = "https://jiji.co.ke"
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
        Search for products on Jiji Kenya
        
        Args:
            query: Search term
            max_pages: Maximum pages to scrape
            
        Returns:
            List of product data dictionaries
        """
        products = []
        
        try:
            # Jiji uses a search endpoint with query parameters
            search_url = f"{self.base_url}/search"

            for page in range(1, max_pages + 1):
                logger.info(f"Scraping Jiji page {page} for query: {query}")

                # Add delay to avoid being blocked
                time.sleep(random.uniform(3, 6))

                # Build search parameters
                params = {
                    'query': query,
                    'page': page
                }

                response = self.session.get(search_url, params=params, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract products from page
                page_products = self._extract_products_from_page(soup)
                
                if not page_products:
                    logger.info(f"No products found on page {page}, stopping")
                    break
                
                products.extend(page_products)
                logger.info(f"Found {len(page_products)} products on page {page}")
                
        except Exception as e:
            logger.error(f"Error scraping Jiji search: {str(e)}")
        
        return products
    
    def _extract_products_from_page(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract product data from Jiji search results page
        """
        products = []
        
        # Jiji product selectors - updated based on actual HTML structure
        product_selectors = [
            '.b-list-advert__gallery__item',       # Main product containers
            '.js-advert-list-item',                # Items with JS class
            '.b-list-advert-base',                 # Base advert elements
            '.qa-advert-list-item'                 # QA attribute items
        ]

        product_elements = []
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                product_elements = elements
                logger.info(f"Found {len(elements)} products with selector: {selector}")
                break
        
        if not product_elements:
            # Fallback: look for any links that seem to be ads
            ad_links = soup.select('a[href*="/ads/"]')
            if ad_links:
                logger.info(f"Found {len(ad_links)} ad links as fallback")
                for link in ad_links[:20]:  # Limit to avoid duplicates
                    try:
                        product_data = self._extract_from_link(link)
                        if product_data:
                            products.append(product_data)
                    except Exception as e:
                        logger.error(f"Error extracting from ad link: {str(e)}")
                        continue
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
        Extract data from a single Jiji ad element
        """
        try:
            # Updated selectors for current Jiji structure
            name = None
            product_link = None

            # Try to get the main ad link - Jiji structure has the link as the main element
            if element.name == 'a' and 'qa-advert-list-item' in element.get('class', []):
                # The element itself is the link
                product_link = urljoin(self.base_url, element.get('href', ''))
                name = element.get('title', '').strip()
            else:
                # Look for link within the element
                link_selectors = [
                    'a.qa-advert-list-item',                   # Main product links
                    'a.b-list-advert-base',                    # Base advert links
                    'a[href*=".html"]'                         # Any Jiji product link
                ]

                for selector in link_selectors:
                    link_element = element.select_one(selector)
                    if link_element:
                        product_link = urljoin(self.base_url, link_element.get('href', ''))
                        name = link_element.get('title', '').strip()
                        if product_link:
                            break

            # If we didn't get the name from the link, try the title selectors
            if not name:
                title_selectors = [
                    '.qa-advert-title',                    # Main title with QA attribute
                    '.b-advert-title-inner',               # Inner title element
                    '.qa-advert-list-item-title',          # List item title
                    '.b-list-advert-base__item-title'      # Base item title
                ]

                for selector in title_selectors:
                    title_element = element.select_one(selector)
                    if title_element:
                        name = title_element.get_text(strip=True)
                        if name:
                            break
            
            if not name:
                return None
            
            # Price extraction - updated selectors based on actual HTML structure
            price_selectors = [
                '.qa-advert-price',                    # Main price with QA attribute
                '.b-list-advert__price-base',          # Price base container
                '.b-list-advert-base__data__price',    # Price data container
                '.b-list-advert__price'                # General price class
            ]
            
            price = None
            for selector in price_selectors:
                price_element = element.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    # Handle Jiji's "KSh" prefix and number formatting
                    price = self._extract_price_from_text(price_text)
                    if price:
                        break
            
            # Location
            location = None
            location_selectors = [
                '[data-testid="advert-location"]',
                '.advert-location',
                '.location',
                '.ad-location'
            ]
            
            for selector in location_selectors:
                loc_element = element.select_one(selector)
                if loc_element:
                    location = loc_element.get_text(strip=True)
                    break
            
            # Product image - Jiji uses picture elements with img inside
            image_url = None
            img_selectors = [
                'picture img',                         # Images inside picture elements
                '.b-list-advert-base__img img',        # Images in base img containers
                'img[alt*="Photo"]',                   # Images with Photo in alt text
                'img'                                  # Any img element
            ]

            for selector in img_selectors:
                img_element = element.select_one(selector)
                if img_element:
                    img_src = img_element.get('src') or img_element.get('data-src') or img_element.get('data-lazy')
                    if img_src and img_src.startswith('http'):
                        image_url = img_src
                        break
            
            # Posted date/time
            posted_time = None
            time_selectors = [
                '[data-testid="advert-date"]',
                '.advert-date',
                '.posted-time',
                '.date'
            ]
            
            for selector in time_selectors:
                time_element = element.select_one(selector)
                if time_element:
                    posted_time = time_element.get_text(strip=True)
                    break
            
            # Seller info
            seller = None
            seller_selectors = [
                '.seller-name',
                '.advertiser',
                '.user-name'
            ]
            
            for selector in seller_selectors:
                seller_element = element.select_one(selector)
                if seller_element:
                    seller = seller_element.get_text(strip=True)
                    break
            
            # Build product data
            product_data = {
                'name': name,
                'price': price,
                'currency': 'KES',
                'url': product_link,
                'image_url': image_url,
                'location': location,
                'posted_time': posted_time,
                'seller': seller,
                'retailer': 'Jiji Kenya',
                'retailer_id': 'jiji_ke',
                'in_stock': True,  # Classified ads are usually available
                'scraped_at': time.time()
            }
            
            # Only return if we have essential data
            if product_data['name'] and (product_data['price'] or product_data['url']):
                return product_data
            
        except Exception as e:
            logger.error(f"Error extracting single Jiji product: {str(e)}")
        
        return None
    
    def _extract_from_link(self, link_element) -> Optional[Dict[str, Any]]:
        """
        Extract basic product info from an ad link element
        """
        try:
            name = link_element.get_text(strip=True) or link_element.get('title', '').strip()
            if not name:
                return None
            
            product_link = urljoin(self.base_url, link_element.get('href'))
            
            # Try to find price and other info in parent elements
            price = None
            location = None
            image_url = None
            
            parent = link_element.find_parent()
            if parent:
                # Look for price
                price_element = parent.select_one('.price, .amount, .cost')
                if price_element:
                    price = self._extract_price_from_text(price_element.get_text(strip=True))
                
                # Look for location
                loc_element = parent.select_one('.location, .area')
                if loc_element:
                    location = loc_element.get_text(strip=True)
                
                # Look for image
                img_element = parent.select_one('img')
                if img_element:
                    img_src = img_element.get('src') or img_element.get('data-src')
                    if img_src:
                        image_url = urljoin(self.base_url, img_src) if not img_src.startswith('http') else img_src
            
            return {
                'name': name,
                'price': price,
                'currency': 'KES',
                'url': product_link,
                'image_url': image_url,
                'location': location,
                'retailer': 'Jiji Kenya',
                'retailer_id': 'jiji_ke',
                'in_stock': True,
                'scraped_at': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error extracting from Jiji link: {str(e)}")
            return None
    
    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """Extract price value from text"""
        if not text:
            return None
            
        try:
            # Remove any non-price text
            text = text.lower().strip()
            # Handle "call" or "contact" prices
            if 'call' in text or 'contact' in text:
                return None
                
            # Remove currency symbols and formatting
            price_text = (text.replace('ksh', '').replace('kshs', '').replace('sh', '')
                            .replace('ksh.', '').replace('kes', '').replace('₹', '')
                            .replace(',', '').replace('/-', '').strip())
            
            # Handle ranges by taking the lower price
            if '-' in price_text:
                price_text = price_text.split('-')[0].strip()
                
            # Handle "k" and "m" abbreviations
            if 'k' in price_text.lower():
                price_text = price_text.lower().replace('k', '').strip()
                return float(price_text) * 1000
            elif 'm' in price_text.lower():
                price_text = price_text.lower().replace('m', '').strip()
                return float(price_text) * 1000000
                
            # Convert to float
            return float(price_text)
        except (ValueError, TypeError):
            return None
    
    def get_product_details(self, product_url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific Jiji ad
        """
        try:
            time.sleep(random.uniform(2, 4))
            
            response = self.session.get(product_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {
                'url': product_url,
                'retailer': 'Jiji Kenya'
            }
            
            # Ad title
            title_element = soup.select_one('h1, .ad-title, [data-testid="ad-title"]')
            if title_element:
                details['name'] = title_element.get_text(strip=True)
            
            # Price
            price_element = soup.select_one('.price, .ad-price, [data-testid="ad-price"]')
            if price_element:
                details['price'] = self._extract_price_from_text(price_element.get_text(strip=True))
            
            # Description
            desc_element = soup.select_one('.description, .ad-description, [data-testid="ad-description"]')
            if desc_element:
                details['description'] = desc_element.get_text(strip=True)[:500]
            
            # Location
            loc_element = soup.select_one('.location, .ad-location')
            if loc_element:
                details['location'] = loc_element.get_text(strip=True)
            
            # Images
            img_elements = soup.select('.gallery img, .ad-images img, .image-gallery img')
            if img_elements:
                details['images'] = []
                for img in img_elements:
                    img_src = img.get('src') or img.get('data-src')
                    if img_src:
                        full_url = urljoin(self.base_url, img_src) if not img_src.startswith('http') else img_src
                        details['images'].append(full_url)
            
            # Seller information
            seller_element = soup.select_one('.seller-info, .advertiser-info')
            if seller_element:
                seller_name = seller_element.select_one('.name, .seller-name')
                if seller_name:
                    details['seller'] = seller_name.get_text(strip=True)
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting Jiji product details: {str(e)}")
            return None
    
    def search_category(self, category_path: str, max_pages: int = 2) -> List[Dict[str, Any]]:
        """
        Scrape products from a specific category
        """
        products = []
        
        try:
            category_url = f"{self.base_url}{category_path}"
            
            for page in range(1, max_pages + 1):
                page_url = f"{category_url}?page={page}" if page > 1 else category_url
                
                time.sleep(random.uniform(3, 6))
                
                response = self.session.get(page_url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                page_products = self._extract_products_from_page(soup)
                
                if not page_products:
                    break
                
                products.extend(page_products)
                
        except Exception as e:
            logger.error(f"Error scraping Jiji category: {str(e)}")
        
        return products
