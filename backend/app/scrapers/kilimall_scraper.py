"""
Real Kilimall scraper for extracting actual product data
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import json
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

class KilimallScraper:
    """
    Real scraper for Kilimall e-commerce website
    """
    
    def __init__(self):
        self.base_url = "https://www.kilimall.co.ke"
        self.session = requests.Session()
        
        # Headers to mimic real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        self.session.headers.update(self.headers)
    
    def search_products(self, query: str, max_pages: int = 3) -> List[Dict[str, Any]]:
        """
        Search for products on Kilimall
        
        Args:
            query: Search term
            max_pages: Maximum pages to scrape
            
        Returns:
            List of product data dictionaries
        """
        products = []
        
        try:
            # Kilimall search URL format
            search_url = f"{self.base_url}/new/search"
            
            for page in range(1, max_pages + 1):
                logger.info(f"Scraping Kilimall page {page} for query: {query}")
                
                # Add delay
                time.sleep(random.uniform(2, 5))
                
                # Search parameters
                params = {
                    'keyword': query,
                    'page': page,
                    'sort': 'default'
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
            logger.error(f"Error scraping Kilimall search: {str(e)}")
        
        return products
    
    def _extract_products_from_page(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract product data from Kilimall search results page
        """
        products = []
        
        # Kilimall product selectors
        product_selectors = [
            '.goods-item',
            '.product-item',
            '.item-wrap',
            '[data-goods-id]',
            '.goods-list .item'
        ]
        
        product_elements = []
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                product_elements = elements
                logger.info(f"Found {len(elements)} products with selector: {selector}")
                break
        
        if not product_elements:
            # Try alternative approach - look for product links
            product_links = soup.select('a[href*="/goods/"]')
            if product_links:
                logger.info(f"Found {len(product_links)} product links")
                for link in product_links[:20]:  # Limit to avoid duplicates
                    try:
                        product_data = self._extract_from_link(link)
                        if product_data:
                            products.append(product_data)
                    except Exception as e:
                        logger.error(f"Error extracting from link: {str(e)}")
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
        Extract data from a single product element
        """
        try:
            # Product name
            name_selectors = [
                '.goods-name',
                '.product-name',
                '.title',
                'h3',
                '.name a',
                'a[title]'
            ]
            
            name = None
            product_link = None
            
            for selector in name_selectors:
                name_element = element.select_one(selector)
                if name_element:
                    name = name_element.get_text(strip=True) or name_element.get('title', '').strip()
                    if name:
                        # Get product link
                        link_element = name_element if name_element.name == 'a' else name_element.find_parent('a') or element.select_one('a')
                        if link_element and link_element.get('href'):
                            product_link = urljoin(self.base_url, link_element.get('href'))
                        break
            
            if not name:
                return None
            
            # Price extraction
            price_selectors = [
                '.price-current',
                '.current-price',
                '.price',
                '.goods-price',
                '.sale-price',
                '.now-price'
            ]
            
            price = None
            for selector in price_selectors:
                price_element = element.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    price = self._extract_price_from_text(price_text)
                    if price:
                        break
            
            # Original price
            original_price = None
            original_selectors = [
                '.price-original',
                '.original-price',
                '.old-price',
                '.was-price'
            ]
            
            for selector in original_selectors:
                orig_element = element.select_one(selector)
                if orig_element:
                    orig_text = orig_element.get_text(strip=True)
                    original_price = self._extract_price_from_text(orig_text)
                    break
            
            # Product image
            image_url = None
            img_selectors = [
                'img',
                '.goods-img img',
                '.product-img img'
            ]
            
            for selector in img_selectors:
                img_element = element.select_one(selector)
                if img_element:
                    img_src = img_element.get('src') or img_element.get('data-src') or img_element.get('data-original')
                    if img_src and 'http' in img_src:
                        image_url = img_src
                        break
                    elif img_src:
                        image_url = urljoin(self.base_url, img_src)
                        break
            
            # Rating
            rating = None
            rating_element = element.select_one('.rating, .stars, [data-rating]')
            if rating_element:
                rating_text = rating_element.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Discount
            discount = None
            discount_element = element.select_one('.discount, .sale-tag, .percent-off')
            if discount_element:
                discount_text = discount_element.get_text(strip=True)
                discount_match = re.search(r'(\d+)%', discount_text)
                if discount_match:
                    discount = int(discount_match.group(1))
            
            # Build product data
            product_data = {
                'name': name,
                'price': price,
                'original_price': original_price,
                'currency': 'KES',
                'url': product_link,
                'image_url': image_url,
                'rating': rating,
                'discount_percent': discount,
                'retailer': 'Kilimall',
                'retailer_id': 'kilimall_ke',
                'in_stock': True,
                'scraped_at': time.time()
            }
            
            # Only return if we have essential data
            if product_data['name'] and product_data['price']:
                return product_data
            
        except Exception as e:
            logger.error(f"Error extracting single product: {str(e)}")
        
        return None
    
    def _extract_from_link(self, link_element) -> Optional[Dict[str, Any]]:
        """
        Extract basic product info from a product link element
        """
        try:
            name = link_element.get_text(strip=True) or link_element.get('title', '').strip()
            if not name:
                return None
            
            product_link = urljoin(self.base_url, link_element.get('href'))
            
            # Try to find price in nearby elements
            price = None
            parent = link_element.find_parent()
            if parent:
                price_element = parent.select_one('.price, .current-price, .sale-price')
                if price_element:
                    price = self._extract_price_from_text(price_element.get_text(strip=True))
            
            # Try to find image
            image_url = None
            if parent:
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
                'retailer': 'Kilimall',
                'retailer_id': 'kilimall_ke',
                'in_stock': True,
                'scraped_at': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error extracting from link: {str(e)}")
            return None
    
    def _extract_price_from_text(self, price_text: str) -> Optional[float]:
        """
        Extract numeric price from text
        """
        if not price_text:
            return None
        
        # Remove currency symbols and clean
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
        Get detailed product information
        """
        try:
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(product_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {
                'url': product_url,
                'retailer': 'Kilimall'
            }
            
            # Product name
            name_element = soup.select_one('h1, .product-title, .goods-name')
            if name_element:
                details['name'] = name_element.get_text(strip=True)
            
            # Price
            price_element = soup.select_one('.current-price, .price, .sale-price')
            if price_element:
                details['price'] = self._extract_price_from_text(price_element.get_text(strip=True))
            
            # Description
            desc_element = soup.select_one('.description, .product-desc, .goods-desc')
            if desc_element:
                details['description'] = desc_element.get_text(strip=True)[:500]
            
            # Images
            img_elements = soup.select('.product-images img, .goods-gallery img')
            if img_elements:
                details['images'] = []
                for img in img_elements:
                    img_src = img.get('src') or img.get('data-src')
                    if img_src:
                        full_url = urljoin(self.base_url, img_src) if not img_src.startswith('http') else img_src
                        details['images'].append(full_url)
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting Kilimall product details: {str(e)}")
            return None
    
    def search_category(self, category_path: str, max_pages: int = 2) -> List[Dict[str, Any]]:
        """
        Scrape products from a category
        """
        products = []
        
        try:
            category_url = f"{self.base_url}{category_path}"
            
            for page in range(1, max_pages + 1):
                page_url = f"{category_url}?page={page}" if page > 1 else category_url
                
                time.sleep(random.uniform(2, 4))
                
                response = self.session.get(page_url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                page_products = self._extract_products_from_page(soup)
                
                if not page_products:
                    break
                
                products.extend(page_products)
                
        except Exception as e:
            logger.error(f"Error scraping Kilimall category: {str(e)}")
        
        return products
