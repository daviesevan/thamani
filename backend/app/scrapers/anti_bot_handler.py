"""
Anti-bot detection handling for web scrapers
"""
import random
import time
import requests
from typing import List, Dict, Any, Optional
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc

logger = logging.getLogger(__name__)

class AntiBot:
    """
    Advanced anti-bot detection handling
    """
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Free proxy list (you can expand this or use a proxy service)
        self.proxies = [
            # Add working proxies here
            # Format: {'http': 'http://proxy:port', 'https': 'https://proxy:port'}
        ]
        
        self.current_proxy_index = 0
        self.driver = None
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent string"""
        return random.choice(self.user_agents)
    
    def get_random_headers(self) -> Dict[str, str]:
        """Generate realistic browser headers"""
        headers = {
            'User-Agent': self.get_random_user_agent(),
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
        
        # Randomly add some optional headers
        optional_headers = {
            'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
            'Sec-Fetch-User': '?1'
        }
        
        for key, value in optional_headers.items():
            if random.random() > 0.3:  # 70% chance to include each header
                headers[key] = value
        
        return headers
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get the next proxy in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy
    
    def create_session_with_rotation(self) -> requests.Session:
        """Create a requests session with rotating headers and proxies"""
        session = requests.Session()
        
        # Set random headers
        session.headers.update(self.get_random_headers())
        
        # Set proxy if available
        proxy = self.get_next_proxy()
        if proxy:
            session.proxies.update(proxy)
            logger.info(f"Using proxy: {proxy}")
        
        return session
    
    def add_human_delays(self, min_delay: float = 1.0, max_delay: float = 5.0):
        """Add human-like delays between requests"""
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"Adding delay: {delay:.2f} seconds")
        time.sleep(delay)
    
    def create_undetected_driver(self, headless: bool = True) -> webdriver.Chrome:
        """Create an undetected Chrome driver for JavaScript-heavy sites"""
        try:
            options = uc.ChromeOptions()
            
            if headless:
                options.add_argument('--headless')
            
            # Anti-detection options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # Faster loading
            options.add_argument('--disable-javascript')  # Only if JS not needed
            
            # Random window size
            width = random.randint(1200, 1920)
            height = random.randint(800, 1080)
            options.add_argument(f'--window-size={width},{height}')
            
            # Random user agent
            options.add_argument(f'--user-agent={self.get_random_user_agent()}')
            
            driver = uc.Chrome(options=options)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver = driver
            return driver
            
        except Exception as e:
            logger.error(f"Error creating undetected driver: {str(e)}")
            return None
    
    def safe_get_with_selenium(self, url: str, wait_for_element: str = None, 
                              timeout: int = 10) -> Optional[str]:
        """Safely get a page with Selenium and wait for specific elements"""
        if not self.driver:
            self.driver = self.create_undetected_driver()
        
        if not self.driver:
            return None
        
        try:
            # Add random delay before request
            self.add_human_delays(1, 3)
            
            self.driver.get(url)
            
            # Wait for specific element if provided
            if wait_for_element:
                wait = WebDriverWait(self.driver, timeout)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
            else:
                # Default wait for page load
                time.sleep(random.uniform(2, 5))
            
            # Simulate human behavior - random scrolling
            self.simulate_human_behavior()
            
            return self.driver.page_source
            
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {wait_for_element}")
            return self.driver.page_source if self.driver else None
        except WebDriverException as e:
            logger.error(f"WebDriver error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error in safe_get_with_selenium: {str(e)}")
            return None
    
    def simulate_human_behavior(self):
        """Simulate human-like behavior on the page"""
        if not self.driver:
            return
        
        try:
            # Random scrolling
            scroll_actions = random.randint(1, 3)
            for _ in range(scroll_actions):
                scroll_y = random.randint(100, 800)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_y});")
                time.sleep(random.uniform(0.5, 2))
            
            # Random mouse movements (if needed)
            # This would require additional libraries like pyautogui
            
        except Exception as e:
            logger.error(f"Error simulating human behavior: {str(e)}")
    
    def handle_cloudflare_challenge(self, url: str) -> Optional[str]:
        """Handle Cloudflare challenges using undetected Chrome"""
        logger.info("Attempting to handle Cloudflare challenge")
        
        driver = self.create_undetected_driver(headless=False)  # Visible for challenges
        if not driver:
            return None
        
        try:
            driver.get(url)
            
            # Wait for Cloudflare challenge to complete
            wait = WebDriverWait(driver, 30)
            
            # Wait for either the challenge to complete or the page to load
            try:
                # Wait for challenge completion indicators
                wait.until(lambda d: "Checking your browser" not in d.page_source)
                time.sleep(5)  # Additional wait for full page load
            except TimeoutException:
                logger.warning("Cloudflare challenge may not have completed")
            
            page_source = driver.page_source
            driver.quit()
            
            return page_source
            
        except Exception as e:
            logger.error(f"Error handling Cloudflare challenge: {str(e)}")
            if driver:
                driver.quit()
            return None
    
    def detect_blocking(self, response_text: str, status_code: int) -> bool:
        """Detect if the request was blocked or challenged"""
        blocking_indicators = [
            'cloudflare',
            'access denied',
            'blocked',
            'captcha',
            'bot detection',
            'rate limit',
            'too many requests',
            'suspicious activity',
            'security check'
        ]
        
        # Check status codes
        if status_code in [403, 429, 503]:
            return True
        
        # Check response content
        response_lower = response_text.lower()
        for indicator in blocking_indicators:
            if indicator in response_lower:
                return True
        
        return False
    
    def smart_request(self, url: str, session: requests.Session = None, 
                     max_retries: int = 3) -> Optional[requests.Response]:
        """Make a smart request with anti-bot measures"""
        if not session:
            session = self.create_session_with_rotation()
        
        for attempt in range(max_retries):
            try:
                # Add delay before request
                self.add_human_delays(2, 5)
                
                response = session.get(url, timeout=15)
                
                # Check if blocked
                if self.detect_blocking(response.text, response.status_code):
                    logger.warning(f"Blocking detected on attempt {attempt + 1}")
                    
                    if attempt < max_retries - 1:
                        # Try with new session and longer delay
                        session = self.create_session_with_rotation()
                        self.add_human_delays(10, 20)
                        continue
                    else:
                        # Last attempt - try with Selenium
                        logger.info("Falling back to Selenium")
                        page_source = self.safe_get_with_selenium(url)
                        if page_source:
                            # Create a mock response object
                            mock_response = requests.Response()
                            mock_response._content = page_source.encode('utf-8')
                            mock_response.status_code = 200
                            return mock_response
                        return None
                
                return response
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    self.add_human_delays(5, 10)
                    continue
                return None
        
        return None
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except Exception as e:
                logger.error(f"Error cleaning up driver: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()

# Global instance for reuse
anti_bot = AntiBot()

def get_anti_bot_session() -> requests.Session:
    """Get a session with anti-bot measures"""
    return anti_bot.create_session_with_rotation()

def safe_request(url: str, **kwargs) -> Optional[requests.Response]:
    """Make a safe request with anti-bot measures"""
    return anti_bot.smart_request(url, **kwargs)

def get_selenium_page(url: str, wait_for: str = None) -> Optional[str]:
    """Get page content using Selenium"""
    return anti_bot.safe_get_with_selenium(url, wait_for)
