"""Application settings management."""

import json
import os

class SettingsManager:
    """Manages application settings persistence and retrieval."""
    
    DEFAULT_SETTINGS = {
        'api_key': '',
        'use_proxy': False,
        'proxy_file': '',
        'use_tor': False,
        'theme': 'Light',
        'thread_count': 4,
        'batch_size': 4,
        'skip_missing_social': True,
        'requests_per_minute': 20,
        'random_delay_min': 1,
        'random_delay_max': 2,
        'validate_phone': True,
        'validate_email': True,
        'validate_website': True,
        'enable_web_scraping': True,
        'web_scraping_workers': 5
    }
    
    def __init__(self):
        self.settings_file = os.path.join(os.path.expanduser('~'), 'data_collector_settings.json')
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings.update(json.load(f))
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value."""
        self.settings[key] = value
    
    def update(self, new_settings):
        """Update multiple settings."""
        self.settings.update(new_settings)