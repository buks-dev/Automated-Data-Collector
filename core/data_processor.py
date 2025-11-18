"""Data processing utilities."""

import re
import json
import phonenumbers
import requests
from typing import Dict, List, Any

class DataProcessor:
    """Processes and validates collected data."""
    
    @staticmethod
    def clean_data_entry(data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a single data entry."""
        cleaned = {}
        
        # Clean name
        name = data.get('name', 'N/A')
        if name != 'N/A':
            name = name.strip()
            # Remove extra spaces within the name
            name = ' '.join(name.split())
        cleaned['name'] = name
        
        # Clean phone number
        phone = data.get('phone', 'N/A')
        if phone != 'N/A':
            # Remove all non-digit characters except for leading '+'
            phone = re.sub(r'[^\d+]', '', phone)
            # Ensure country code is present if it's a valid phone number
            if phone and not phone.startswith('+') and len(phone) >= 10:
                # Default to Nigeria country code if no country code is present
                phone = f"+234{phone[-10:]}" if len(phone) == 10 else f"+234{phone}"
        cleaned['phone'] = phone
        
        # Clean email
        email = data.get('email', 'N/A')
        if email != 'N/A':
            email = email.strip().lower()
        cleaned['email'] = email
        
        # Clean website
        website = data.get('website', 'N/A')
        if website != 'N/A':
            website = website.strip()
            # Ensure URL has proper format
            if not website.startswith(('http://', 'https://')):
                website = 'https://' + website
        cleaned['website'] = website
        
        # Clean Instagram
        instagram = data.get('instagram', 'N/A')
        if instagram != 'N/A':
            instagram = instagram.strip()
            # Ensure Instagram URL has proper format
            if not instagram.startswith(('http://', 'https://')):
                if instagram.startswith('@'):
                    instagram = f"https://instagram.com/{instagram[1:]}"
                else:
                    instagram = f"https://instagram.com/{instagram}"
        cleaned['instagram'] = instagram
        
        # Clean address
        address = data.get('address', 'N/A')
        if address != 'N/A':
            address = address.strip()
            # Remove extra spaces within the address
            address = ' '.join(address.split())
        cleaned['address'] = address
        
        # Clean other fields
        for field in ['country', 'state', 'location', 'hours', 'products_services', 'image_path']:
            value = data.get(field, 'N/A')
            if value != 'N/A' and isinstance(value, str):
                value = value.strip()
            cleaned[field] = value
        
        return cleaned
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate a phone number."""
        try:
            if phone and phone != 'N/A':
                parsed_number = phonenumbers.parse(phone, None)
                return phonenumbers.is_valid_number(parsed_number)
            return False
        except:
            return False
    
    @staticmethod
    def validate_email_address(email: str) -> bool:
        """Validate an email address."""
        if not email or email == 'N/A':
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_website_url(website: str) -> bool:
        """Validate a website URL."""
        if not website or website == 'N/A':
            return False
        
        try:
            response = requests.head(website, timeout=5)
            return response.status_code < 400
        except:
            return False
    
    @staticmethod
    def remove_duplicates(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entries from data list."""
        unique_entries = set()
        cleaned_data = []
        
        for item in data:
            # Create a unique key based on name and address
            name = item.get('name', '').strip().lower()
            address = item.get('address', '').strip().lower()
            unique_key = (name, address)
            
            # Skip if this is a duplicate entry
            if unique_key in unique_entries:
                continue
            
            # Add to unique entries set and cleaned data
            unique_entries.add(unique_key)
            cleaned_data.append(item)
        
        return cleaned_data
    
    @staticmethod
    def validate_data(data: List[Dict[str, Any]], settings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate all collected data based on settings."""
        validated_count = 0
        validated_data = []
        
        for i, item in enumerate(data):
            validated_item = item.copy()
            
            # Validate phone number
            if settings.get('validate_phone') and item.get('phone') != 'N/A':
                if not DataProcessor.validate_phone_number(item.get('phone')):
                    validated_item['phone'] = 'N/A (Invalid)'
            
            # Validate email
            if settings.get('validate_email') and item.get('email') != 'N/A':
                if not DataProcessor.validate_email_address(item.get('email')):
                    validated_item['email'] = 'N/A (Invalid)'
            
            # Validate website
            if settings.get('validate_website') and item.get('website') != 'N/A':
                if not DataProcessor.validate_website_url(item.get('website')):
                    validated_item['website'] = 'N/A (Invalid)'
            
            validated_data.append(validated_item)
            validated_count += 1
        
        return validated_data