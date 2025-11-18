# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.main_window import DataCollectionApp

def main():
    app = QApplication(sys.argv)
    
    # Set application icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = DataCollectionApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()