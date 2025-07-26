"""
Retailer-specific scraper configurations and methods
"""
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

class RetailerScraperConfig:
    """Base configuration for retailer scrapers"""
    
    def __init__(self, name: str):
        self.name = name
        self.requires_js = False
        self.price_selectors = []
        self.stock_selectors = []
        self.out_of_stock_indicators = []
        self.currency = "KES"
        self.timeout = 10
        
class JumiaScraperConfig(RetailerScraperConfig):
    """Jumia Kenya scraper configuration"""
    
    def __init__(self):
        super().__init__("Jumia Kenya")
        self.requires_js = False
        self.price_selectors = [
            '.prc',  # Main price class
            '.-b.-ltr.-tal.-fs24',  # Alternative price class
            '[data-automation-id="product-price"]',  # Data attribute
            '.price-box .price',  # Price box
            '.-fs24.-fw.-tal.-b',  # Another variant
            '.price .-b',  # Price with bold
        ]
        self.stock_selectors = [
            '.stck-st',
            '.out-of-stock',
            '[data-automation-id="pdp-product-availability"]',
            '.availability-status'
        ]
        self.out_of_stock_indicators = [
            'out of stock', 'unavailable', 'sold out', 'not available'
        ]
        
    def extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from Jumia page"""
        for selector in self.price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                price = self._parse_price(price_text)
                if price:
                    return price
        return None
    
    def check_stock(self, soup: BeautifulSoup) -> bool:
        """Check if product is in stock on Jumia"""
        for selector in self.stock_selectors:
            stock_element = soup.select_one(selector)
            if stock_element:
                stock_text = stock_element.get_text(strip=True).lower()
                for indicator in self.out_of_stock_indicators:
                    if indicator in stock_text:
                        return False
        return True
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price text to extract numeric value"""
        if not price_text:
            return None
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[KES|KSH|Ksh|,\s]', '', price_text, flags=re.IGNORECASE)
        
        # Extract numbers
        numbers = re.findall(r'\d+\.?\d*', cleaned)
        if numbers:
            return float(max(numbers, key=float))
        return None

class KilimallScraperConfig(RetailerScraperConfig):
    """Kilimall scraper configuration"""
    
    def __init__(self):
        super().__init__("Kilimall")
        self.requires_js = False
        self.price_selectors = [
            '.price-current',
            '.product-price .price',
            '.price-box .current-price',
            '.sale-price',
            '.now-price',
            '.final-price'
        ]
        self.stock_selectors = [
            '.stock-status',
            '.availability',
            '.inventory-status'
        ]
        self.out_of_stock_indicators = [
            'out of stock', 'unavailable', 'sold out'
        ]
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from Kilimall page"""
        for selector in self.price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                price = self._parse_price(price_text)
                if price:
                    return price
        return None
    
    def check_stock(self, soup: BeautifulSoup) -> bool:
        """Check if product is in stock on Kilimall"""
        for selector in self.stock_selectors:
            stock_element = soup.select_one(selector)
            if stock_element:
                stock_text = stock_element.get_text(strip=True).lower()
                return 'in stock' in stock_text or 'available' in stock_text
        return True  # Assume in stock if no indicator found
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price text to extract numeric value"""
        if not price_text:
            return None
        
        cleaned = re.sub(r'[KES|KSH|Ksh|,\s]', '', price_text, flags=re.IGNORECASE)
        numbers = re.findall(r'\d+\.?\d*', cleaned)
        if numbers:
            return float(max(numbers, key=float))
        return None

