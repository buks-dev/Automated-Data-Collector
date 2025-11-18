"""Browser automation utilities."""

import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

class BrowserManager:
    """Manages browser instances and operations."""
    
    def __init__(self, headless=True, chromedriver_path=None):
        self.headless = headless
        self.chromedriver_path = chromedriver_path
        self.driver = None
    
    def create_driver(self, user_agent=None, proxy=None):
        """Create and configure a Chrome WebDriver instance."""
        chrome_options = ChromeOptions()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Performance optimizations
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript-har-promises")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--aggressive-cache-discard")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        # Set user agent
        if user_agent:
            chrome_options.add_argument(f"--user-agent={user_agent}")
        else:
            # Rotate user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0)",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0)"
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        # Setup proxy if available
        if proxy:
            chrome_options.add_argument(f"--proxy-server={proxy}")
        
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Performance preferences
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,  # Disable images
                'plugins': 2,  # Disable plugins
                'popups': 2,  # Disable popups
            }
        }
        chrome_options.add_experimental_option('prefs', prefs)
        
        # Initialize WebDriver
        if self.chromedriver_path and os.path.exists(self.chromedriver_path):
            service = Service(executable_path=self.chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set page load timeout
        self.driver.set_page_load_timeout(30)
        
        # Execute script to avoid detection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return self.driver
    
    def close_driver(self):
        """Close the browser driver."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def navigate_to_google_maps(self, search_term):
        """Navigate to Google Maps with the given search term."""
        if not self.driver:
            self.create_driver()
        
        url = f"https://www.google.com/maps/search/{search_term.replace(' ', '+')}"
        self.driver.get(url)
        time.sleep(random.uniform(1, 2))  # Wait for page to load
    
    def find_search_results(self):
        """Find search result elements on the page."""
        if not self.driver:
            return []
        
        # Try multiple selectors for search results
        selectors = [
            (By.CSS_SELECTOR, "div[role='article']"),
            (By.CSS_SELECTOR, "div.section-result"),
            (By.CSS_SELECTOR, "div.place-result"),
            (By.CSS_SELECTOR, "div[jsaction*='mouseover']"),
            (By.CSS_SELECTOR, "div[aria-label*='result']"),
            (By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd"),
            (By.CSS_SELECTOR, "div[jscontroller='AtSb']"),
            (By.CSS_SELECTOR, "div[aria-label*='Results for']")
        ]
        
        for selector_by, selector_value in selectors:
            try:
                results = self.driver.find_elements(selector_by, selector_value)
                if results:
                    return results
            except:
                continue
        
        return []
    
    def load_more_results(self):
        """Try to load more results on the page."""
        if not self.driver:
            return False
        
        try:
            # Try multiple ways to load more results
            load_more_selectors = [
                (By.CSS_SELECTOR, "button[aria-label='More results']"),
                (By.CSS_SELECTOR, "button[aria-label*='more']"),
                (By.CSS_SELECTOR, "button[aria-label*='next']"),
                (By.CSS_SELECTOR, "button[aria-label*='load']"),
                (By.XPATH, "//button[contains(@aria-label, 'more') or contains(@aria-label, 'More')]")
            ]
            
            for load_by, load_value in load_more_selectors:
                try:
                    load_more_button = self.driver.find_element(load_by, load_value)
                    if load_more_button and load_more_button.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
                        time.sleep(0.5)
                        load_more_button.click()
                        time.sleep(random.uniform(1, 2))
                        return True
                except:
                    continue
            
            # Try scrolling to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))
            
            return True
        except Exception as e:
            print(f"Error loading more results: {str(e)}")
            return False