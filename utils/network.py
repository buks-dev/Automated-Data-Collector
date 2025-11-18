"""Network utility classes and functions."""

import socket
import time
import requests
import random
import os
from PyQt5.QtCore import QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Try to import stem, but make it optional
try:
    import stem.process
    from stem.util import term
    TOR_AVAILABLE = True
except ImportError:
    TOR_AVAILABLE = False

class InternetConnectionChecker(QThread):
    """Checks internet connection status in a background thread."""
    
    connection_status_changed = pyqtSignal(bool)  # True if connected, False if disconnected
    
    def __init__(self):
        super().__init__()
        self.is_running = True
        self.check_interval = 5  # Check every 5 seconds
        self.timeout = 3  # Timeout for each check
        
    def run(self):
        while self.is_running:
            is_connected = self.check_internet_connection()
            self.connection_status_changed.emit(is_connected)
            time.sleep(self.check_interval)
    
    def check_internet_connection(self):
        try:
            # Try to connect to Google's DNS
            socket.create_connection(("8.8.8.8", 53), timeout=self.timeout)
            return True
        except OSError:
            pass
        
        try:
            # Try to connect to Google's website
            response = requests.get("https://www.google.com", timeout=self.timeout)
            return response.status_code == 200
        except:
            pass
        
        return False
    
    def stop(self):
        self.is_running = False

class ProxyManager:
    """Manages proxy rotation and Tor functionality."""
    
    def __init__(self):
        self.proxies = []
        self.current_proxy_index = 0
        self.tor_process = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        })
        # Set timeout for requests
        self.session.timeout = 10
        
    def load_proxies(self, proxy_file=None):
        """Load proxies from file or use free proxy sources."""
        if proxy_file and os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
        else:
            # Fetch free proxies (in production, use a paid service)
            try:
                response = requests.get('https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc', timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.proxies = [f"{p['ip']}:{p['port']}" for p in data.get('data', [])]
            except:
                pass
        
        # Add Tor as a fallback if available
        if TOR_AVAILABLE:
            self.proxies.append("127.0.0.1:9050")  # Default Tor port
        
        return len(self.proxies) > 0
    
    def start_tor(self):
        """Start Tor process."""
        if not TOR_AVAILABLE:
            print("Tor functionality not available. Install 'stem' module to enable Tor.")
            return False
            
        try:
            self.tor_process = stem.process.launch_tor_with_config(
                config = {
                    'SocksPort': '9050',
                    'ExitNodes': '{us}',
                },
                init_msg_handler = print
            )
            return True
        except Exception as e:
            print(f"Failed to start Tor: {str(e)}")
            return False
    
    def stop_tor(self):
        """Stop Tor process."""
        if self.tor_process:
            self.tor_process.terminate()
            self.tor_process = None
    
    def get_next_proxy(self):
        """Get the next proxy in rotation."""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy
    
    def test_proxy(self, proxy, timeout=5):
        """Test if a proxy is working."""
        try:
            proxies = {
                'http': f'socks5://{proxy}',
                'https': f'socks5://{proxy}'
            }
            response = self.session.get('https://httpbin.org/ip', proxies=proxies, timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def rotate_ip(self):
        """Rotate IP using Tor or proxy."""
        if self.tor_process and TOR_AVAILABLE:
            # Tor circuit renewal
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(("127.0.0.1", 9050))
                    s.sendall(b'SIGNAL NEWNYM\r\n')
                return True
            except:
                return False
        return False