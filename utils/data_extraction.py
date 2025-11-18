"""Data extraction utilities."""

import os
import re
import json
import uuid
import time
import random
import requests
import phonenumbers
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Tuple, Optional

class EmailExtractor:
    """Extracts email addresses from websites."""
    
    def __init__(self):
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Standard email
            r'\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email with spaces around @
            r'\b[A-Za-z0-9._%+-]+\s*\[\s*@\s*\]\s*[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email with [@] instead of @
            r'\b[A-Za-z0-9._%+-]+\(at\)[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email with (at)
            r'\b[A-Za-z0-9._%+-]+\s*\(a\)\s*[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email with (a)
        ]
        self.contact_keywords = ['contact', 'about', 'team', 'staff', 'reach', 'connect']
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        })
        # Set timeout for requests
        self.session.timeout = 10
    
    def extract_emails(self, url, max_pages=2):
        """Extract emails from a website and its contact pages."""
        emails = set()
        visited_urls = set()
        urls_to_visit = [url]
        
        for _ in range(max_pages):
            if not urls_to_visit:
                break
                
            current_url = urls_to_visit.pop(0)
            if current_url in visited_urls:
                continue
                
            visited_urls.add(current_url)
            
            try:
                response = self.session.get(current_url)
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract emails from text
                text = soup.get_text()
                for pattern in self.email_patterns:
                    found_emails = re.findall(pattern, text, re.IGNORECASE)
                    for email in found_emails:
                        # Clean up the email
                        clean_email = email.replace(' ', '').replace('[', '').replace(']', '').replace('(at)', '@').replace('(a)', '@')
                        if self.validate_email(clean_email):
                            emails.add(clean_email.lower())
                
                # Find links to contact pages
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if href and not href.startswith('mailto:') and not href.startswith('tel:'):
                        absolute_url = urljoin(current_url, href)
                        if self.is_contact_page(link.text.lower()) and absolute_url not in visited_urls:
                            urls_to_visit.append(absolute_url)
                            
            except Exception as e:
                print(f"Error extracting emails from {current_url}: {str(e)}")
                continue
        
        return list(emails) if emails else ["N/A"]
    
    def validate_email(self, email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def is_contact_page(self, text):
        """Check if a link text suggests it's a contact page."""
        return any(keyword in text for keyword in self.contact_keywords)

class DataExtractor:
    """Extracts various data from web pages."""
    
    @staticmethod
    def clean_text(s: str) -> str:
        """Clean text by normalizing whitespace."""
        return re.sub(r"\s+", " ", s or "").strip()
    
    @staticmethod
    def detect_platform(html: str) -> str:
        """Detect e-commerce platform from HTML content."""
        from config import PLATFORM_FINGERPRINTS
        
        for plat, patterns in PLATFORM_FINGERPRINTS.items():
            for pat in patterns:
                if re.search(pat, html, flags=re.I):
                    return plat
        return ""
    
    @staticmethod
    def extract_meta(soup: BeautifulSoup, *names) -> str:
        """Extract content from meta tags by name or property."""
        for n in names:
            tag = soup.find("meta", attrs={"name": n}) or soup.find("meta", attrs={"property": n})
            if tag and tag.get("content"):
                return DataExtractor.clean_text(tag["content"])
        return ""
    
    @staticmethod
    def extract_socials(html: str) -> Tuple[str, Dict[str, str]]:
        """Extract social media links from HTML."""
        from config import SOCIAL_PATTERNS
        
        socials = {}
        insta = ""
        for label, pat in SOCIAL_PATTERNS.items():
            m = re.search(pat, html, flags=re.I)
            if m:
                url = m.group(1)
                if label == "Instagram" and not insta:
                    insta = url
                socials[label] = url
        return insta, socials
    
    @staticmethod
    def extract_whatsapp(html: str) -> str:
        """Extract WhatsApp link from HTML."""
        from config import WHATSAPP_LINK, PHONE_REGEX
        
        m = re.search(WHATSAPP_LINK, html, flags=re.I)
        if m:
            return m.group(1)
        
        # fallback: if "whatsapp" appears near a phone-like pattern
        if "whatsapp" in html.lower():
            m2 = re.search(PHONE_REGEX, html, flags=re.I)
            if m2:
                return m2.group(0)
        return "N/A"
    
    @staticmethod
    def extract_emails(html: str) -> List[str]:
        """Extract email addresses from HTML."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, html)
        
        # Filter out common non-business emails
        filtered_emails = []
        for email in emails:
            if not any(skip in email.lower() for skip in ['privacy', 'support', 'info', 'contact', 'admin', 'noreply']):
                filtered_emails.append(email)
        return filtered_emails
    
    @staticmethod
    def extract_address(html: str) -> str:
        """Extract address information from HTML."""
        # Look for common address patterns
        address_patterns = [
            r'\d+\s+[\w\s]+,\s*[\w\s]+,\s*[\w\s]+,\s*\d{5}',
            r'\d+\s+[\w\s]+,\s*[\w\s]+,\s*\d{5}',
            r'\d+\s+[\w\s]+,\s*[\w\s]+'
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, html)
            if match:
                return DataExtractor.clean_text(match.group(0))
        
        # Check for address in structured data
        soup = BeautifulSoup(html, 'lxml')
        for itemtype in ['PostalAddress', 'LocalBusiness']:
            address_tag = soup.find(attrs={'itemtype': f'http://schema.org/{itemtype}'})
            if address_tag:
                address_parts = []
                for part in ['streetAddress', 'addressLocality', 'addressRegion', 'postalCode']:
                    tag = address_tag.find(attrs={'itemprop': part})
                    if tag:
                        address_parts.append(tag.get_text())
                if address_parts:
                    return ', '.join(address_parts)
        
        return ""
    
    @staticmethod
    def is_business_name(name: str) -> bool:
        """Check if the extracted name is likely a business name and not a generic title."""
        if not name or len(name) < 3:
            return False
        
        # Filter out generic page titles
        generic_terms = [
            'home', 'welcome', 'index', 'page not found', '404', 'access denied',
            'login', 'sign in', 'register', 'contact us', 'about us', 'privacy policy',
            'terms of service', 'sitemap', 'search results', 'category'
        ]
        
        name_lower = name.lower()
        return not any(term in name_lower for term in generic_terms)
    
    @staticmethod
    def guess_name(soup: BeautifulSoup) -> str:
        """Guess business name from HTML."""
        # Try business name from structured data first
        business_name = ""
        
        # Check for organization name in structured data
        org_tag = soup.find(attrs={'itemtype': 'http://schema.org/Organization'})
        if org_tag:
            name_tag = org_tag.find(attrs={'itemprop': 'name'})
            if name_tag:
                business_name = DataExtractor.clean_text(name_tag.get_text())
                if DataExtractor.is_business_name(business_name):
                    return business_name
        
        # Try logo alt text which often contains business name
        logo = soup.find('img', {'id': 'logo'}) or soup.find('img', {'class': 'logo'})
        if logo and logo.get('alt'):
            business_name = DataExtractor.clean_text(logo['alt'])
            if DataExtractor.is_business_name(business_name):
                return business_name
        
        # Try site title but clean it
        title = soup.title.text if soup.title else ""
        if title:
            # Remove common suffixes
            clean_title = re.sub(r'\s*[-|]\s*(Home|Welcome|Official Site|Page|Shop|Store)?$', '', title)
            clean_title = re.sub(r'\s*\|\s.*$', '', clean_title)  # Remove anything after |
            if DataExtractor.is_business_name(clean_title):
                return clean_title
        
        # Try h1 tag
        h1 = soup.find("h1")
        if h1:
            h1_text = DataExtractor.clean_text(h1.get_text())
            if DataExtractor.is_business_name(h1_text):
                return h1_text
        
        # Try site name from meta tags
        site_name = DataExtractor.extract_meta(soup, "og:site_name", "application-name", "twitter:title")
        if site_name and DataExtractor.is_business_name(site_name):
            return site_name
        
        # If all else fails, use domain name
        url_tag = soup.find('link', {'rel': 'canonical'})
        if url_tag and url_tag.get('href'):
            try:
                parsed = urlparse(url_tag['href'])
                domain = parsed.netloc
                if domain.startswith('www.'):
                    domain = domain[4:]
                # Remove TLD
                domain_parts = domain.split('.')
                if len(domain_parts) > 1:
                    return domain_parts[0].title()
            except:
                pass
        
        return ""
    
    @staticmethod
    def guess_niche(soup: BeautifulSoup) -> str:
        """Guess business niche from HTML."""
        desc = DataExtractor.extract_meta(soup, "description", "og:description")
        if desc:
            return desc
        # try common labels
        for sel in ["[itemprop=description]", ".product-description", ".about", ".site-description"]:
            el = soup.select_one(sel)
            if el:
                return DataExtractor.clean_text(el.get_text(" ", strip=True))
        return ""