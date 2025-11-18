data_collector/
├── __init__.py
├── main.py                 # Entry point
├── config.py               # Configuration constants
├── models.py               # Data models
├── settings.py             # Application settings
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # Main application window
│   ├── dialogs.py          # Settings and other dialogs
│   └── widgets.py          # Custom UI components
├── core/
│   ├── __init__.py
│   ├── data_collection.py  # Data collection logic
│   ├── web_scraping.py     # Web scraping logic
│   └── data_processor.py   # Data processing
├── utils/
│   ├── __init__.py
│   ├── browser.py          # Browser automation
│   ├── network.py          # Network utilities
│   ├── data_extraction.py  # Data extraction utilities
│   └── file_ops.py         # File operations
└── resources/
    ├── icons/
    └── styles/

// For other developers

pip install PyQt5 selenium beautifulsoup4 requests pandas webdriver-manager phonenumbers


python data_collector/main.py