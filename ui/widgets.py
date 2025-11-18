# ui/widgets.py
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox, QProgressBar, 
    QGroupBox, QFormLayout, QCheckBox, QTextEdit, QFrame, QGridLayout,
    QDoubleSpinBox, QPlainTextEdit, QSpacerItem, QSizePolicy, QSystemTrayIcon,
    QMenu, QStyle, QStackedWidget, QRadioButton, QButtonGroup
)
from core.utils import NIGERIAN_STATES

class SearchParametersCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Form section
        form_group = QFrame()
        form_group.setObjectName("FormGroup")
        form_layout = QGridLayout(form_group)
        form_layout.setVerticalSpacing(12)
        form_layout.setHorizontalSpacing(10)
        
        row = 0
        # Query input
        query_label = QLabel("Search Query")
        query_label.setObjectName("FieldLabel")
        self.query_edit = QLineEdit()
        self.query_edit.setPlaceholderText("e.g., restaurants, hotels, stores")
        form_layout.addWidget(query_label, row, 0)
        form_layout.addWidget(self.query_edit, row, 1)
        row += 1
        
        # Location input
        location_label = QLabel("Location")
        location_label.setObjectName("FieldLabel")
        self.location_edit = QLineEdit()
        self.location_edit.setText("Nigeria")
        self.location_edit.setPlaceholderText("e.g., Nigeria, Lagos, Abuja")
        form_layout.addWidget(location_label, row, 0)
        form_layout.addWidget(self.location_edit, row, 1)
        row += 1
        
        # State dropdown with Nigerian states
        state_label = QLabel("State")
        state_label.setObjectName("FieldLabel")
        self.state_combo = QComboBox()
        self.state_combo.setEditable(True)  # Allow manual input
        self.state_combo.addItems(["N/A"] + NIGERIAN_STATES)
        self.state_combo.setCurrentText("N/A")
        form_layout.addWidget(state_label, row, 0)
        form_layout.addWidget(self.state_combo, row, 1)
        row += 1
        
        # Country dropdown
        country_label = QLabel("Country")
        country_label.setObjectName("FieldLabel")
        self.country_combo = QComboBox()
        self.country_combo.addItems([
            "Nigeria", "United States", "Canada", "United Kingdom", "Australia", 
            "Germany", "France", "Spain", "Italy", "Japan", "China", 
            "India", "Brazil", "Mexico", "Other"
        ])
        self.country_combo.setCurrentText("Nigeria")
        form_layout.addWidget(country_label, row, 0)
        form_layout.addWidget(self.country_combo, row, 1)
        row += 1
        
        # Number of entries
        entries_label = QLabel("Number of Entries")
        entries_label.setObjectName("FieldLabel")
        self.entries_spin = QSpinBox()
        self.entries_spin.setMinimum(1)
        self.entries_spin.setMaximum(100)
        self.entries_spin.setValue(10)
        form_layout.addWidget(entries_label, row, 0)
        form_layout.addWidget(self.entries_spin, row, 1)
        row += 1
        
        # ChromeDriver path
        chromedriver_label = QLabel("ChromeDriver Path")
        chromedriver_label.setObjectName("FieldLabel")
        self.chromedriver_input = QLineEdit()
        self.chromedriver_input.setPlaceholderText("Path to ChromeDriver (leave empty for auto)")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_chromedriver)
        
        chromedriver_layout = QHBoxLayout()
        chromedriver_layout.addWidget(self.chromedriver_input)
        chromedriver_layout.addWidget(self.browse_button)
        form_layout.addWidget(chromedriver_label, row, 0)
        form_layout.addLayout(chromedriver_layout, row, 1)
        row += 1
        
        # Advanced options
        advanced_group = QFrame()
        advanced_group.setObjectName("FormGroup")
        advanced_layout = QVBoxLayout(advanced_group)
        advanced_layout.setSpacing(15)
        
        # API checkbox
        self.api_checkbox = QCheckBox("Use Google Places API (requires API key)")
        self.api_checkbox.setChecked(False)
        advanced_layout.addWidget(self.api_checkbox)
        
        # Skip missing social checkbox
        self.skip_missing_social_checkbox = QCheckBox("Skip entries without website or Instagram")
        self.skip_missing_social_checkbox.setChecked(True)
        advanced_layout.addWidget(self.skip_missing_social_checkbox)
        
        form_layout.addWidget(QLabel("Advanced Options"), row, 0)
        form_layout.addWidget(advanced_group, row, 1)
        
        # Add form to layout
        layout.addWidget(QLabel("Search Parameters"))
        layout.addWidget(form_group)
    
    def browse_chromedriver(self):
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select ChromeDriver", "", "Executable Files (*.exe);;All Files (*)"
        )
        if file_path:
            self.chromedriver_input.setText(file_path)

class NetworkStatusCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Network status indicator
        network_group = QFrame()
        network_group.setObjectName("FormGroup")
        network_layout = QVBoxLayout(network_group)
        
        network_title = QLabel("Network Status")
        network_title.setObjectName("GroupTitle")
        network_layout.addWidget(network_title)
        
        network_status_layout = QHBoxLayout()
        self.connection_label = QLabel("Connected")
        self.connection_label.setStyleSheet("color: green;")
        network_status_layout.addWidget(QLabel("Internet Status:"))
        network_status_layout.addWidget(self.connection_label)
        network_status_layout.addStretch()
        network_layout.addLayout(network_status_layout)
        
        layout.addWidget(network_group)
        layout.addStretch()

class WebScrapingCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Form section
        form_group = QFrame()
        form_group.setObjectName("FormGroup")
        form_layout = QGridLayout(form_group)
        form_layout.setVerticalSpacing(12)
        form_layout.setHorizontalSpacing(10)
        
        row = 0
        # Query input
        query_label = QLabel("Search Query")
        query_label.setObjectName("FieldLabel")
        self.query_edit = QLineEdit()
        self.query_edit.setPlaceholderText("e.g., fashion boutique, organic skincare...")
        form_layout.addWidget(query_label, row, 0)
        form_layout.addWidget(self.query_edit, row, 1)
        row += 1
        
        # Location input
        location_label = QLabel("Location")
        location_label.setObjectName("FieldLabel")
        self.location_edit = QLineEdit()
        self.location_edit.setText("Nigeria")
        self.location_edit.setPlaceholderText("e.g., Lagos, Nigeria")
        form_layout.addWidget(location_label, row, 0)
        form_layout.addWidget(self.location_edit, row, 1)
        row += 1
        
        # Niche input
        niche_label = QLabel("Niche / Store Type")
        niche_label.setObjectName("FieldLabel")
        self.niche_edit = QLineEdit()
        self.niche_edit.setPlaceholderText("e.g., clothing, beauty, gadgets")
        form_layout.addWidget(niche_label, row, 0)
        form_layout.addWidget(self.niche_edit, row, 1)
        row += 1
        
        # Pages to scan
        pages_label = QLabel("Pages to scan")
        pages_label.setObjectName("FieldLabel")
        self.pages_spin = QSpinBox()
        self.pages_spin.setRange(1, 20)
        self.pages_spin.setValue(3)
        form_layout.addWidget(pages_label, row, 0)
        form_layout.addWidget(self.pages_spin, row, 1)
        row += 1
        
        # Add form to layout
        layout.addWidget(QLabel("Web Scraping Parameters"))
        layout.addWidget(form_group)
        
        # Options section
        options_group = QFrame()
        options_group.setObjectName("FormGroup")
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(15)
        
        options_title = QLabel("Scraping Options")
        options_title.setObjectName("GroupTitle")
        options_layout.addWidget(options_title)
        
        # E-commerce mode
        self.ecom_toggle = QCheckBox("E-commerce mode (filter by platform)")
        self.ecom_toggle.setChecked(True)
        options_layout.addWidget(self.ecom_toggle)
        
        # Platform selection
        platform_container = QWidget()
        platform_layout = QHBoxLayout(platform_container)
        platform_layout.setContentsMargins(20, 0, 0, 0)
        platform_layout.addWidget(QLabel("Platform:"))
        self.platform_box = QComboBox()
        self.platform_box.addItems(["Any", "Shopify", "WooCommerce", "Wix", "BigCommerce", "Squarespace", "Magento", "Etsy", "Amazon"])
        platform_layout.addWidget(self.platform_box)
        platform_layout.addStretch()
        options_layout.addWidget(platform_container)
        
        # Browser mode
        self.browser_toggle = QCheckBox("Browser mode (Selenium) - slower but more reliable")
        self.browser_toggle.setChecked(False)
        options_layout.addWidget(self.browser_toggle)
        
        # Headless option
        headless_container = QWidget()
        headless_layout = QHBoxLayout(headless_container)
        headless_layout.setContentsMargins(20, 0, 0, 0)
        self.headless_toggle = QCheckBox("Headless browser")
        self.headless_toggle.setChecked(True)
        headless_layout.addWidget(self.headless_toggle)
        headless_layout.addStretch()
        options_layout.addWidget(headless_container)
        
        layout.addWidget(options_group)
        
        # Buttons section
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(15)
        
        self.start_btn = QPushButton("Start Scraping")
        self.start_btn.setObjectName("PrimaryButton")
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.clear_btn = QPushButton("Clear Results")
        self.export_btn = QPushButton("Export CSV")
        
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addWidget(self.export_btn)
        
        layout.addWidget(buttons_container)
        
        # Progress section
        progress_group = QFrame()
        progress_group.setObjectName("FormGroup")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(15)
        
        progress_title = QLabel("Scraping Progress")
        progress_title.setObjectName("GroupTitle")
        progress_layout.addWidget(progress_title)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel("Ready")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_group)
        layout.addStretch()

class ResultsCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Results header with count
        results_header = QWidget()
        results_header_layout = QHBoxLayout(results_header)
        results_header_layout.setContentsMargins(0, 0, 0, 0)
        
        results_title = QLabel("Scraping Results")
        results_title.setObjectName("CardTitle")
        self.results_count = QLabel("0 records found")
        self.results_count.setObjectName("ResultsCount")
        
        results_header_layout.addWidget(results_title)
        results_header_layout.addStretch()
        results_header_layout.addWidget(self.results_count)
        
        # Table with filtering options
        table_controls = QFrame()
        table_controls.setObjectName("TableControls")
        table_controls_layout = QHBoxLayout(table_controls)
        table_controls_layout.setContentsMargins(10, 10, 10, 10)
        
        table_controls_layout.addWidget(QLabel("Filter:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter results...")
        table_controls_layout.addWidget(self.filter_edit)
        
        # Add export button to table controls
        export_table_btn = QPushButton("Export CSV")
        export_table_btn.setObjectName("SecondaryButton")
        table_controls_layout.addWidget(export_table_btn)
        
        # Create table
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(11)  # Added state column
        self.data_table.setHorizontalHeaderLabels([
            "Name", "Phone", "Email", "Website", "Instagram", 
            "Country", "State", "Location", "Hours", "Products/Services", "Image"
        ])
        
        # Make table fill the available space
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSortingEnabled(True)
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # Add components to layout
        layout.addWidget(results_header)
        layout.addWidget(table_controls)
        layout.addWidget(self.data_table, 1)  # Give table stretch factor of 1
        
        # Connect signals
        export_table_btn.clicked.connect(self.export_data)
    
    def add_data(self, data):
        """Add data to table"""
        row_position = self.data_table.rowCount()
        self.data_table.insertRow(row_position)
        
        self.data_table.setItem(row_position, 0, QTableWidgetItem(data.get('name', 'N/A')))
        self.data_table.setItem(row_position, 1, QTableWidgetItem(data.get('phone', 'N/A')))
        self.data_table.setItem(row_position, 2, QTableWidgetItem(data.get('email', 'N/A')))
        self.data_table.setItem(row_position, 3, QTableWidgetItem(data.get('website', 'N/A')))
        self.data_table.setItem(row_position, 4, QTableWidgetItem(data.get('instagram', 'N/A')))
        self.data_table.setItem(row_position, 5, QTableWidgetItem(data.get('country', 'N/A')))
        self.data_table.setItem(row_position, 6, QTableWidgetItem(data.get('state', 'N/A')))
        self.data_table.setItem(row_position, 7, QTableWidgetItem(data.get('location', 'N/A')))
        
        # Format hours for display
        hours = data.get('hours', 'N/A')
        if hours != 'N/A':
            try:
                import json
                hours_dict = json.loads(hours)
                hours_text = "\n".join([f"{day}: {time}" for day, time in hours_dict.items()])
                self.data_table.setItem(row_position, 8, QTableWidgetItem(hours_text))
            except:
                self.data_table.setItem(row_position, 8, QTableWidgetItem(hours))
        else:
            self.data_table.setItem(row_position, 8, QTableWidgetItem('N/A'))
        
        # Format products/services for display
        products_services = data.get('products_services', 'N/A')
        if products_services != 'N/A':
            try:
                import json
                services_list = json.loads(products_services)
                services_text = "\n".join(services_list[:5])  # Show first 5 items
                if len(services_list) > 5:
                    services_text += f"\n... and {len(services_list) - 5} more"
                self.data_table.setItem(row_position, 9, QTableWidgetItem(services_text))
            except:
                self.data_table.setItem(row_position, 9, QTableWidgetItem(products_services))
        else:
            self.data_table.setItem(row_position, 9, QTableWidgetItem('N/A'))
        
        # For image, just show the path or a thumbnail
        image_path = data.get('image_path', 'N/A')
        if image_path != 'N/A':
            try:
                from PyQt5.QtGui import QPixmap
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label = QLabel()
                    image_label.setPixmap(pixmap)
                    image_label.setAlignment(Qt.AlignCenter)
                    self.data_table.setCellWidget(row_position, 10, image_label)
                else:
                    self.data_table.setItem(row_position, 10, QTableWidgetItem("Image"))
            except:
                self.data_table.setItem(row_position, 10, QTableWidgetItem("Image"))
        else:
            self.data_table.setItem(row_position, 10, QTableWidgetItem("N/A"))
        
        # Resize rows to content
        self.data_table.resizeRowsToContents()
        
        # Scroll to the new row
        self.data_table.scrollToBottom()
    
    def clear_data(self):
        """Clear all data from table"""
        self.data_table.setRowCount(0)
        self.update_count(0)
    
    def update_count(self, count):
        """Update the results count label"""
        self.results_count.setText(f"{count} record{'s' if count != 1 else ''} found")
    
    def export_data(self):
        """Export data to CSV"""
        # This will be connected to the main window's export method
        pass
    
    def filter_results(self, filter_text):
        """Filter results based on filter text"""
        for row in range(self.data_table.rowCount()):
            match = False
            for col in range(self.data_table.columnCount()):
                index = self.data_table.model().index(row, col)
                item_text = self.data_table.model().data(index)
                if item_text and filter_text in str(item_text).lower():
                    match = True
                    break
            self.data_table.setRowHidden(row, not match)

class LogsCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Logs header
        logs_header = QWidget()
        logs_header_layout = QHBoxLayout(logs_header)
        logs_header_layout.setContentsMargins(0, 0, 0, 0)
        
        logs_title = QLabel("Activity Log")
        logs_title.setObjectName("CardTitle")
        
        logs_header_layout.addWidget(logs_title)
        logs_header_layout.addStretch()
        
        # Create log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        
        # Add components to layout
        layout.addWidget(logs_header)
        layout.addWidget(self.log_text, 1)  # Give log text area stretch factor of 1
    
    def add_log(self, timestamp, message):
        """Add a log entry"""
        self.log_text.append(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class SettingsDialog(QDialog):
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
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Proxy List File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.proxy_file_input.setText(file_path)
    
    def get_settings(self):
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
        if theme == "Dark":
            self.dark_theme_radio.setChecked(True)
        elif theme == "Blue":
            self.blue_theme_radio.setChecked(True)
        elif theme == "Green":
            self.green_theme_radio.setChecked(True)
        else:
            self.light_theme_radio.setChecked(True)
    
    def set_settings(self, settings):
        """Set current settings values"""
        self.api_key_input.setText(settings.get('api_key', ''))
        self.use_proxy_checkbox.setChecked(settings.get('use_proxy', False))
        self.proxy_file_input.setText(settings.get('proxy_file', ''))
        self.use_tor_checkbox.setChecked(settings.get('use_tor', False))
        self.set_theme(settings.get('theme', 'Light'))
        self.thread_count.setValue(settings.get('thread_count', 4))
        self.batch_size.setValue(settings.get('batch_size', 4))
        self.skip_missing_social_checkbox.setChecked(settings.get('skip_missing_social', True))
        self.requests_per_minute.setValue(settings.get('requests_per_minute', 20))
        self.random_delay_min.setValue(settings.get('random_delay_min', 1))
        self.random_delay_max.setValue(settings.get('random_delay_max', 2))
        self.validate_phone_checkbox.setChecked(settings.get('validate_phone', True))
        self.validate_email_checkbox.setChecked(settings.get('validate_email', True))
        self.validate_website_checkbox.setChecked(settings.get('validate_website', True))
        self.enable_web_scraping_checkbox.setChecked(settings.get('enable_web_scraping', True))
        self.web_scraping_workers.setValue(settings.get('web_scraping_workers', 5))
    
    def apply_settings(self):
        """Apply settings without closing the dialog"""
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
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Settings Applied", "Settings have been applied successfully.")