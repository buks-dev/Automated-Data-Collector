# core/web_scraping.py
"""Web scraping logic for Google search results."""

import time
import random
import re
import threading
import concurrent.futures
from typing import Dict, List, Optional, Tuple, Set
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QRunnable
from bs4 import BeautifulSoup
import requests

from models import ScrapedItem
from config import ECOM_PLATFORM_QUERIES
from utils.data_extraction import DataExtractor

class WebScrapeWorkerSignals(QObject):
    """Signals for web scraping worker."""
    progress = pyqtSignal(str)  # Status messages
    row_found = pyqtSignal(object)
    finished_ok = pyqtSignal()
    finished_err = pyqtSignal(str)
    update_progress = pyqtSignal(int, int)  # Current, total
    network_issue = pyqtSignal()

class WebScrapeWorker(QRunnable):
    """Worker for web scraping Google search results."""
    
    def __init__(self, params: Dict):
        super().__init__()
        self.params = params
        self.signals = WebScrapeWorkerSignals()
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._processed_count = 0
        self._total_count = 0
        self._paused = threading.Event()
        self._paused.clear()  # Not paused initially
        
    def stop(self):
        self._stop.set()
        
    def pause(self):
        self._paused.set()
        
    def resume(self):
        self._paused.clear()
        
    def is_paused(self):
        return self._paused.is_set()
        
    def _process_site(self, page_no, site_url):
        if self._stop.is_set():
            return None
            
        try:
            # Check if we're paused
            while self._paused.is_set() and not self._stop.is_set():
                time.sleep(0.5)
                
            if self._stop.is_set():
                return None
                
            self.signals.progress.emit(f"Scanning: {site_url}")
            html = fetch_url(site_url, timeout=15)
            if not html:
                return None
                
            # First check if we can extract an email - if not, skip this site
            emails = DataExtractor.extract_emails(html)
            if not emails:
                return None
                
            soup = BeautifulSoup(html, "lxml")
            item = ScrapedItem()
            item.website = site_url
            item.location = self.params["location"]
            item.source_page = page_no
            
            # Add email (first one found)
            item.email = emails[0]
            
            # Detect platform & e-commerce hints
            item.platform = DataExtractor.detect_platform(html)
            
            # Guess name & niche
            item.name = DataExtractor.guess_name(soup)
            item.niche = DataExtractor.guess_niche(soup)
            
            # socials
            insta, socials = DataExtractor.extract_socials(html)
            item.instagram = insta
            if socials:
                # remove instagram from "other"
                other = {k: v for k, v in socials.items() if k != "Instagram"}
                item.social = ", ".join([f"{k}: {v}" for k, v in other.items()]) if other else ""
                
            # WhatsApp - use N/A if not found
            whatsapp = DataExtractor.extract_whatsapp(html)
            item.whatsapp = whatsapp if whatsapp else "N/A"
            
            # Extract address
            item.address = DataExtractor.extract_address(html)
            
            # If ecommerce_only is on with a chosen platform, drop non-matching platforms
            if self.params["ecommerce_only"] and self.params["platform"] != "Any":
                chosen = self.params["platform"]
                if chosen in ECOM_PLATFORM_QUERIES:
                    if item.platform and item.platform != chosen:
                        return None
            
            with self._lock:
                self._processed_count += 1
                self.signals.update_progress.emit(self._processed_count, self._total_count)
                
            return item
        except Exception as e:
            with self._lock:
                self._processed_count += 1
                self.signals.update_progress.emit(self._processed_count, self._total_count)
            return None
            
    def _sleep(self, adaptive=False):
        if adaptive:
            # Adaptive delay based on response times
            dmin = self.params.get("delay_min", 0.5)  # Reduced minimum
            dmax = self.params.get("delay_max", 1.5)  # Reduced maximum
        else:
            dmin = self.params.get("delay_min", 1.0)
            dmax = self.params.get("delay_max", 2.5)
        time.sleep(random.uniform(dmin, dmax))
        
    def run(self):
        try:
            self._run_logic()
            if not self._stop.is_set():
                self.signals.finished_ok.emit()
        except Exception as e:
            self.signals.finished_err.emit(str(e))
            
    def _run_logic(self):
        q = self.params["query"].strip()
        loc = self.params["location"].strip()
        niche = self.params["niche"].strip()
        pages = int(self.params["pages"])
        ecommerce_only = bool(self.params["ecommerce_only"])
        platform = self.params["platform"]
        use_browser = bool(self.params["use_browser"])
        headless = bool(self.params.get("headless", True))
        max_workers = int(self.params.get("max_workers", 5))  # New parameter
        
        queries = build_google_queries(q, loc, niche, ecommerce_only, platform)
        all_links: List[Tuple[int, str]] = []
        
        if use_browser:
            self.signals.progress.emit("Launching browser...")
            from utils.browser import BrowserManager
            browser_manager = BrowserManager(headless=headless)
            driver = browser_manager.create_driver()
            
            try:
                for qtext in queries:
                    if self._stop.is_set(): 
                        return
                    self.signals.progress.emit(f"Searching: {qtext}")
                    driver.get("https://www.google.com/")
                    time.sleep(random.uniform(1.0, 2.0))  # Reduced delay
                    box = driver.find_element(By.NAME, "q")
                    box.clear()
                    box.send_keys(qtext)
                    time.sleep(random.uniform(0.2, 0.5))  # Reduced delay
                    box.send_keys(Keys.ENTER)
                    links = selenium_collect_serp_links(driver, pages)
                    for i, link in enumerate(links):
                        all_links.append((i // 10 + 1, link))  # approx page no
            finally:
                driver.quit()
        else:
            # Use a session for connection pooling
            session = requests.Session()
            session.headers.update(random_header())
            
            for qtext in queries:
                if self._stop.is_set(): 
                    return
                self.signals.progress.emit(f"Fetching SERPs: {qtext}")
                
                # Fetch multiple SERP pages concurrently
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    future_to_page = {
                        executor.submit(self._fetch_serp_page, session, qtext, page_idx): page_idx 
                        for page_idx in range(pages)
                    }
                    
                    for future in concurrent.futures.as_completed(future_to_page):
                        if self._stop.is_set():
                            executor.shutdown(wait=False)
                            return
                            
                        page_idx = future_to_page[future]
                        try:
                            links = future.result()
                            for link in links:
                                all_links.append((page_idx + 1, link))
                            self._sleep(adaptive=True)
                        except Exception as e:
                            self.signals.progress.emit(f"SERP fetch failed (page {page_idx+1}): {str(e)}")
        
        # Deduplicate links
        seen = set()
        uniq_links: List[Tuple[int, str]] = []
        for p, u in all_links:
            if u not in seen:
                seen.add(u)
                uniq_links.append((p, u))
        
        self._total_count = len(uniq_links)
        self.signals.progress.emit(f"Visiting {len(uniq_links)} result pages...")
        
        # Process sites concurrently with a thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_site = {
                executor.submit(self._process_site, page_no, site_url): (page_no, site_url)
                for page_no, site_url in uniq_links
            }
            
            for future in concurrent.futures.as_completed(future_to_site):
                if self._stop.is_set():
                    executor.shutdown(wait=False)
                    return
                    
                page_no, site_url = future_to_site[future]
                try:
                    item = future.result()
                    if item:
                        self.signals.row_found.emit(item)
                except Exception as e:
                    self.signals.progress.emit(f"Error processing {site_url}: {str(e)}")
    
    def _fetch_serp_page(self, session, qtext, page_idx):
        if self._stop.is_set():
            return []
            
        # Check if we're paused
        while self._paused.is_set() and not self._stop.is_set():
            time.sleep(0.5)
            
        if self._stop.is_set():
            return []
            
        url = google_serp_page_url(qtext, page_idx)
        try:
            r = session.get(url, timeout=20)
            if r.status_code == 200 and r.text:
                return parse_serp_links(r.text)
            return []
        except Exception:
            return []

def random_header() -> Dict[str, str]:
    """Return a random user agent header."""
    from config import DEFAULT_HEADERS
    return {"User-Agent": random.choice(DEFAULT_HEADERS), "Accept-Language": "en-US,en;q=0.9"}

def is_valid_result_link(href: str) -> bool:
    """Check if a URL is a valid result link."""
    if not href or "google." in href or href.startswith("/"):
        return False
    # filter some common non-merchant results
    bad = ["webcache.googleusercontent", "policies.google", "accounts.google", "youtube.com/results"]
    return not any(b in href for b in bad)

def is_landing_page(url: str) -> bool:
    """Check if URL is likely a landing page and not a product page."""
    # Skip URLs with product patterns
    product_patterns = [
        '/product/', '/products/', '/item/', '/items/', '/p/', 
        '/collection/', '/collections/', '/category/', '/categories/',
        '/shop/', '/store/'
    ]
    
    url_lower = url.lower()
    return not any(pattern in url_lower for pattern in product_patterns)

def build_google_queries(query: str, location: str, niche: str, ecommerce_only: bool, platform: str) -> List[str]:
    """Build Google search queries based on parameters."""
    base = f'{query} {location} {niche}'.strip()
    if not ecommerce_only or platform not in ECOM_PLATFORM_QUERIES:
        return [base]
    plat_bits = " ".join(ECOM_PLATFORM_QUERIES[platform])
    return [f'{base} {plat_bits}']

def fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch URL content with timeout."""
    try:
        r = requests.get(url, headers=random_header(), timeout=timeout)
        if r.status_code == 200 and r.text:
            return r.text
        return None
    except Exception:
        return None

def parse_serp_links(html: str) -> List[str]:
    """Parse SERP links from HTML."""
    soup = BeautifulSoup(html, "lxml")
    results: List[str] = []
    # Try robust selectors
    for a in soup.select("#search a[href], a[jsname][href]"):
        href = a.get("href", "")
        if is_valid_result_link(href) and is_landing_page(href):
            results.append(href)
    # Deduplicate, preserve order
    seen: Set[str] = set()
    unique = []
    for u in results:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique

def google_serp_page_url(q: str, page_idx: int) -> str:
    """Generate Google SERP page URL."""
    start = page_idx * 10
    return f"https://www.google.com/search?q={requests.utils.quote(q)}&num=10&start={start}&hl=en"

def selenium_collect_serp_links(driver, pages: int) -> List[str]:
    """Collect SERP links using Selenium."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    
    links: List[str] = []
    for page in range(pages):
        time.sleep(random.uniform(1.2, 2.8))  # human-like pause
        soup = BeautifulSoup(driver.page_source, "lxml")
        page_links = parse_serp_links(str(soup))
        for u in page_links:
            if u not in links:
                links.append(u)
        # paginate
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.END)
        time.sleep(random.uniform(0.8, 1.6))
        try:
            next_link = driver.find_element(By.XPATH, "//a[@id='pnnext' or contains(@aria-label,'Next')]")
            driver.execute_script("arguments[0].click();", next_link)
        except Exception:
            break
    return links