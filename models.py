"""Data models used throughout the application."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set

@dataclass
class ScrapedItem:
    """Represents a scraped data item from a website."""
    email: str = ""
    name: str = ""
    website: str = ""
    platform: str = ""
    niche: str = ""
    instagram: str = ""
    social: str = ""  # other social links (comma-separated)
    whatsapp: str = ""
    location: str = ""
    address: str = ""
    source_page: int = 0

@dataclass
class BusinessData:
    """Represents complete business data collected from various sources."""
    name: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""
    instagram: str = ""
    country: str = ""
    state: str = ""
    location: str = ""
    address: str = ""
    hours: str = ""
    products_services: str = ""
    image_path: str = ""
    search_query: str = ""