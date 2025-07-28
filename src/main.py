"""
Main entry point for NextCare2 application
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor

# Add src directory to path
src_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, src_dir)

from database.connection import db_manager
from ui.login_window import LoginWindow
from ui.config_window import ConfigurationWindow
from ui.dashboard_window import DashboardWindow
from ui.styles import get_application_style
from utils.auth import auth_manager
from utils.constants import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nextcare2.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class NextCareApplication:
    """Main NextCare2 application class"""
    
    def __init__(self):
        self.app = None
        self.login_window = None
        self.config_window = None
        self.dashboard_window = None
        
    def create_splash_screen(self):
        """Create and show splash screen"""
        # Create a simple splash screen
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor(PRIMARY_COLOR))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw logo/title
        painter.setPen(QColor("white"))
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "NextCare2")
        
        # Draw subtitle
        subtitle_font = QFont("Arial", 12)
        painter.setFont(subtitle_font)
        subtitle_rect = pixmap.rect()
        subtitle_rect.moveTop(subtitle_rect.top() + 60)
        painter.drawText(subtitle_rect, Qt.AlignmentFlag.AlignCenter, 
                        "Predictive Maintenance System\nLoading...")
        
        painter.end()
        
        splash = QSplashScreen(pixmap)
        splash.show()
        
        # Process events to show splash
        self.app.processEvents()
        
        return splash
    
    def initialize_database(self):
        """Initialize database connection and schema"""
        try:
            logger.info("Initializing database connection...")
            
            # Test connection
            connection_result = db_manager.test_connection()
            
            if not connection_result['connected']:
                # Try to create database if it doesn't exist
                logger.info("Creating database if not exists...")
                if not db_manager.create_database_if_not_exists():
                    raise Exception("Failed to create database")
                
                # Try connection again
                connection_result = db_manager.test_connection()
                
                if not connection_result['connected']:
                    raise Exception(f"Database connection failed: {connection_result['error']}")
            
            # Initialize schema
            logger.info("Initializing database schema...")
            if not db_manager.initialize_schema():
                raise Exception("Failed to initialize database schema")
            
            logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            QMessageBox.critical(
                None, "Database Error",
                f"Failed to initialize database:\n\n{str(e)}\n\n"
                "Please check your PostgreSQL installation and configuration."
            )
            return False
    
    def show_login(self):
        """Show login window"""
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.on_login_successful)
        
        if self.login_window.exec() == LoginWindow.DialogCode.Accepted:
            return True
        else:
            return False
    
    def on_login_successful(self, user_info):
        """Handle successful login"""
        logger.info(f"User {user_info['username']} logged in successfully")
        
        # Show appropriate window based on user role
        role = user_info['role']
        
        if role in ['admin', 'manager']:
            # Admins and managers can choose to go to configuration or dashboard
            self.show_configuration()
        else:
            # Engineers go directly to dashboard
            self.show_dashboard()
    
    def show_configuration(self):
        """Show configuration window"""
        self.config_window = ConfigurationWindow()
        self.config_window.skip_to_dashboard.connect(self.show_dashboard)
        self.config_window.show()
    
    def show_dashboard(self):
        """Show dashboard window"""
        # Close config window if open
        if self.config_window:
            self.config_window.close()
            self.config_window = None
        
        self.dashboard_window = DashboardWindow()
        self.dashboard_window.show()
    
    def run(self):
        """Run the application"""
        # Create QApplication
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(APP_VERSION)
        
        # Apply global stylesheet
        self.app.setStyleSheet(get_application_style())
        
        try:
            # Show splash screen
            splash = self.create_splash_screen()
            
            # Initialize database
            splash.showMessage("Initializing database...", Qt.AlignmentFlag.AlignBottom, QColor("white"))
            self.app.processEvents()
            
            if not self.initialize_database():
                splash.close()
                return 1
            
            # Show login
            splash.showMessage("Loading login...", Qt.AlignmentFlag.AlignBottom, QColor("white"))
            self.app.processEvents()
            
            # Close splash screen
            splash.close()
            
            # Show login window
            if not self.show_login():
                logger.info("Application closed by user")
                return 0
            
            # Run event loop
            return self.app.exec()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            QMessageBox.critical(
                None, "Application Error",
                f"An unexpected error occurred:\n\n{str(e)}"
            )
            return 1
        
        finally:
            # Cleanup
            if db_manager:
                db_manager.disconnect()

def main():
    """Main entry point"""
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    
    try:
        app = NextCareApplication()
        exit_code = app.run()
        
        logger.info(f"Application exited with code {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())