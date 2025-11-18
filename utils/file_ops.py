"""File operation utilities."""

import os
import json
import shutil
import pandas as pd
import datetime
from typing import List, Dict, Any

class FileManager:
    """Manages file operations for the application."""
    
    @staticmethod
    def create_export_directory(base_dir: str) -> str:
        """Create a timestamped directory for exporting data."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        export_folder = os.path.join(base_dir, f"data_collection_{timestamp}")
        os.makedirs(export_folder, exist_ok=True)
        return export_folder
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], file_path: str) -> bool:
        """Export data to a CSV file."""
        try:
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def export_to_json(data: List[Dict[str, Any]], file_path: str) -> bool:
        """Export data to a JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def copy_image(source_path: str, dest_dir: str, name: str) -> str:
        """Copy an image to the destination directory with a safe filename."""
        import re
        
        if not os.path.exists(source_path):
            return ""
        
        # Create a safe filename from the business name
        safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
        if not safe_name:
            safe_name = "image"
        
        dest_path = os.path.join(dest_dir, f"{safe_name}.jpg")
        
        # Handle duplicate filenames
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(dest_dir, f"{safe_name}_{counter}.jpg")
            counter += 1
        
        try:
            shutil.copy2(source_path, dest_path)
            return dest_path
        except Exception as e:
            print(f"Error copying image: {e}")
            return ""
    
    @staticmethod
    def cleanup_temp_directory(temp_dir: str):
        """Clean up temporary directory."""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error cleaning up temp directory: {e}")