"""Data collection logic for Google Maps scraping."""

import os
import time
import uuid
import json
import random
import requests
import threading
import re
from typing import Dict, List, Optional, Tuple
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QThreadPool, QRunnable
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from models import BusinessData
from utils.browser import BrowserManager
from utils.data_extraction import EmailExtractor
from utils.network import ProxyManager
from utils.file_ops import FileManager

class DataProcessorSignals(QObject):
    """Signals for data processing."""
    data_ready = pyqtSignal(dict)
    skipped = pyqtSignal(str)  # Signal for skipped entries
    error = pyqtSignal(str)

class DataProcessor(QRunnable):
    """Processes a single search result entry."""
    
    def __init__(self, driver, result_element, index, temp_dir, email_extractor, skip_missing_social):
        super().__init__()
        self.driver = driver
        self.result_element = result_element
        self.index = index
        self.temp_dir = temp_dir
        self.email_extractor = email_extractor
        self.skip_missing_social = skip_missing_social
        self.signals = DataProcessorSignals()
    
    def run(self):
        """Process the search result entry."""
        try:
            # Extract name and address from result element before clicking
            entry_info = self.extract_info_from_result()
            entry_name = entry_info.get('name', 'Unknown')
            entry_address = entry_info.get('address', 'N/A')
            
            # Improved element interaction with multiple attempts
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Scroll to element with more precision
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", self.result_element)
                    time.sleep(random.uniform(0.3, 0.7))  # Increased delay
                    
                    # Try regular click first
                    self.result_element.click()
                    break
                except Exception as click_error:
                    # If regular click fails, try JavaScript click
                    try:
                        self.driver.execute_script("arguments[0].click();", self.result_element)
                        break
                    except Exception as js_error:
                        if attempt == max_attempts - 1:
                            raise Exception(f"Failed to click element after {max_attempts} attempts: {str(click_error)}")
                        time.sleep(random.uniform(0.5, 1.0))  # Wait before retry
            
            # Wait for details to load with increased delay
            time.sleep(random.uniform(1.0, 1.5))
            
            # Extract data
            data = self.extract_data()
            
            # Use the name and address we extracted earlier if the extracted data doesn't have valid ones
            if data:
                if data.get('name') == 'N/A' or data.get('name') == 'Results' or not data.get('name'):
                    data['name'] = entry_name
                
                if data.get('address') == 'N/A' or not data.get('address'):
                    data['address'] = entry_address
            
            if data:
                # Check if we should skip this entry
                if self.skip_missing_social and data.get('website') == "N/A" and data.get('instagram') == "N/A":
                    business_name = data.get('name', entry_name)
                    business_address = data.get('address', entry_address)
                    self.signals.skipped.emit(f"Skipped entry {self.index + 1} ({business_name}) - Address: {business_address} - No website or Instagram")
                else:
                    self.signals.data_ready.emit(data)
            else:
                self.signals.error.emit(f"Failed to extract data from entry {self.index + 1}")
        except Exception as e:
            self.signals.error.emit(f"Error processing entry {self.index + 1}: {str(e)}")
    
    def extract_info_from_result(self):
        """Extract the business name and address from the result element before clicking."""
        try:
            info = {'name': 'Unknown', 'address': 'N/A'}
            
            # Try multiple selectors to find the name
            name_selectors = [
                "div.fontHeadlineSmall",
                "div.fontBodyMedium",
                "h3",
                "a",
                "div[role='article'] > div > div > div > div > div",
                "div[jsaction*='mouseover'] > div > div > div"
            ]
            
            for selector in name_selectors:
                try:
                    name_element = self.result_element.find_element(By.CSS_SELECTOR, selector)
                    name_text = name_element.text.strip()
                    if name_text and name_text != "Results":
                        info['name'] = name_text
                        break
                except:
                    continue
            
            # If no selector worked for name, try to get any text from the result element
            if info['name'] == 'Unknown':
                try:
                    text = self.result_element.text.strip()
                    if text and text != "Results":
                        # Split by newlines and take the first non-empty line
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        if lines:
                            info['name'] = lines[0]
                except:
                    pass
            
            # Try to extract address from the result element
            address_selectors = [
                "div.fontBodyMedium:last-child",
                "div[role='article'] > div > div > div > div > div:last-child",
                "div[jsaction*='mouseover'] > div > div > div:last-child"
            ]
            
            for selector in address_selectors:
                try:
                    address_element = self.result_element.find_element(By.CSS_SELECTOR, selector)
                    address_text = address_element.text.strip()
                    if address_text and address_text != info['name']:
                        info['address'] = address_text
                        break
                except:
                    continue
            
            # If no selector worked for address, try to get any text from the result element
            if info['address'] == 'N/A':
                try:
                    text = self.result_element.text.strip()
                    if text and text != "Results" and text != info['name']:
                        # Split by newlines and look for address-like text
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        # Skip the first line (likely the name)
                        if len(lines) > 1:
                            # Look for lines that might contain address information
                            for line in lines[1:]:
                                if any(char.isdigit() for char in line) or len(line.split()) > 3:
                                    info['address'] = line
                                    break
                except:
                    pass
            
            return info
        except Exception as e:
            print(f"Error extracting info from result: {str(e)}")
            return {'name': 'Unknown', 'address': 'N/A'}
    
    def extract_data(self):
        """Extract detailed data from the business page."""
        try:
            data = {}
            
            # Extract name
            try:
                name_element = self.driver.find_element(By.CSS_SELECTOR, "h1.fontHeadlineLarge")
                data['name'] = name_element.text if name_element else "N/A"
            except:
                try:
                    name_element = self.driver.find_element(By.CSS_SELECTOR, "h1")
                    data['name'] = name_element.text if name_element else "N/A"
                except:
                    data['name'] = "N/A"
            
            # Extract phone number
            try:
                phone_element = self.driver.find_element(By.CSS_SELECTOR, "button[data-tooltip='Copy phone number']")
                phone = phone_element.get_attribute('aria-label')
                if phone and 'Copy phone number' in phone:
                    data['phone'] = phone.replace('Copy phone number ', '')
                else:
                    data['phone'] = phone or "N/A"
            except:
                try:
                    phone_element = self.driver.find_element(By.XPATH, "//a[contains(@href, 'tel:')]")
                    data['phone'] = phone_element.get_attribute('href').replace('tel:', '')
                except:
                    data['phone'] = "N/A"
            
            # Extract website
            try:
                website_element = self.driver.find_element(By.CSS_SELECTOR, "a[data-tooltip='Open website']")
                data['website'] = website_element.get_attribute('href')
            except:
                try:
                    website_element = self.driver.find_element(By.XPATH, "//a[contains(@href, 'http') and not(contains(@href, 'google'))]")
                    data['website'] = website_element.get_attribute('href')
                except:
                    data['website'] = "N/A"
            
            # Extract email from website
            if data.get('website') and data['website'] != "N/A":
                emails = self.email_extractor.extract_emails(data['website'])
                data['email'] = emails[0] if emails else "N/A"
            else:
                data['email'] = "N/A"
            
            # Extract Instagram
            try:
                data['instagram'] = self.extract_instagram()
            except:
                data['instagram'] = "N/A"
            
            # Extract address
            try:
                address_element = self.driver.find_element(By.CSS_SELECTOR, "button[data-tooltip='Copy address']")
                address = address_element.get_attribute('aria-label')
                if address and 'Copy address' in address:
                    data['address'] = address.replace('Copy address ', '')
                else:
                    data['address'] = address or "N/A"
            except:
                try:
                    # Try alternative address selectors
                    address_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.fontBodyMedium")
                    for element in address_elements:
                        text = element.text.strip()
                        if text and any(char.isdigit() for char in text) and len(text.split()) > 3:
                            data['address'] = text
                            break
                    else:
                        data['address'] = "N/A"
                except:
                    data['address'] = "N/A"
            
            # Extract opening hours
            try:
                hours_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='hours']")
                hours_button.click()
                time.sleep(random.uniform(0.3, 0.7))  # Reduced delay
                
                hours_elements = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                hours_dict = {}
                for row in hours_elements:
                    try:
                        day = row.find_element(By.CSS_SELECTOR, "td:first-child").text
                        time = row.find_element(By.CSS_SELECTOR, "td:last-child").text
                        hours_dict[day] = time
                    except:
                        continue
                
                if hours_dict:
                    data['hours'] = json.dumps(hours_dict)
                else:
                    # Try alternative hours display
                    hours_text_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.fontBodyMedium")
                    for elem in hours_text_elements:
                        if "hour" in elem.text.lower() or ":" in elem.text:
                            data['hours'] = elem.text
                            break
                    else:
                        data['hours'] = "N/A"
            except:
                data['hours'] = "N/A"
            
            # Extract image
            try:
                image_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='View all photos']")
                image_button.click()
                time.sleep(random.uniform(0.3, 0.7))  # Reduced delay
                
                # Get the main image
                main_image = self.driver.find_element(By.CSS_SELECTOR, "button.cX2WmGKJbX__image-viewer-image")
                image_url = None
                
                if main_image.get_attribute('style'):
                    image_style = main_image.get_attribute('style')
                    image_url_match = re.search(r'url\("([^"]+)"\)', image_style)
                    if image_url_match:
                        image_url = image_url_match.group(1)
                else:
                    image_url = main_image.get_attribute('src')
                
                if image_url:
                    data['image_path'] = self.download_image(image_url, data.get('name', 'unknown'))
                else:
                    data['image_path'] = "N/A"
                
                # Close the image viewer
                close_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']")
                close_button.click()
                time.sleep(0.3)  # Reduced delay
            except:
                data['image_path'] = "N/A"
            
            # Extract products/services
            try:
                menu_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='menu']")
                menu_button.click()
                time.sleep(random.uniform(0.3, 0.7))  # Reduced delay
                
                # Extract menu items or services
                menu_items = []
                item_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.fontBodyMedium")
                for element in item_elements:
                    if element.text and element.text not in menu_items:
                        menu_items.append(element.text)
                
                if menu_items:
                    data['products_services'] = json.dumps(menu_items[:10])  # Limit to first 10 items
                else:
                    # Try to get from description
                    description_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.fontBodyMedium")
                    descriptions = [elem.text for elem in description_elements if elem.text]
                    if descriptions:
                        data['products_services'] = json.dumps(descriptions[:5])  # Limit to first 5 descriptions
                    else:
                        data['products_services'] = "N/A"
            except:
                data['products_services'] = "N/A"
            
            return data
            
        except Exception as e:
            print(f"Error extracting data: {str(e)}")
            return None
    
    def extract_instagram(self):
        """Extract Instagram handle from website or description."""
        # Try to find Instagram in the business description
        description_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.fontBodyMedium")
        for element in description_elements:
            text = element.text
            instagram_match = re.search(r'instagram\.com/([a-zA-Z0-9_.]+)', text)
            if instagram_match:
                return f"https://instagram.com/{instagram_match.group(1)}"
        
        # Try from website if available
        website = self.driver.find_elements(By.CSS_SELECTOR, "a[data-tooltip='Open website']")
        if website:
            website_url = website[0].get_attribute('href')
            if website_url and website_url != "N/A":
                try:
                    response = requests.get(website_url, timeout=5)
                    if response.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for Instagram links
                        instagram_links = soup.select('a[href*="instagram.com"]')
                        if instagram_links:
                            return instagram_links[0].get('href')
                        
                        # Look for Instagram handles in text
                        instagram_pattern = r'@([a-zA-Z0-9_.]+)'
                        handles = re.findall(instagram_pattern, soup.get_text())
                        if handles:
                            return f"https://instagram.com/{handles[0]}"
                except:
                    pass
        
        return "N/A"
    
    def download_image(self, image_url, name):
        """Download and save image."""
        try:
            response = requests.get(image_url, stream=True, timeout=5)
            if response.status_code == 200:
                # Save image to a temporary location
                safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
                image_path = os.path.join(self.temp_dir, f"{safe_name}_{uuid.uuid4().hex[:8]}.jpg")
                
                with open(image_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                
                return image_path
        except:
            pass
        
        return "N/A"

class DataCollectorThread(QThread):
    """Thread for collecting data from Google Maps."""
    
    progress_updated = pyqtSignal(int)
    data_collected = pyqtSignal(dict)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    proxy_rotated = pyqtSignal(str)
    entry_skipped = pyqtSignal(str)  # Signal for skipped entries
    real_time_update = pyqtSignal(dict)  # Signal for real-time table updates
    connection_status_changed = pyqtSignal(bool)  # Signal for connection status changes
    
    def __init__(self, search_query, location, state, country, num_entries, chromedriver_path=None, 
                 api_key=None, proxy_manager=None, skip_missing_social=False, parent=None):
        super().__init__(parent)
        self.search_query = search_query
        self.location = location
        self.state = state
        self.country = country
        self.num_entries = num_entries
        self.chromedriver_path = chromedriver_path
        self.api_key = api_key
        self.proxy_manager = proxy_manager
        self.skip_missing_social = skip_missing_social
        self.is_running = True
        self.is_paused = False  # For pausing when connection is poor
        self.temp_dir = os.path.join(os.path.expanduser('~'), 'temp_data_collector')
        os.makedirs(self.temp_dir, exist_ok=True)
        self.email_extractor = EmailExtractor()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0)"
        ]
        self.request_count = 0
        self.last_request_time = 0
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(4)  # Process up to 4 entries in parallel
        self.collected_count = 0
        self.skipped_count = 0
        self.processed_count = 0
        self.max_to_process = self.num_entries * 5  # Process up to 5x the target to find enough valid entries
        self.internet_connected = True  # Assume connected initially
        
        # Register cleanup on exit
        import atexit
        atexit.register(self.cleanup)
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            if os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def rate_limit(self):
        """Implement rate limiting to avoid detection."""
        self.request_count += 1
        current_time = time.time()
        
        # Calculate delay based on request count
        if self.request_count > 20:
            delay = random.uniform(1, 2)  # Reduced delay
        elif self.request_count > 10:
            delay = random.uniform(0.5, 1)  # Reduced delay
        else:
            delay = random.uniform(0.1, 0.5)  # Reduced delay
        
        # Ensure minimum time between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < delay:
            time.sleep(delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def rotate_user_agent(self):
        """Rotate user agent."""
        return random.choice(self.user_agents)
    
    def setup_driver(self):
        """Setup WebDriver with anti-detection measures and optimizations."""
        browser_manager = BrowserManager(
            headless=True, 
            chromedriver_path=self.chromedriver_path
        )
        
        # Setup proxy if available
        proxy = None
        if self.proxy_manager:
            proxy = self.proxy_manager.get_next_proxy()
            if proxy:
                self.proxy_rotated.emit(f"Using proxy: {proxy}")
        
        driver = browser_manager.create_driver(proxy=proxy)
        return driver, proxy
    
    def run(self):
        """Main thread execution method."""
        driver = None
        try:
            self.status_updated.emit("Initializing data collection...")
            
            # Try using Google Places API first if API key is provided
            if self.api_key:
                self.status_updated.emit("Using Google Places API...")
                api_results = self.collect_via_api()
                if api_results:
                    self.status_updated.emit("API collection completed successfully")
                    self.finished.emit()
                    return
            
            # Fallback to web scraping
            self.status_updated.emit("Initializing web driver...")
            driver, proxy = self.setup_driver()
            
            self.status_updated.emit("Navigating to Google Maps...")
            
            # Navigate to Google Maps
            search_term = f"{self.search_query} {self.location}"
            if self.state and self.state != "N/A":
                search_term += f", {self.state}"
            
            browser_manager = BrowserManager()
            browser_manager.driver = driver
            browser_manager.navigate_to_google_maps(search_term)
            
            self.status_updated.emit("Waiting for search results...")
            
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
            
            found_results = False
            selector_by, selector_value = None, None
            for by, value in selectors:
                try:
                    WebDriverWait(driver, 10).until(  # Reduced timeout
                        EC.presence_of_element_located((by, value))
                    )
                    found_results = True
                    selector_by, selector_value = by, value
                    self.status_updated.emit(f"Found results using selector: {value}")
                    break
                except TimeoutException:
                    self.status_updated.emit(f"Selector {value} timed out, trying next...")
                    continue
            
            if not found_results:
                # Check if there's a "No results" message
                try:
                    no_results = driver.find_element(By.XPATH, "//*[contains(text(), 'No results')]")
                    if no_results:
                        self.error_occurred.emit("No results found for your search query. Try different keywords or location.")
                        return
                except:
                    pass
                
                # Save page source for debugging
                page_source = driver.page_source
                debug_file = os.path.join(self.temp_dir, "debug_page.html")
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                
                self.error_occurred.emit(f"Timeout while waiting for search results to load. Debug information saved to {debug_file}")
                return
            
            self.status_updated.emit("Starting data collection...")
            consecutive_errors = 0
            
            while self.collected_count < self.num_entries and self.processed_count < self.max_to_process and self.is_running and consecutive_errors < 3:
                # Check if we should pause due to poor internet connection
                if not self.internet_connected:
                    self.status_updated.emit("Internet connection lost. Pausing data collection...")
                    self.is_paused = True
                    
                    # Wait for connection to be restored
                    while not self.internet_connected and self.is_running:
                        time.sleep(1)  # Check every second
                    
                    if not self.is_running:
                        break
                    
                    self.status_updated.emit("Internet connection restored. Resuming data collection...")
                    self.is_paused = False
                    continue
                
                try:
                    # Rate limiting
                    self.rate_limit()
                    
                    # Get all result elements using the found selector
                    results = driver.find_elements(selector_by, selector_value)
                    
                    if self.processed_count >= len(results):
                        # Load more results if needed
                        self.status_updated.emit("Loading more results...")
                        if not browser_manager.load_more_results():
                            self.status_updated.emit("No more results available.")
                            break
                        
                        # Get updated results
                        results = driver.find_elements(selector_by, selector_value)
                        if self.processed_count >= len(results):
                            self.status_updated.emit("No additional results loaded.")
                            break
                    
                    # Process up to 4 entries in parallel
                    batch_size = min(4, len(results) - self.processed_count, self.max_to_process - self.processed_count)
                    if batch_size <= 0:
                        break
                    
                    self.status_updated.emit(f"Processing batch of {batch_size} entries...")
                    
                    # Create and run worker threads for this batch
                    workers = []
                    for i in range(batch_size):
                        result_index = self.processed_count + i
                        worker = DataProcessor(
                            driver, 
                            results[result_index], 
                            result_index, 
                            self.temp_dir, 
                            self.email_extractor,
                            self.skip_missing_social
                        )
                        worker.signals.data_ready.connect(self.handle_data_ready)
                        worker.signals.error.connect(self.handle_worker_error)
                        worker.signals.skipped.connect(self.handle_entry_skipped)
                        workers.append(worker)
                    
                    # Start all workers
                    for worker in workers:
                        self.thread_pool.start(worker)
                    
                    # Wait for all workers to complete
                    self.thread_pool.waitForDone(30000)  # 30 seconds timeout
                    
                    self.processed_count += batch_size
                    self.progress_updated.emit(int((self.collected_count / self.num_entries) * 100))
                    self.status_updated.emit(f"Processed {self.processed_count} entries, collected {self.collected_count} valid entries")
                    
                    # Rotate IP periodically if using proxy manager
                    if self.proxy_manager and self.processed_count % 10 == 0:
                        self.status_updated.emit("Rotating IP address...")
                        if self.proxy_manager.rotate_ip():
                            self.proxy_rotated.emit("IP address rotated successfully")
                        else:
                            self.proxy_rotated.emit("Failed to rotate IP address")
                    
                except Exception as e:
                    self.status_updated.emit(f"Error processing batch: {str(e)}")
                    consecutive_errors += 1
                    continue
            
            # Check if we collected enough entries
            if self.collected_count < self.num_entries:
                self.status_updated.emit(f"Warning: Only collected {self.collected_count} of {self.num_entries} requested entries.")
                if self.skip_missing_social:
                    self.status_updated.emit(f"Consider disabling 'Skip entries without website or Instagram' to collect more entries.")
            
            self.finished.emit()
            
        except WebDriverException as e:
            error_msg = f"WebDriver error: {str(e)}. "
            if not self.chromedriver_path:
                error_msg += "Please ensure ChromeDriver is installed and compatible with your Chrome browser."
            else:
                error_msg += "Please check the ChromeDriver path and ensure it's compatible with your Chrome browser."
            self.error_occurred.emit(error_msg)
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {str(e)}")
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except:
                    pass
    
    def handle_data_ready(self, data):
        """Handle data ready signal from worker."""
        # Add country, location, state, and search query to the data
        data['country'] = self.country
        data['location'] = self.location
        data['state'] = self.state
        data['search_query'] = self.search_query
        
        # Emit signals for both real-time update and data collection
        self.real_time_update.emit(data)
        self.data_collected.emit(data)
        
        # Update counters
        self.collected_count += 1
        self.progress_updated.emit(int((self.collected_count / self.num_entries) * 100))
    
    def handle_worker_error(self, error_message):
        """Handle worker error signal."""
        self.status_updated.emit(error_message)
    
    def handle_entry_skipped(self, message):
        """Handle entry skipped signal."""
        self.skipped_count += 1
        self.entry_skipped.emit(message)
    
    def set_connection_status(self, is_connected):
        """Set the internet connection status."""
        self.internet_connected = is_connected
        self.connection_status_changed.emit(is_connected)
    
    def collect_via_api(self):
        """Collect data using Google Places API."""
        if not self.api_key:
            return False
            
        api = GooglePlacesAPI(self.api_key)
        places = api.search_places(self.search_query, self.location)
        
        if not places:
            return False
            
        collected_count = 0
        for place in places:
            if not self.is_running or collected_count >= self.num_entries:
                break
                
            place_id = place.get('place_id')
            if not place_id:
                continue
                
            details = api.get_place_details(place_id)
            if not details:
                continue
                
            # Extract data from API response
            data = {
                'country': self.country,
                'location': self.location,
                'state': self.state,
                'search_query': self.search_query,
                'name': details.get('name', 'N/A'),
                'phone': details.get('formatted_phone_number', 'N/A'),
                'website': details.get('website', 'N/A'),
                'email': 'N/A',  # API doesn't provide emails
                'instagram': 'N/A',  # API doesn't provide Instagram
                'address': place.get('formatted_address', 'N/A'),
                'hours': json.dumps(details.get('opening_hours', {}).get('weekday_text', [])),
                'products_services': 'N/A',  # API doesn't provide products/services
                'image_path': 'N/A'
            }
            
            # Extract email from website if available
            if data['website'] != 'N/A':
                data['email'] = self.email_extractor.extract_emails(data['website'])[0]
            
            # Download first image if available
            photos = details.get('photos', [])
            if photos:
                photo_reference = photos[0].get('photo_reference')
                if photo_reference:
                    image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={self.api_key}"
                    data['image_path'] = self.download_image(image_url, data.get('name', 'unknown'))
            
            # Check if we should skip this entry
            if self.skip_missing_social and data.get('website') == "N/A" and data.get('instagram') == "N/A":
                self.skipped_count += 1
                self.entry_skipped.emit(f"Skipped entry {collected_count + 1} ({data.get('name', 'Unknown')}) - Address: {data.get('address', 'N/A')} - No website or Instagram")
            else:
                # Emit signals for both real-time update and data collection
                self.real_time_update.emit(data)
                self.data_collected.emit(data)
                collected_count += 1
                self.progress_updated.emit(int((collected_count / self.num_entries) * 100))
                self.status_updated.emit(f"Collected {collected_count} of {self.num_entries} entries via API")
            
            # Rate limiting for API
            time.sleep(random.uniform(0.1, 0.3))  # Reduced delay
        
        return True
    
    def download_image(self, image_url, name):
        """Download and save image."""
        try:
            response = requests.get(image_url, stream=True, timeout=5)
            if response.status_code == 200:
                # Save image to a temporary location
                safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
                image_path = os.path.join(self.temp_dir, f"{safe_name}_{uuid.uuid4().hex[:8]}.jpg")
                
                with open(image_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                
                return image_path
        except:
            pass
        
        return "N/A"
    
    def stop(self):
        """Stop the data collection process."""
        self.is_running = False

class GooglePlacesAPI:
    """Wrapper for Google Places API."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        })
        # Set timeout for requests
        self.session.timeout = 10
    
    def search_places(self, query, location, radius=5000):
        """Search for places using Google Places API."""
        endpoint = f"{self.base_url}/textsearch/json"
        params = {
            "query": f"{query} in {location}",
            "radius": radius,
            "key": self.api_key
        }
        
        try:
            response = self.session.get(endpoint, params=params)
            if response.status_code == 200:
                results = response.json().get('results', [])
                return results
        except Exception as e:
            print(f"API search error: {str(e)}")
        return []
    
    def get_place_details(self, place_id):
        """Get detailed information about a place."""
        endpoint = f"{self.base_url}/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,formatted_phone_number,website,opening_hours,photos,review",
            "key": self.api_key
        }
        
        try:
            response = self.session.get(endpoint, params=params)
            if response.status_code == 200:
                return response.json().get('result', {})
        except Exception as e:
            print(f"API details error: {str(e)}")
        return {}