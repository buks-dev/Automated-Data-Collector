"""Dialog windows for the application."""

import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QGroupBox, QFormLayout, QSpinBox, QCheckBox, 
                            QRadioButton, QButtonGroup, QScrollArea, QDialogButtonBox, 
                            QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from config import THEMES

class SettingsDialog(QDialog):
    """Settings dialog for configuring application options."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Settings")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Main layout for the dialog
        main_layout = QVBoxLayout(self)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create a widget to hold all settings
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # API Key section
        api_group = QGroupBox("Google Places API")
        api_layout = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Google Places API key")
        api_layout.addRow("API Key:", self.api_key_input)
        
        api_group.setLayout(api_layout)
        settings_layout.addWidget(api_group)
        
        # Theme selection section
        theme_group = QGroupBox("Appearance")
        theme_layout = QVBoxLayout()
        
        self.theme_group = QButtonGroup(self)
        
        self.light_theme_radio = QRadioButton("Light Theme")
        self.light_theme_radio.setChecked(True)
        self.theme_group.addButton(self.light_theme_radio)
        
        self.dark_theme_radio = QRadioButton("Dark Theme")
        self.theme_group.addButton(self.dark_theme_radio)
        
        self.blue_theme_radio = QRadioButton("Blue Theme")
        self.theme_group.addButton(self.blue_theme_radio)
        
        self.green_theme_radio = QRadioButton("Green Theme")
        self.theme_group.addButton(self.green_theme_radio)
        
        theme_layout.addWidget(self.light_theme_radio)
        theme_layout.addWidget(self.dark_theme_radio)
        theme_layout.addWidget(self.blue_theme_radio)
        theme_layout.addWidget(self.green_theme_radio)
        
        theme_group.setLayout(theme_layout)
        settings_layout.addWidget(theme_group)
        
        # Proxy settings
        proxy_group = QGroupBox("Proxy Settings")
        proxy_layout = QVBoxLayout()
        
        self.use_proxy_checkbox = QCheckBox("Use proxy rotation")
        proxy_layout.addWidget(self.use_proxy_checkbox)
        
        proxy_file_layout = QHBoxLayout()
        self.proxy_file_input = QLineEdit()
        self.proxy_file_input.setPlaceholderText("Path to proxy list file (optional)")
        self.proxy_file_button = QPushButton("Browse...")
        self.proxy_file_button.clicked.connect(self.browse_proxy_file)
        
        proxy_file_layout.addWidget(self.proxy_file_input)
        proxy_file_layout.addWidget(self.proxy_file_button)
        proxy_layout.addLayout(proxy_file_layout)
        
        self.use_tor_checkbox = QCheckBox("Use Tor for IP rotation")
        proxy_layout.addWidget(self.use_tor_checkbox)
        
        proxy_group.setLayout(proxy_layout)
        settings_layout.addWidget(proxy_group)
        
        # Performance settings
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QFormLayout()
        
        self.thread_count = QSpinBox()
        self.thread_count.setMinimum(1)
        self.thread_count.setMaximum(8)
        self.thread_count.setValue(4)
        perf_layout.addRow("Parallel Threads:", self.thread_count)
        
        self.batch_size = QSpinBox()
        self.batch_size.setMinimum(1)
        self.batch_size.setMaximum(10)
        self.batch_size.setValue(4)
        perf_layout.addRow("Batch Size:", self.batch_size)
        
        perf_group.setLayout(perf_layout)
        settings_layout.addWidget(perf_group)
        
        # Data filtering settings
        filter_group = QGroupBox("Data Filtering")
        filter_layout = QVBoxLayout()
        
        self.skip_missing_social_checkbox = QCheckBox("Skip entries without website or Instagram")
        self.skip_missing_social_checkbox.setChecked(True)
        filter_layout.addWidget(self.skip_missing_social_checkbox)
        
        filter_group.setLayout(filter_layout)
        settings_layout.addWidget(filter_group)
        
        # Rate limiting settings
        rate_group = QGroupBox("Rate Limiting")
        rate_layout = QFormLayout()
        
        self.requests_per_minute = QSpinBox()
        self.requests_per_minute.setMinimum(1)
        self.requests_per_minute.setMaximum(60)
        self.requests_per_minute.setValue(20)
        rate_layout.addRow("Requests per minute:", self.requests_per_minute)
        
        self.random_delay_min = QSpinBox()
        self.random_delay_min.setMinimum(1)
        self.random_delay_min.setMaximum(30)
        self.random_delay_min.setValue(1)
        rate_layout.addRow("Min delay (seconds):", self.random_delay_min)
        
        self.random_delay_max = QSpinBox()
        self.random_delay_max.setMinimum(1)
        self.random_delay_max.setMaximum(60)
        self.random_delay_max.setValue(2)
        rate_layout.addRow("Max delay (seconds):", self.random_delay_max)
        
        rate_group.setLayout(rate_layout)
        settings_layout.addWidget(rate_group)
        
        # Data validation settings
        validation_group = QGroupBox("Data Validation")
        validation_layout = QVBoxLayout()
        
        self.validate_phone_checkbox = QCheckBox("Validate phone numbers")
        self.validate_phone_checkbox.setChecked(True)
        validation_layout.addWidget(self.validate_phone_checkbox)
        
        self.validate_email_checkbox = QCheckBox("Validate email addresses")
        self.validate_email_checkbox.setChecked(True)
        validation_layout.addWidget(self.validate_email_checkbox)
        
        self.validate_website_checkbox = QCheckBox("Validate website URLs")
        self.validate_website_checkbox.setChecked(True)
        validation_layout.addWidget(self.validate_website_checkbox)
        
        validation_group.setLayout(validation_layout)
        settings_layout.addWidget(validation_group)
        
        # Web scraping settings
        web_group = QGroupBox("Web Scraping")
        web_layout = QVBoxLayout()
        
        self.enable_web_scraping_checkbox = QCheckBox("Enable Web Scraping for Google")
        self.enable_web_scraping_checkbox.setChecked(True)
        web_layout.addWidget(self.enable_web_scraping_checkbox)
        
        self.web_scraping_workers = QSpinBox()
        self.web_scraping_workers.setMinimum(1)
        self.web_scraping_workers.setMaximum(15)
        self.web_scraping_workers.setValue(5)
        web_layout.addWidget(QLabel("Concurrent Workers:"))
        web_layout.addWidget(self.web_scraping_workers)
        
        web_group.setLayout(web_layout)
        settings_layout.addWidget(web_group)
        
        # Set the widget as the scroll area's widget
        scroll_area.setWidget(settings_widget)
        
        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)
        
        # Buttons - now with Apply button
        buttons = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        
        # Store reference to parent for applying settings
        self.parent = parent
    
    def browse_proxy_file(self):
        """Browse for proxy file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Proxy List File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.proxy_file_input.setText(file_path)
    
    def get_settings(self):
        """Get current settings values."""
        theme = "Light"
        if self.dark_theme_radio.isChecked():
            theme = "Dark"
        elif self.blue_theme_radio.isChecked():
            theme = "Blue"
        elif self.green_theme_radio.isChecked():
            theme = "Green"
            
        return {
            'api_key': self.api_key_input.text(),
            'use_proxy': self.use_proxy_checkbox.isChecked(),
            'proxy_file': self.proxy_file_input.text(),
            'use_tor': self.use_tor_checkbox.isChecked(),
            'theme': theme,
            'thread_count': self.thread_count.value(),
            'batch_size': self.batch_size.value(),
            'skip_missing_social': self.skip_missing_social_checkbox.isChecked(),
            'requests_per_minute': self.requests_per_minute.value(),
            'random_delay_min': self.random_delay_min.value(),
            'random_delay_max': self.random_delay_max.value(),
            'validate_phone': self.validate_phone_checkbox.isChecked(),
            'validate_email': self.validate_email_checkbox.isChecked(),
            'validate_website': self.validate_website_checkbox.isChecked(),
            'enable_web_scraping': self.enable_web_scraping_checkbox.isChecked(),
            'web_scraping_workers': self.web_scraping_workers.value()
        }
    
    def set_theme(self, theme):
        """Set the theme radio button."""
        if theme == "Dark":
            self.dark_theme_radio.setChecked(True)
        elif theme == "Blue":
            self.blue_theme_radio.setChecked(True)
        elif theme == "Green":
            self.green_theme_radio.setChecked(True)
        else:
            self.light_theme_radio.setChecked(True)
    
    def apply_settings(self):
        """Apply settings without closing the dialog."""
        if self.parent:
            # Get the current settings
            new_settings = self.get_settings()
            
            # Apply theme immediately if changed
            current_theme = self.parent.settings.get('theme', 'Light')
            new_theme = new_settings.get('theme', 'Light')
            if current_theme != new_theme:
                self.parent.apply_theme(new_theme)
            
            # Update parent settings
            self.parent.settings = new_settings
            self.parent.save_settings()
            
            # Show confirmation message
            QMessageBox.information(self, "Settings Applied", "Settings have been applied successfully.")