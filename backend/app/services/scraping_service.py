"""
Web scraping service for fetching real-time prices from retailer websites
"""
import logging
import time
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from decimal import Decimal
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import re

from app.extensions.extensions import db
from app.models.product import ProductRetailer, PriceHistory

# Set up logger
logger = logging.getLogger(__name__)

class ScrapingService:
    """
    Service for scraping product prices from retailer websites
    """
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_selenium_driver(self, headless=True):
        """
        Create and configure a Selenium WebDriver
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={self.ua.random}')
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            return None
    
    def scrape_product_price(self, product_retailer: ProductRetailer) -> Dict[str, Any]:
        """
        Scrape price for a specific product from a retailer
        
        Args:
            product_retailer: ProductRetailer instance
            
        Returns:
            Dict containing scraped price data
        """
        retailer_name = product_retailer.retailer.name.lower()
        url = product_retailer.retailer_product_url
        
        if not url:
            return {"success": False, "error": "No product URL available"}
        
        try:
            # Choose scraping method based on retailer
            if 'jumia' in retailer_name:
                return self._scrape_jumia(url)
            elif 'kilimall' in retailer_name:
                return self._scrape_kilimall(url)
            elif 'masoko' in retailer_name:
                return self._scrape_masoko(url)
            elif 'pigiame' in retailer_name:
                return self._scrape_pigiame(url)
            elif 'jiji' in retailer_name:
                return self._scrape_jiji(url)
            else:
                return self._scrape_generic(url)
                
        except Exception as e:
            logger.error(f"Error scraping {retailer_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _scrape_jumia(self, url: str) -> Dict[str, Any]:
        """Scrape price from Jumia Kenya"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Jumia price selectors (multiple possible selectors)
            price_selectors = [
                '.prc',  # Main price class
                '.-b -ltr -tal -fs24',  # Alternative price class
                '[data-automation-id="product-price"]',  # Data attribute
                '.price-box .price',  # Price box
            ]
            
            price_text = None
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    break
            
            if not price_text:
                return {"success": False, "error": "Price element not found"}
            
            # Extract numeric price
            price = self._extract_price(price_text)
            if price is None:
                return {"success": False, "error": f"Could not parse price: {price_text}"}
            
            # Check stock status
            stock_indicators = soup.select('.stck-st, .out-of-stock, [data-automation-id="pdp-product-availability"]')
            in_stock = True
            for indicator in stock_indicators:
                text = indicator.get_text(strip=True).lower()
                if any(phrase in text for phrase in ['out of stock', 'unavailable', 'sold out']):
                    in_stock = False
                    break
            
            return {
                "success": True,
                "price": price,
                "currency": "KES",
                "in_stock": in_stock,
                "scraped_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error scraping Jumia: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _scrape_kilimall(self, url: str) -> Dict[str, Any]:
        """Scrape price from Kilimall"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Kilimall price selectors
            price_selectors = [
                '.price-current',
                '.product-price .price',
                '.price-box .current-price',
                '.sale-price'
            ]
            
            price_text = None
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    break
            
            if not price_text:
                return {"success": False, "error": "Price element not found"}
            
            price = self._extract_price(price_text)
            if price is None:
                return {"success": False, "error": f"Could not parse price: {price_text}"}
            
            # Check stock
            stock_element = soup.select_one('.stock-status, .availability')
            in_stock = True
            if stock_element:
                stock_text = stock_element.get_text(strip=True).lower()
                in_stock = 'in stock' in stock_text or 'available' in stock_text
            
            return {
                "success": True,
                "price": price,
                "currency": "KES",
                "in_stock": in_stock,
                "scraped_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error scraping Kilimall: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _scrape_masoko(self, url: str) -> Dict[str, Any]:
        """Scrape price from Masoko (requires JavaScript)"""
        driver = None
        try:
            driver = self.get_selenium_driver()
            if not driver:
                return {"success": False, "error": "Could not create web driver"}
            
            driver.get(url)
            
            # Wait for price element to load
            wait = WebDriverWait(driver, 10)
            
            price_selectors = [
                '.price',
                '.product-price',
                '[data-testid="price"]',
                '.current-price'
            ]
            
            price_element = None
            for selector in price_selectors:
                try:
                    price_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not price_element:
                return {"success": False, "error": "Price element not found"}
            
            price_text = price_element.text.strip()
            price = self._extract_price(price_text)
            
            if price is None:
                return {"success": False, "error": f"Could not parse price: {price_text}"}
            
            # Check stock
            in_stock = True
            try:
                stock_element = driver.find_element(By.CSS_SELECTOR, '.stock-status, .availability, .out-of-stock')
                stock_text = stock_element.text.strip().lower()
                in_stock = 'out of stock' not in stock_text and 'unavailable' not in stock_text
            except:
                pass  # Assume in stock if no stock indicator found
            
            return {
                "success": True,
                "price": price,
                "currency": "KES",
                "in_stock": in_stock,
                "scraped_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error scraping Masoko: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            if driver:
                driver.quit()
    
    def _scrape_pigiame(self, url: str) -> Dict[str, Any]:
        """Scrape price from Pigiame"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            price_selectors = [
                '.price',
                '.ad-price',
                '.listing-price',
                '[data-price]'
            ]
            
            price_text = None
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    if not price_text and price_element.get('data-price'):
                        price_text = price_element.get('data-price')
                    break
            
            if not price_text:
                return {"success": False, "error": "Price element not found"}
            
            price = self._extract_price(price_text)
            if price is None:
                return {"success": False, "error": f"Could not parse price: {price_text}"}
            
            return {
                "success": True,
                "price": price,
                "currency": "KES",
                "in_stock": True,  # Assume in stock for classified ads
                "scraped_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error scraping Pigiame: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _scrape_jiji(self, url: str) -> Dict[str, Any]:
        """Scrape price from Jiji Kenya"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            price_selectors = [
                '.price-section .price',
                '.ad-price',
                '[data-testid="ad-price"]',
                '.price-container .price'
            ]
            
            price_text = None
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    break
            
            if not price_text:
                return {"success": False, "error": "Price element not found"}
            
            price = self._extract_price(price_text)
            if price is None:
                return {"success": False, "error": f"Could not parse price: {price_text}"}
            
            return {
                "success": True,
                "price": price,
                "currency": "KES",
                "in_stock": True,  # Assume in stock for classified ads
                "scraped_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error scraping Jiji: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _scrape_generic(self, url: str) -> Dict[str, Any]:
        """Generic scraper for unknown retailers"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Common price selectors
            price_selectors = [
                '.price', '.product-price', '.current-price', '.sale-price',
                '[data-price]', '[data-testid*="price"]', '.amount',
                '.cost', '.value', '.pricing'
            ]
            
            price_text = None
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    if not price_text and price_element.get('data-price'):
                        price_text = price_element.get('data-price')
                    if price_text:
                        break
            
            if not price_text:
                return {"success": False, "error": "Price element not found"}
            
            price = self._extract_price(price_text)
            if price is None:
                return {"success": False, "error": f"Could not parse price: {price_text}"}
            
            return {
                "success": True,
                "price": price,
                "currency": "KES",
                "in_stock": True,  # Assume in stock if no stock indicator
                "scraped_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error in generic scraping: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """
        Extract numeric price from text
        
        Args:
            price_text: Raw price text from webpage
            
        Returns:
            Extracted price as float or None if not found
        """
        if not price_text:
            return None
        
        # Remove common currency symbols and text
        price_text = re.sub(r'[KES|KSH|Ksh|₹|$|€|£|,\s]', '', price_text, flags=re.IGNORECASE)
        
        # Find all numbers in the text
        numbers = re.findall(r'\d+\.?\d*', price_text)
        
        if not numbers:
            return None
        
        # Take the largest number (usually the main price)
        prices = [float(num) for num in numbers if float(num) > 0]
        
        if not prices:
            return None
        
        return max(prices)
    
    def add_random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to avoid being blocked"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
