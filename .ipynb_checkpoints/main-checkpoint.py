# ui/main_window.py
"""Main application window."""

import os
import sys
import json
import datetime
import shutil
import atexit
from typing import List, Dict, Any

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QComboBox, QFileDialog, QProgressBar, QMessageBox, QGroupBox, 
                            QFormLayout, QSpinBox, QStatusBar, QToolBar, QAction, QHeaderView,
                            QAbstractItemView, QTabWidget, QScrollArea, QSplitter, QCheckBox,
                            QTextEdit, QDialog, QDialogButtonBox, QRadioButton, QButtonGroup,
                            QFrame, QGridLayout, QDoubleSpinBox, QPlainTextEdit, QSpacerItem,
                            QSizePolicy, QSystemTrayIcon, QMenu, QStyle, QStackedWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter, QColor

from models import BusinessData, ScrapedItem
from settings import SettingsManager
from config import THEMES
from utils.network import InternetConnectionChecker, ProxyManager
from utils.file_ops import FileManager
from core.data_collection import DataCollectorThread
from core.web_scraping import WebScrapeWorker
from core.data_processor import DataProcessor
from ui.dialogs import SettingsDialog
from ui.widgets import (SearchParametersCard, NetworkStatusCard, WebScrapingCard, 
                        ResultsTableWidget)
'''
 & C:/Users/BUKS/anaconda3/python.exe "c:/Users/BUKS/Desktop/Python Data Collector/main.py"
'''