class MasokoScraperConfig(RetailerScraperConfig):
    """Masoko scraper configuration (requires JavaScript)"""
    
    def __init__(self):
        super().__init__("Masoko")
        self.requires_js = True
        self.price_selectors = [
            '.price',
            '.product-price',
            '[data-testid="price"]',
            '.current-price',
            '.selling-price'
        ]
        self.stock_selectors = [
            '.stock-status',
            '.availability',
            '.out-of-stock'
        ]
        self.out_of_stock_indicators = [
            'out of stock', 'unavailable', 'sold out'
        ]
    
    def extract_price_selenium(self, driver) -> Optional[float]:
        """Extract price using Selenium for JavaScript-heavy pages"""
        wait = WebDriverWait(driver, self.timeout)
        
        for selector in self.price_selectors:
            try:
                price_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                price_text = price_element.text.strip()
                price = self._parse_price(price_text)
                if price:
                    return price
            except TimeoutException:
                continue
        return None
    
    def check_stock_selenium(self, driver) -> bool:
        """Check stock status using Selenium"""
        try:
            stock_element = driver.find_element(By.CSS_SELECTOR, ', '.join(self.stock_selectors))
            stock_text = stock_element.text.strip().lower()
            for indicator in self.out_of_stock_indicators:
                if indicator in stock_text:
                    return False
        except:
            pass  # Assume in stock if no stock indicator found
        return True
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price text to extract numeric value"""
        if not price_text:
            return None
        
        cleaned = re.sub(r'[KES|KSH|Ksh|,\s]', '', price_text, flags=re.IGNORECASE)
        numbers = re.findall(r'\d+\.?\d*', cleaned)
        if numbers:
            return float(max(numbers, key=float))
        return None

class PigiameScraperConfig(RetailerScraperConfig):
    """Pigiame scraper configuration"""
    
    def __init__(self):
        super().__init__("Pigiame")
        self.requires_js = False
        self.price_selectors = [
            '.price',
            '.ad-price',
            '.listing-price',
            '[data-price]',
            '.amount'
        ]
        # Classified ads usually don't have stock status
        self.stock_selectors = []
        self.out_of_stock_indicators = []
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from Pigiame page"""
        for selector in self.price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                if not price_text and price_element.get('data-price'):
                    price_text = price_element.get('data-price')
                price = self._parse_price(price_text)
                if price:
                    return price
        return None
    
    def check_stock(self, soup: BeautifulSoup) -> bool:
        """Classified ads are usually always 'in stock'"""
        return True
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price text to extract numeric value"""
        if not price_text:
            return None
        
        cleaned = re.sub(r'[KES|KSH|Ksh|,\s]', '', price_text, flags=re.IGNORECASE)
        numbers = re.findall(r'\d+\.?\d*', cleaned)
        if numbers:
            return float(max(numbers, key=float))
        return None

class JijiScraperConfig(RetailerScraperConfig):
    """Jiji Kenya scraper configuration"""
    
    def __init__(self):
        super().__init__("Jiji Kenya")
        self.requires_js = False
        self.price_selectors = [
            '.price-section .price',
            '.ad-price',
            '[data-testid="ad-price"]',
            '.price-container .price',
            '.listing-price'
        ]
        # Classified ads usually don't have stock status
        self.stock_selectors = []
        self.out_of_stock_indicators = []
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from Jiji page"""
        for selector in self.price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                price = self._parse_price(price_text)
                if price:
                    return price
        return None
    
    def check_stock(self, soup: BeautifulSoup) -> bool:
        """Classified ads are usually always 'in stock'"""
        return True
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price text to extract numeric value"""
        if not price_text:
            return None
        
        cleaned = re.sub(r'[KES|KSH|Ksh|,\s]', '', price_text, flags=re.IGNORECASE)
        numbers = re.findall(r'\d+\.?\d*', cleaned)
        if numbers:
            return float(max(numbers, key=float))
        return None

class GenericScraperConfig(RetailerScraperConfig):
    """Generic scraper for unknown retailers"""
    
    def __init__(self):
        super().__init__("Generic")
        self.requires_js = False
        self.price_selectors = [
            '.price', '.product-price', '.current-price', '.sale-price',
            '[data-price]', '[data-testid*="price"]', '.amount',
            '.cost', '.value', '.pricing', '.money'
        ]
        self.stock_selectors = [
            '.stock', '.availability', '.inventory'
        ]
        self.out_of_stock_indicators = [
            'out of stock', 'unavailable', 'sold out', 'not available'
        ]
    
    def extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract price from generic page"""
        for selector in self.price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
                if not price_text and price_element.get('data-price'):
                    price_text = price_element.get('data-price')
                price = self._parse_price(price_text)
                if price:
                    return price
        return None
    
    def check_stock(self, soup: BeautifulSoup) -> bool:
        """Check stock status generically"""
        for selector in self.stock_selectors:
            stock_element = soup.select_one(selector)
            if stock_element:
                stock_text = stock_element.get_text(strip=True).lower()
                for indicator in self.out_of_stock_indicators:
                    if indicator in stock_text:
                        return False
        return True  # Assume in stock if no indicator found
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price text to extract numeric value"""
        if not price_text:
            return None
        
        cleaned = re.sub(r'[KES|KSH|Ksh|₹|$|€|£|,\s]', '', price_text, flags=re.IGNORECASE)
        numbers = re.findall(r'\d+\.?\d*', cleaned)
        if numbers:
            return float(max(numbers, key=float))
        return None

# Scraper factory
SCRAPER_CONFIGS = {
    'jumia': JumiaScraperConfig,
    'kilimall': KilimallScraperConfig,
    'masoko': MasokoScraperConfig,
    'pigiame': PigiameScraperConfig,
    'jiji': JijiScraperConfig,
    'generic': GenericScraperConfig
}

def get_scraper_config(retailer_name: str) -> RetailerScraperConfig:
    """
    Get appropriate scraper configuration for a retailer
    
    Args:
        retailer_name: Name of the retailer
        
    Returns:
        Scraper configuration instance
    """
    retailer_key = retailer_name.lower()
    
    for key, config_class in SCRAPER_CONFIGS.items():
        if key in retailer_key:
            return config_class()
    
    # Default to generic scraper
    return GenericScraperConfig()
