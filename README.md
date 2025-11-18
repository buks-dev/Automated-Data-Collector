# Automated Data Collector

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-yellow)](https://riverbankcomputing.com/software/pyqt/intro)
[![Selenium](https://img.shields.io/badge/Selenium-4.0%2B-red)](https://www.selenium.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A powerful, user-friendly desktop application built with Python and PyQt5 for automating data collection from the web. Designed for efficiency, it leverages Selenium for browser automation, BeautifulSoup for parsing, and Pandas for data handling—making it ideal for researchers, marketers, or anyone needing to scrape and process structured data at scale.

## 🚀 Features

- **Intuitive GUI**: Clean PyQt5-based interface with main window and customizable dialogs for easy configuration and monitoring.
- **Robust Web Scraping**: Selenium-powered browser automation with support for dynamic content, combined with BeautifulSoup for efficient HTML parsing.
- **Data Processing Pipeline**: Built-in tools for extracting, cleaning, and transforming data using Pandas; includes phone number validation and formatting.
- **Modular Design**: Extensible architecture with separate modules for UI, scraping logic, network utilities, and data models.
- **Resource Management**: Automatic webdriver handling via Webdriver Manager; no manual driver downloads required.
- **Export Capabilities**: Seamlessly save processed data to CSV, Excel, or JSON formats.
- **Error Handling & Logging**: Comprehensive logging and user-friendly error dialogs for smooth operation.

## 📋 Prerequisites

- Python 3.8 or higher
- A modern web browser (Chrome recommended for Selenium)

## 🛠 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/buks-dev/Automated-Data-Collector.git
   cd Automated-Data-Collector
   ```

2. Install the required dependencies:
   ```bash
   pip install PyQt5 selenium beautifulsoup4 requests pandas webdriver-manager phonenumbers
   ```

3. (Optional) Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

## 🚀 Quick Start

Run the application:
```bash
python data_collector/main.py
```

This launches the main window where you can:
- Configure scraping targets via the settings dialog.
- Start data collection sessions.
- Monitor progress and view extracted data in real-time.
- Export results.

For detailed usage, refer to the [User Guide](docs/USER_GUIDE.md) (coming soon).

## 🏗 Project Structure

```
data_collector/
├── __init__.py
├── main.py                          # Entry point
├── config.py                        # Configuration constants
├── models/                          # Data models
│   └── __init__.py
├── ui/                              # Application settings
│   ├── __init__.py
│   ├── main_window.py               # Main application window
│   └── dialogs.py                   # Settings and other dialogs
├── web_scraping/                    # Web scraping logic
│   ├── __init__.py
│   ├── components/
│   │   └── core/
│   │       ├── __init__.py
│   │       └── utils/               # Data collection logic
│   │           ├── __init__.py
│   │           └── browser.py       # Browser operations
│   └── network/                     # Network utilities
│       ├── data.py                  # Data extraction
│       └── process.py               # Data processing
└── resources/
    ├── icons/
    └── styles/
```

## 🔧 Customization & Extension

- **Add New Scrapers**: Extend the `web_scraping/components/core/utils` module to define custom extraction logic.
- **UI Tweaks**: Modify styles in `resources/styles/` or add widgets in `ui/dialogs.py`.
- **Data Models**: Update `models/` for new data schemas.

## 🤝 Contributing

Contributions are welcome! Please fork the repo and submit a pull request. For major changes, please open an issue first.

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details (coming soon).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with love using open-source tools like PyQt5, Selenium, and Pandas.
- Thanks to the community for inspiration and bug reports!

---

**⭐ Star this repo if it helps you!**  
**🐛 Found a bug? [Open an issue](https://github.com/buks-dev/Automated-Data-Collector/issues).**  
**💡 Feature request? Let us know!**
