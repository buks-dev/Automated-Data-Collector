# ui/main_window.py
import os
import sys
import re
import time
import random
import csv
import threading
import json
import datetime
import shutil
import atexit
import uuid
import socket
import phonenumbers
import requests
import pandas as pd
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog, 
    QProgressBar, QMessageBox, QGroupBox, QFormLayout, QSpinBox, 
    QStatusBar, QToolBar, QAction, QHeaderView, QAbstractItemView, 
    QTabWidget, QScrollArea, QSplitter, QCheckBox, QTextEdit, 
    QDialog, QDialogButtonBox, QRadioButton, QButtonGroup, QFrame,
    QGridLayout, QDoubleSpinBox, QPlainTextEdit, QSpacerItem,
    QSizePolicy, QSystemTrayIcon, QMenu, QStyle, QStackedWidget
)

# Import modular components
from ui.widgets import (
    SearchParametersCard, NetworkStatusCard, WebScrapingCard, 
    ResultsCard, LogsCard, SettingsDialog
)
from core.data_collection import DataCollectorThread
from core.web_scraping import WebScrapeWorker
from core.utils import (
    InternetConnectionChecker, ProxyManager, EmailExtractor, 
    THEMES, NIGERIAN_STATES
)
from core.models import ResultsModel, LogModel

class DataCollectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automated Data Collection Software")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize data storage
        self.collected_data = []
        self.unique_entries = set()  # Track unique entries to avoid duplicates
        self.web_scraped_data = []  # Store web scraped data
        self.web_unique_entries = set()  # Track unique web scraped entries
        self.current_directory = ""
        self.settings = {
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
        
        # Load settings if available
        self.load_settings()
        
        # Setup UI
        self.setup_ui()
        
        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup toolbar
        self.setup_toolbar()
        
        # Apply theme
        self.apply_theme(self.settings.get('theme', 'Light'))
        
        # Initialize proxy manager
        self.proxy_manager = ProxyManager()
        
        # Initialize internet connection checker
        self.connection_checker = InternetConnectionChecker()
        self.connection_checker.connection_status_changed.connect(self.handle_connection_status_change)
        self.connection_checker.start()
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def cleanup(self):
        """Clean up temporary files and stop threads"""
        try:
            temp_dir = os.path.join(os.path.expanduser('~'), 'temp_data_collector')
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            # Stop Tor if running
            if self.proxy_manager:
                self.proxy_manager.stop_tor()
                
            # Stop connection checker
            if hasattr(self, 'connection_checker'):
                self.connection_checker.stop()
                self.connection_checker.wait()
        except:
            pass
    
    def load_settings(self):
        """Load settings from file"""
        settings_file = os.path.join(os.path.expanduser('~'), 'data_collector_settings.json')
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    self.settings = json.load(f)
            except:
                pass
    
    def save_settings(self):
        """Save settings to file"""
        settings_file = os.path.join(os.path.expanduser('~'), 'data_collector_settings.json')
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f)
        except:
            pass
    
    def apply_theme(self, theme_name):
        """Apply the selected theme to the application"""
        theme = THEMES.get(theme_name, THEMES["Light"])
        
        style = f"""
            QMainWindow {{
                background-color: {theme["main_window"]};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {theme["group_box_border"]};
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
                background-color: {theme["group_box"]};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 7px;
                padding: 0px 5px 0px 5px;
                color: {theme["group_box_title"]};
            }}
            
            QPushButton {{
                background-color: {theme["button"]};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: {theme["button_hover"]};
            }}
            
            QPushButton:pressed {{
                background-color: {theme["button_pressed"]};
            }}
            
            QPushButton:disabled {{
                background-color: {theme["button_disabled"]};
                color: {theme["button_disabled_text"]};
            }}
            
            QTableWidget {{
                gridline-color: {theme["table_grid"]};
                background-color: {theme["table"]};
                border: 1px solid {theme["table_border"]};
                border-radius: 4px;
            }}
            
            QTableWidget::item {{
                padding: 5px;
            }}
            
            QTableWidget::item:selected {{
                background-color: {theme["table_selected"]};
                color: {theme["table_selected_text"]};
            }}
            
            QHeaderView::section {{
                background-color: {theme["header"]};
                color: {theme["header_text"]};
                padding: 5px;
                border: none;
                border-right: 1px solid {theme["header_border"]};
                border-bottom: 1px solid {theme["header_border"]};
            }}
            
            QComboBox {{
                border: 1px solid {theme["combobox_border"]};
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
                background-color: {theme["combobox"]};
            }}
            
            QLineEdit, QSpinBox {{
                border: 1px solid {theme["line_edit_border"]};
                border-radius: 4px;
                padding: 5px;
                background-color: {theme["line_edit"]};
            }}
            
            QProgressBar {{
                border: 1px solid {theme["progress_bar"]};
                border-radius: 4px;
                text-align: center;
                height: 20px;
                background-color: {theme["progress_bar"]};
            }}
            
            QProgressBar::chunk {{
                background-color: {theme["progress_bar_chunk"]};
            }}
            
            QToolBar {{
                background-color: {theme["toolbar"]};
                spacing: 5px;
            }}
            
            QToolBar QToolButton {{
                background-color: {theme["toolbar_button"]};
                color: {theme["toolbar_button_text"]};
                border: none;
                border-radius: 4px;
                padding: 5px;
            }}
            
            QToolBar QToolButton:hover {{
                background-color: {theme["toolbar_button_hover"]};
            }}
            
            QMenuBar {{
                background-color: {theme["menubar"]};
                color: {theme["menubar_text"]};
            }}
            
            QMenuBar::item:selected {{
                background-color: {theme["menubar_selected"]};
            }}
            
            QMenu {{
                background-color: {theme["menu"]};
                border: 1px solid {theme["menu_border"]};
                border-radius: 4px;
            }}
            
            QMenu::item:selected {{
                background-color: {theme["menu_selected"]};
            }}
            
            QCheckBox {{
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            
            QTextEdit {{
                border: 1px solid {theme["text_edit_border"]};
                border-radius: 4px;
                padding: 5px;
                background-color: {theme["text_edit"]};
            }}
            
            QLabel {{
                color: {theme["label"]};
            }}
            
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
            
            QTabWidget::pane {{
                border: 1px solid {theme["menu_border"]};
                background-color: {theme["group_box"]};
                border-radius: 4px;
            }}
            
            QTabBar::tab {{
                background-color: {theme["group_box"]};
                color: {theme["label"]};
                padding: 8px 16px;
                border: 1px solid {theme["menu_border"]};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {theme["main_window"]};
                color: {theme["button"]};
                border-bottom: 2px solid {theme["button"]};
            }}
        """
        
        self.setStyleSheet(style)
    
    def handle_connection_status_change(self, is_connected):
        """Handle changes in internet connection status"""
        if is_connected:
            self.status_bar.showMessage("Internet connection restored", 5000)
            if hasattr(self, 'connection_label'):
                self.connection_label.setText("Internet: Connected")
                self.connection_label.setStyleSheet("color: green;")
        else:
            self.status_bar.showMessage("Warning: Poor internet connection", 5000)
            if hasattr(self, 'connection_label'):
                self.connection_label.setText("Internet: Disconnected")
                self.connection_label.setStyleSheet("color: red;")
            
            # Notify collector thread about connection status
            if hasattr(self, 'collector_thread') and self.collector_thread:
                self.collector_thread.set_connection_status(is_connected)
            
            # Notify web scraper thread about connection status
            if hasattr(self, 'web_scrape_worker') and self.web_scrape_worker:
                self.web_scrape_worker.set_connection_status(is_connected)
    
    def setup_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Collection", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_collection)
        file_menu.addAction(new_action)
        
        export_action = QAction("Export Data", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Ctrl+S")
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        clear_action = QAction("Clear Data", self)
        clear_action.triggered.connect(self.clear_data)
        edit_menu.addAction(clear_action)
        
        validate_action = QAction("Validate Data", self)
        validate_action.triggered.connect(self.validate_data)
        edit_menu.addAction(validate_action)
        
        clean_action = QAction("Clean Data", self)
        clean_action.triggered.connect(self.clean_data)
        edit_menu.addAction(clean_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_table)
        view_menu.addAction(refresh_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        proxy_test_action = QAction("Test Proxies", self)
        proxy_test_action.triggered.connect(self.test_proxies)
        tools_menu.addAction(proxy_test_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        new_action = QAction("New Collection", self)
        new_action.triggered.connect(self.new_collection)
        toolbar.addAction(new_action)
        
        start_action = QAction("Start Collection", self)
        start_action.triggered.connect(self.start_collection)
        toolbar.addAction(start_action)
        
        stop_action = QAction("Stop Collection", self)
        stop_action.triggered.connect(self.stop_collection)
        toolbar.addAction(stop_action)
        
        toolbar.addSeparator()
        
        export_action = QAction("Export Data", self)
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
    
    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create a tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.search_tab = self.create_search_tab()
        self.tab_widget.addTab(self.search_tab, "Search Parameters")
        
        self.web_scraping_tab = self.create_web_scraping_tab()
        self.tab_widget.addTab(self.web_scraping_tab, "Web Scraping")
        
        self.results_tab = self.create_results_tab()
        self.tab_widget.addTab(self.results_tab, "Results")
        
        self.logs_tab = self.create_logs_tab()
        self.tab_widget.addTab(self.logs_tab, "Activity Log")
        
        # Initialize collector thread
        self.collector_thread = None
        
        # Initialize web scraper thread
        self.web_scrape_worker = None
    
    def create_search_tab(self):
        # Create search parameters tab
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        search_layout.setContentsMargins(15, 15, 15, 15)
        search_layout.setSpacing(15)
        
        # Create search parameters card
        self.search_card = SearchParametersCard()
        search_layout.addWidget(self.search_card)
        
        # Create network status card
        self.network_card = NetworkStatusCard()
        search_layout.addWidget(self.network_card)
        
        # Action buttons
        self.start_button = QPushButton("Start Collection")
        self.start_button.clicked.connect(self.start_collection)
        search_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Collection")
        self.stop_button.clicked.connect(self.stop_collection)
        self.stop_button.setEnabled(False)
        search_layout.addWidget(self.stop_button)
        
        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_data)
        search_layout.addWidget(self.export_button)
        
        return search_tab
    
    def create_web_scraping_tab(self):
        # Create web scraping tab
        web_scraping_tab = QWidget()
        web_scraping_layout = QVBoxLayout(web_scraping_tab)
        web_scraping_layout.setContentsMargins(15, 15, 15, 15)
        web_scraping_layout.setSpacing(15)
        
        # Create web scraping card
        self.web_scraping_card = WebScrapingCard()
        web_scraping_layout.addWidget(self.web_scraping_card)
        
        # Connect signals
        self.web_scraping_card.start_btn.clicked.connect(self.start_web_scraping)
        self.web_scraping_card.stop_btn.clicked.connect(self.stop_web_scraping)
        self.web_scraping_card.clear_btn.clicked.connect(self.clear_web_results)
        self.web_scraping_card.export_btn.clicked.connect(self.export_web_csv)
        self.web_scraping_card.ecom_toggle.stateChanged.connect(self._toggle_web_platform)
        self.web_scraping_card.browser_toggle.stateChanged.connect(
            lambda s: self.web_scraping_card.headless_toggle.setEnabled(s)
        )
        
        return web_scraping_tab
    
    def create_results_tab(self):
        # Create results tab
        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)
        results_layout.setContentsMargins(15, 15, 15, 15)
        results_layout.setSpacing(15)
        
        # Create results card
        self.results_card = ResultsCard()
        results_layout.addWidget(self.results_card)
        
        # Connect filter signal
        self.results_card.filter_edit.textChanged.connect(self.filter_results)
        
        return results_tab
    
    def create_logs_tab(self):
        # Create logs tab
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        logs_layout.setContentsMargins(15, 15, 15, 15)
        logs_layout.setSpacing(15)
        
        # Create logs card
        self.logs_card = LogsCard()
        logs_layout.addWidget(self.logs_card)
        
        return logs_tab
    
    def browse_chromedriver(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select ChromeDriver", "", "Executable Files (*.exe);;All Files (*)"
        )
        if file_path:
            self.search_card.chromedriver_input.setText(file_path)
    
    def open_settings(self):
        dialog = SettingsDialog(self)
        
        # Set current values
        dialog.set_settings(self.settings)
        
        if dialog.exec_() == QDialog.Accepted:
            # Update settings
            self.settings = dialog.get_settings()
            self.save_settings()
            self.apply_theme(self.settings.get('theme', 'Light'))
            self.log_message("Settings updated successfully")
    
    def log_message(self, message):
        """Add a message to the status log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.logs_card.add_log(timestamp, message)
    
    def new_collection(self):
        if self.collected_data and QMessageBox.question(
            self, "New Collection", 
            "Do you want to clear existing data and start a new collection?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            self.clear_data()
        
        # Focus on search input
        self.search_card.query_edit.setFocus()
    
    def start_collection(self):
        search_query = self.search_card.query_edit.text()
        location = self.search_card.location_edit.text()
        state = self.search_card.state_combo.currentText()
        country = self.search_card.country_combo.currentText()
        num_entries = self.search_card.entries_spin.value()
        chromedriver_path = self.search_card.chromedriver_input.text()
        
        if not search_query or not location:
            QMessageBox.warning(self, "Input Error", "Please enter both search query and location.")
            return
        
        # Validate chromedriver_path if provided
        if chromedriver_path and not os.path.exists(chromedriver_path):
            QMessageBox.warning(self, "ChromeDriver Path Error", 
                               "The specified ChromeDriver path does not exist. Please check the path or leave it empty for automatic management.")
            return
        
        # Setup proxy manager if needed
        if self.settings.get('use_proxy') or self.settings.get('use_tor'):
            if self.settings.get('use_tor'):
                self.log_message("Starting Tor...")
                if not self.proxy_manager.start_tor():
                    QMessageBox.warning(self, "Tor Error", "Failed to start Tor. Please check if Tor is installed.")
                    return
                self.log_message("Tor started successfully")
            
            if self.settings.get('proxy_file'):
                proxy_file = self.settings.get('proxy_file')
                if os.path.exists(proxy_file):
                    self.log_message(f"Loading proxies from {proxy_file}")
                    self.proxy_manager.load_proxies(proxy_file)
                else:
                    self.log_message("Proxy file not found, using default proxies")
                    self.proxy_manager.load_proxies()
            else:
                self.log_message("Loading default proxies")
                self.proxy_manager.load_proxies()
        else:
            self.proxy_manager = None
        
        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_bar.showMessage("Initializing data collection...")
        self.log_message("Starting data collection...")
        
        # Get API key if using API
        api_key = None
        if self.search_card.api_checkbox.isChecked():
            api_key = self.settings.get('api_key')
            if not api_key:
                QMessageBox.warning(self, "API Key Missing", 
                                   "Please enter a Google Places API key in settings to use the API.")
                return
        
        # Start collection thread
        self.collector_thread = DataCollectorThread(
            search_query, location, state, country, num_entries, chromedriver_path, 
            api_key, self.proxy_manager, self.search_card.skip_missing_social_checkbox.isChecked()
        )
        self.collector_thread.progress_updated.connect(self.update_progress)
        self.collector_thread.data_collected.connect(self.add_data_to_table)
        self.collector_thread.status_updated.connect(self.update_status)
        self.collector_thread.finished.connect(self.collection_finished)
        self.collector_thread.error_occurred.connect(self.collection_error)
        self.collector_thread.proxy_rotated.connect(self.proxy_rotated)
        self.collector_thread.entry_skipped.connect(self.entry_skipped)
        self.collector_thread.real_time_update.connect(self.add_real_time_data)
        self.collector_thread.connection_status_changed.connect(self.handle_connection_status_change)
        self.collector_thread.start()
    
    def stop_collection(self):
        if self.collector_thread and self.collector_thread.isRunning():
            self.collector_thread.stop()
            self.status_bar.showMessage("Stopping collection...")
            self.log_message("Stopping collection...")
    
    def update_progress(self, value):
        self.status_bar.showMessage(f"Progress: {value}%")
    
    def update_status(self, message):
        self.status_bar.showMessage(message)
        self.log_message(message)
    
    def proxy_rotated(self, message):
        self.log_message(f"Proxy: {message}")
    
    def entry_skipped(self, message):
        self.log_message(message)
    
    def add_real_time_data(self, data):
        """Add data to table in real-time as it's retrieved"""
        # Clean the data before adding
        cleaned_data = self.clean_data_entry(data)
        
        # Create a unique key based on name and address to avoid duplicates
        name = cleaned_data.get('name', '').strip().lower()
        address = cleaned_data.get('address', '').strip().lower()
        unique_key = (name, address)
        
        # Skip if this is a duplicate entry
        if unique_key in self.unique_entries:
            self.log_message(f"Duplicate entry skipped: {name}")
            return
        
        # Add to unique entries set
        self.unique_entries.add(unique_key)
        
        # Add data to our collection
        self.collected_data.append(cleaned_data)
        
        # Add data to table
        self.results_card.add_data(cleaned_data)
        
        # Update results count
        count = len(self.collected_data)
        self.results_card.update_count(count)
        
        # Auto-switch to results tab if not already there
        if self.tab_widget.currentIndex() != 2:  # Results tab
            self.tab_widget.setCurrentIndex(2)
    
    def clean_data_entry(self, data):
        """Clean a single data entry"""
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
    
    def clean_data(self):
        """Clean all collected data"""
        if not self.collected_data:
            QMessageBox.warning(self, "No Data", "No data to clean.")
            return
        
        self.log_message("Starting data cleaning...")
        cleaned_count = 0
        
        # Create a new list for cleaned data
        cleaned_data = []
        self.unique_entries = set()  # Reset unique entries set
        
        for i, data in enumerate(self.collected_data):
            # Clean the data entry
            cleaned_entry = self.clean_data_entry(data)
            
            # Create a unique key based on name and address
            name = cleaned_entry.get('name', '').strip().lower()
            address = cleaned_entry.get('address', '').strip().lower()
            unique_key = (name, address)
            
            # Skip if this is a duplicate entry
            if unique_key in self.unique_entries:
                self.log_message(f"Duplicate entry removed: {name}")
                continue
            
            # Add to unique entries set and cleaned data
            self.unique_entries.add(unique_key)
            cleaned_data.append(cleaned_entry)
            cleaned_count += 1
            
            if cleaned_count % 5 == 0:
                self.log_message(f"Cleaned {cleaned_count} of {len(self.collected_data)} entries")
        
        # Replace the collected data with cleaned data
        self.collected_data = cleaned_data
        
        # Refresh table with cleaned data
        self.refresh_table()
        
        removed_count = len(self.collected_data) - cleaned_count
        self.log_message(f"Data cleaning completed. Removed {removed_count} duplicate entries.")
        QMessageBox.information(self, "Data Cleaning Complete", 
                               f"Data cleaning completed.\n\nTotal entries: {cleaned_count}\nRemoved duplicates: {removed_count}")
    
    def add_data_to_table(self, data):
        """Add data to table (called when collection is complete)"""
        # This method is now just for backward compatibility
        # The real-time updates are handled by add_real_time_data
        pass
    
    def collection_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        collected_count = len(self.collected_data)
        self.status_bar.showMessage(f"Collection finished. {collected_count} entries collected.")
        self.log_message(f"Collection finished. {collected_count} entries collected.")
        
        # Show skipped count if any
        if self.collector_thread and hasattr(self.collector_thread, 'skipped_count'):
            skipped_count = self.collector_thread.skipped_count
            if skipped_count > 0:
                self.log_message(f"Skipped {skipped_count} entries without website or Instagram.")
                self.status_bar.showMessage(f"Collection finished. {collected_count} entries collected, {skipped_count} skipped.")
        
        self.collector_thread = None
        
        # Stop Tor if running
        if self.proxy_manager:
            self.proxy_manager.stop_tor()
    
    def collection_error(self, error_message):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_bar.showMessage(f"Error: {error_message}")
        self.log_message(f"Error: {error_message}")
        
        # Create a more informative error dialog
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Collection Error")
        error_dialog.setText("An error occurred during data collection.")
        error_dialog.setInformativeText(error_message)
        error_dialog.setDetailedText("Please try the following solutions:\n\n"
                                    "1. Check your internet connection\n"
                                    "2. Try a different search query or location\n"
                                    "3. Reduce the number of entries to collect\n"
                                    "4. Update Chrome and ChromeDriver\n"
                                    "5. Try again later as Google may have temporary restrictions")
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.exec_()
        
        self.collector_thread = None
        
        # Stop Tor if running
        if self.proxy_manager:
            self.proxy_manager.stop_tor()
    
    def clear_data(self):
        self.collected_data = []
        self.unique_entries = set()  # Reset unique entries set
        self.results_card.clear_data()
        self.status_bar.showMessage("Data cleared.")
        self.log_message("Data cleared.")
    
    def refresh_table(self):
        # Clear and repopulate the table
        current_data = self.collected_data.copy()
        self.clear_data()
        
        for data in current_data:
            self.add_real_time_data(data)
        
        self.status_bar.showMessage("Table refreshed.")
        self.log_message("Table refreshed.")
    
    def validate_data(self):
        """Validate all collected data"""
        if not self.collected_data:
            QMessageBox.warning(self, "No Data", "No data to validate.")
            return
        
        self.log_message("Starting data validation...")
        validated_count = 0
        
        for i, data in enumerate(self.collected_data):
            # Validate phone number
            if self.settings.get('validate_phone') and data.get('phone') != 'N/A':
                try:
                    phone_number = data.get('phone')
                    parsed_number = phonenumbers.parse(phone_number, None)
                    if not phonenumbers.is_valid_number(parsed_number):
                        self.collected_data[i]['phone'] = 'N/A (Invalid)'
                except:
                    self.collected_data[i]['phone'] = 'N/A (Invalid)'
            
            # Validate email
            if self.settings.get('validate_email') and data.get('email') != 'N/A':
                email = data.get('email')
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, email):
                    self.collected_data[i]['email'] = 'N/A (Invalid)'
            
            # Validate website
            if self.settings.get('validate_website') and data.get('website') != 'N/A':
                website = data.get('website')
                try:
                    response = requests.head(website, timeout=5)
                    if response.status_code >= 400:
                        self.collected_data[i]['website'] = 'N/A (Invalid)'
                except:
                    self.collected_data[i]['website'] = 'N/A (Invalid)'
            
            validated_count += 1
            if validated_count % 5 == 0:
                self.log_message(f"Validated {validated_count} of {len(self.collected_data)} entries")
        
        # Refresh table with validated data
        self.refresh_table()
        self.log_message("Data validation completed.")
    
    def test_proxies(self):
        """Test all loaded proxies"""
        if not self.proxy_manager or not self.proxy_manager.proxies:
            QMessageBox.warning(self, "No Proxies", "No proxies loaded. Please configure proxy settings first.")
            return
        
        self.log_message("Testing proxies...")
        working_proxies = []
        
        for proxy in self.proxy_manager.proxies:
            self.log_message(f"Testing proxy: {proxy}")
            if self.proxy_manager.test_proxy(proxy):
                working_proxies.append(proxy)
                self.log_message(f"Proxy {proxy} is working")
            else:
                self.log_message(f"Proxy {proxy} failed")
        
        self.log_message(f"Proxy testing completed. {len(working_proxies)} of {len(self.proxy_manager.proxies)} proxies are working.")
        
        if working_proxies:
            # Update proxy list with only working ones
            self.proxy_manager.proxies = working_proxies
            QMessageBox.information(self, "Proxy Test Results", 
                                   f"{len(working_proxies)} of {len(self.proxy_manager.proxies)} proxies are working.")
        else:
            QMessageBox.warning(self, "Proxy Test Results", "No working proxies found.")
    
    def export_data(self):
        if not self.collected_data:
            QMessageBox.warning(self, "No Data", "No data to export.")
            return
        
        # Ask for directory
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Save Data")
        if not directory:
            return
        
        self.current_directory = directory
        
        try:
            # Create a dedicated folder for this export
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            export_folder = os.path.join(directory, f"data_collection_{timestamp}")
            os.makedirs(export_folder, exist_ok=True)
            
            # Prepare data for CSV
            csv_data = []
            for item in self.collected_data:
                csv_item = {
                    'Name': item.get('name', 'N/A'),
                    'Phone': item.get('phone', 'N/A'),
                    'Email': item.get('email', 'N/A'),
                    'Website': item.get('website', 'N/A'),
                    'Instagram': item.get('instagram', 'N/A'),
                    'Country': item.get('country', 'N/A'),
                    'State': item.get('state', 'N/A'),
                    'Location': item.get('location', 'N/A'),
                    'Address': item.get('address', 'N/A'),
                    'Hours': item.get('hours', 'N/A'),
                    'Products/Services': item.get('products_services', 'N/A'),
                    'Image Path': item.get('image_path', 'N/A')
                }
                csv_data.append(csv_item)
            
            # Export to CSV
            csv_path = os.path.join(export_folder, "collected_data.csv")
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_path, index=False)
            
            # Export to JSON
            json_path = os.path.join(export_folder, "collected_data.json")
            with open(json_path, 'w') as f:
                json.dump(self.collected_data, f, indent=2)
            
            # Copy and rename images
            images_copied = 0
            for item in self.collected_data:
                image_path = item.get('image_path')
                if image_path and image_path != 'N/A' and os.path.exists(image_path):
                    # Create a safe filename from the business name
                    safe_name = re.sub(r'[^\w\s-]', '', item.get('name', 'unknown')).strip().replace(' ', '_')
                    new_image_path = os.path.join(export_folder, f"{safe_name}.jpg")
                    
                    # Copy the image
                    shutil.copy2(image_path, new_image_path)
                    images_copied += 1
            
            # Show success message
            QMessageBox.information(
                self, 
                "Export Successful", 
                f"Data exported successfully to {export_folder}\n\n"
                f"CSV file: {len(csv_data)} entries\n"
                f"JSON file: {len(csv_data)} entries\n"
                f"Images copied: {images_copied}"
            )
            
            self.status_bar.showMessage(f"Data exported to {export_folder}")
            self.log_message(f"Data exported to {export_folder}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred during export: {str(e)}")
            self.status_bar.showMessage(f"Export error: {str(e)}")
            self.log_message(f"Export error: {str(e)}")
    
    def show_about(self):
        QMessageBox.about(self, "About", 
                         "<h2>Automated Data Collection Software</h2>"
                         "<p>This application collects data from Google Maps and other web sources.</p>"
                         "<p><b>Version:</b> 1.0</p>"
                         "<p><b>Features:</b></p>"
                         "<ul>"
                         "<li>Real-time data display as entries are retrieved</li>"
                         "<li>Ensures exact number of requested entries are collected</li>"
                         "<li>Internet connection monitoring with data preservation</li>"
                         "<li>Multiple theme options including dark mode</li>"
                         "<li>Google Places API support for reliable data extraction</li>"
                         "<li>Proxy rotation and Tor support for IP masking</li>"
                         "<li>Advanced email extraction from websites</li>"
                         "<li>Image downloading and organization</li>"
                         "<li>CSV and JSON export functionality</li>"
                         "<li>Responsive user interface</li>"
                         "<li>Automatic ChromeDriver management</li>"
                         "<li>Advanced anti-detection measures</li>"
                         "<li>Data validation capabilities</li>"
                         "<li>Optimized parallel processing for faster scraping</li>"
                         "<li>Nigeria-focused with state selection</li>"
                         "<li>Option to skip entries without social media links</li>"
                         "<li>Duplicate data detection and removal</li>"
                         "<li>Data cleaning functionality</li>"
                         "<li>Web scraping capabilities for Google</li>"
                         "</ul>"
                         "<p><b>Developed by:</b> Buks Tech</p>")
    
    # Web scraping methods
    def _toggle_web_platform(self):
        self.web_scraping_card.platform_box.setEnabled(self.web_scraping_card.ecom_toggle.isChecked())
    
    def start_web_scraping(self):
        query = self.web_scraping_card.query_edit.text().strip()
        if not query:
            QMessageBox.warning(self, "Input Error", "Please enter a search query.")
            return
            
        if self.web_scraping_card.browser_toggle.isChecked() and not SELENIUM_AVAILABLE:
            QMessageBox.warning(self, "Browser Mode Unavailable", 
                               "Selenium/webdriver-manager not installed. Please install them or turn off Browser mode.")
            return

        params = {
            "query": query,
            "location": self.web_scraping_card.location_edit.text().strip(),
            "niche": self.web_scraping_card.niche_edit.text().strip(),
            "pages": self.web_scraping_card.pages_spin.value(),
            "delay_min": 0.5,
            "delay_max": 1.5,
            "max_workers": self.settings.get('web_scraping_workers', 5),
            "ecommerce_only": self.web_scraping_card.ecom_toggle.isChecked(),
            "platform": self.web_scraping_card.platform_box.currentText(),
            "use_browser": self.web_scraping_card.browser_toggle.isChecked(),
            "headless": self.web_scraping_card.headless_toggle.isChecked()
        }

        self.web_scrape_worker = WebScrapeWorker(params)
        self.web_scrape_worker.progress.connect(self.on_web_progress)
        self.web_scrape_worker.row_found.connect(self.on_web_row_found)
        self.web_scrape_worker.finished_ok.connect(self.on_web_done)
        self.web_scrape_worker.finished_err.connect(self.on_web_error)
        self.web_scrape_worker.update_progress.connect(self.on_web_progress_update)
        self.web_scrape_worker.network_issue.connect(self.on_web_network_issue)

        self.web_scraping_card.progress_bar.setVisible(True)
        self.web_scraping_card.progress_bar.setValue(0)
        self.log_message("Starting web scraping...")
        self.web_scraping_card.start_btn.setEnabled(False)
        self.web_scraping_card.stop_btn.setEnabled(True)
        
        # Switch to results tab to show progress
        self.tab_widget.setCurrentIndex(2)  # Results tab
        
        self.web_scrape_worker.start()
    
    def stop_web_scraping(self):
        if self.web_scrape_worker and self.web_scrape_worker.isRunning():
            self.web_scrape_worker.stop()
            self.log_message("Stopping web scraping...")
    
    def clear_web_results(self):
        self.web_scraped_data = []
        self.web_unique_entries = set()
        self.web_scraping_card.progress_bar.setVisible(False)
        self.web_scraping_card.progress_label.setText("Ready")
        self.log_message("Web scraping results cleared.")
    
    def export_web_csv(self):
        if not self.web_scraped_data:
            QMessageBox.warning(self, "No Data", "There is no web scraping data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export Web Scraping Data", "web_results.csv", "CSV files (*.csv)")
        if not path:
            return

        try:
            # Prepare data for CSV
            csv_data = []
            for item in self.web_scraped_data:
                csv_item = {
                    'Email': item.email,
                    'Business Name': item.name,
                    'Website': item.website,
                    'Platform': item.platform,
                    'Niche/Category': item.niche,
                    'Instagram': item.instagram,
                    'Other Socials': item.social,
                    'WhatsApp': item.whatsapp,
                    'Location': item.location,
                    'Address': item.address,
                    'Source Page': item.source_page
                }
                csv_data.append(csv_item)
            
            # Export to CSV
            df = pd.DataFrame(csv_data)
            df.to_csv(path, index=False)
            
            QMessageBox.information(
                self, 
                "Export Successful", 
                f"Web scraping data exported successfully to:\n{path}"
            )
            
            self.log_message(f"Web scraping data exported to {path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")
            self.log_message(f"Export error: {str(e)}")
    
    def on_web_progress(self, msg: str):
        self.log_message(f"Web Scraping: {msg}")
    
    def on_web_row_found(self, item):
        # Create a unique key based on name and website to avoid duplicates
        name = item.name.strip().lower() if item.name else ""
        website = item.website.strip().lower() if item.website else ""
        unique_key = (name, website)
        
        # Skip if this is a duplicate entry
        if unique_key in self.web_unique_entries:
            self.log_message(f"Duplicate web entry skipped: {name}")
            return
        
        # Add to unique entries set
        self.web_unique_entries.add(unique_key)
        
        # Add data to our collection
        self.web_scraped_data.append(item)
        
        # Update results count
        count = len(self.web_scraped_data)
        self.results_card.update_count(count)
        
        # Auto-switch to results tab if not already there
        if self.tab_widget.currentIndex() != 2:  # Results tab
            self.tab_widget.setCurrentIndex(2)
    
    def on_web_done(self):
        self.web_scraping_card.progress_bar.setVisible(False)
        self.web_scraping_card.progress_label.setText("Completed")
        self.log_message("Web scraping completed.")
        self.web_scraping_card.start_btn.setEnabled(True)
        self.web_scraping_card.stop_btn.setEnabled(False)
        
        # Show notification
        count = len(self.web_scraped_data)
        self.log_message(f"Web scraping completed. Found {count} records.")
    
    def on_web_error(self, err: str):
        self.web_scraping_card.progress_bar.setVisible(False)
        self.web_scraping_card.progress_label.setText("Error occurred")
        self.web_scraping_card.start_btn.setEnabled(True)
        self.web_scraping_card.stop_btn.setEnabled(False)
        self.log_message(f"Web scraping error: {err}")
        
        QMessageBox.critical(self, "Web Scraping Error", f"An error occurred during web scraping: {err}")
    
    def on_web_progress_update(self, current, total):
        if total > 0:
            percentage = int((current / total) * 100)
            self.web_scraping_card.progress_bar.setValue(percentage)
            self.web_scraping_card.progress_label.setText(f"Processing {current} of {total} sites ({percentage}%)")
    
    def on_web_network_issue(self):
        self.log_message("Network issue detected. Pausing web scraping...")
        self.web_scrape_worker.pause()
        
        # Show notification
        self.tray_icon.showMessage(
            "Network Issue",
            "Network connection lost. Web scraping paused. Will resume when connection is restored.",
            QSystemTrayIcon.MessageIcon.Warning,
            5000
        )
    
    def filter_results(self):
        filter_text = self.results_card.filter_edit.text().lower()
        self.results_card.filter_results(filter_text)