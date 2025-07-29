"""
Application manager for smooth window transitions
"""

import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

# Use absolute imports instead of relative imports
from ui.login_window import LoginWindow
from ui.config_window import ConfigurationWindow
from ui.dashboard_window import DashboardWindow
from utils.auth import auth_manager

logger = logging.getLogger(__name__)

class AppManager(QObject):
    """Manages application window transitions"""
    
    def __init__(self):
        super().__init__()
        self.login_window = None
        self.config_window = None
        self.dashboard_window = None
        
    def start_application(self):
        """Start the application with login window"""
        self.show_login()
    
    def show_login(self):
        """Show login window"""
        # Clean up existing windows
        if self.config_window:
            self.config_window.hide()
        if self.dashboard_window:
            self.dashboard_window.hide()
        
        # Create or reuse login window
        if not self.login_window:
            self.login_window = LoginWindow()
            self.login_window.login_successful.connect(self.on_login_successful)
        else:
            # Clear form
            self.login_window.username_input.clear()
            self.login_window.password_input.clear()
            self.login_window.status_label.hide()
        
        self.login_window.show()
        self.login_window.raise_()
        self.login_window.activateWindow()
    
    def on_login_successful(self, user_data):
        """Handle successful login"""
        self.login_window.hide()
        self.show_configuration()
    
    def show_configuration(self):
        """Show configuration window"""
        if not self.config_window:
            self.config_window = ConfigurationWindow()
            self.config_window.skip_to_dashboard.connect(self.show_dashboard)
            # Replace the logout method
            self.config_window.logout = self.show_login
        
        self.config_window.show()
        self.config_window.raise_()
        self.config_window.activateWindow()
    
    def show_dashboard(self):
        """Show dashboard window"""
        if self.config_window:
            self.config_window.hide()
        
        if not self.dashboard_window:
            self.dashboard_window = DashboardWindow()
            # Connect logout to return to login
            self.dashboard_window.logout = self.logout_and_return_to_login
        
        self.dashboard_window.show()
        self.dashboard_window.raise_()
        self.dashboard_window.activateWindow()
    
    def logout_and_return_to_login(self):
        """Logout and return to login"""
        # Stop any ongoing processes in dashboard
        if self.dashboard_window:
            if hasattr(self.dashboard_window, 'refresh_timer'):
                self.dashboard_window.refresh_timer.stop()
            if hasattr(self.dashboard_window, 'sensor_client'):
                try:
                    from communication.sensor_client import sensor_client
                    sensor_client.stop_polling()
                    sensor_client.disconnect_from_sensor()
                except ImportError:
                    pass  # Ignore if sensor client doesn't exist
        
        # Logout user
        auth_manager.logout()
        
        # Show login window
        self.show_login()

# Global app manager instance
app_manager = AppManager()