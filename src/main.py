"""
Main application entry point
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication

from ui.app_manager import app_manager
from ui.styles import get_application_style

def main():
    """Main application function"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setStyleSheet(get_application_style())
    
    # Start the application
    app_manager.start_application()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()