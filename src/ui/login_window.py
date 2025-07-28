"""
Login window for NextCare2 application
"""

import sys
import logging
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QFrame,
                            QApplication, QMessageBox, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPalette

# Use try/except to handle both relative and absolute imports
try:
    from ..utils.auth import auth_manager
    from ..utils.constants import *
    from .styles import get_login_style, get_application_style
except ImportError:
    # Fallback to absolute imports when running directly
    from utils.auth import auth_manager
    from utils.constants import *
    from ui.styles import get_login_style, get_application_style

logger = logging.getLogger(__name__)

class LoginWindow(QDialog):
    """Professional login window with role-based authentication"""
    
    login_successful = pyqtSignal(dict)  # Emits user info on successful login
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_TITLE} - Login")
        self.setFixedSize(LOGIN_WINDOW_WIDTH, LOGIN_WINDOW_HEIGHT)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        
        # Apply styling - use both application-wide and login-specific styles
        self.setStyleSheet(get_application_style() + get_login_style())
        
        self.setup_ui()
        self.center_window()
        
    def setup_ui(self):
        """Setup the login UI components"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Main container
        container = QFrame()
        container.setObjectName("login-container")
        container.setStyleSheet(f"""
            QFrame#login-container {{
                background-color: {CARD_COLOR};
                border-radius: 12px;
                padding: 32px;
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)
        
        # Header
        self.create_header(layout)
        
        # Login form
        self.create_login_form(layout)
        
        # Buttons
        self.create_buttons(layout)
        
        # Error/Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {ERROR_COLOR}; font-size: 12px; font-weight: 600;")
        self.status_label.hide()
        layout.addWidget(self.status_label)
        
        main_layout.addWidget(container)
        self.setLayout(main_layout)
    
    def create_header(self, layout):
        """Create the header section"""
        # Logo/Title
        title_label = QLabel("NextCare")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {PRIMARY_COLOR};
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Predictive Maintenance System")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            font-size: 14px;
            color: {SECONDARY_COLOR};
            margin-bottom: 24px;
        """)
        layout.addWidget(subtitle_label)
    
    def create_login_form(self, layout):
        """Create the login form"""
        # Username field
        username_label = QLabel("Username:")
        username_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: 600; margin-bottom: 4px;")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #E1E8ED;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                min-height: 20px;
                margin-bottom: 16px;
            }}
            QLineEdit:focus {{
                border-color: {ACCENT_COLOR};
            }}
        """)
        layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password:")
        password_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: 600; margin-bottom: 4px;")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #E1E8ED;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                min-height: 20px;
                margin-bottom: 16px;
            }}
            QLineEdit:focus {{
                border-color: {ACCENT_COLOR};
            }}
        """)
        layout.addWidget(self.password_input)
        
        # Connect Enter key to login
        self.username_input.returnPressed.connect(self.attempt_login)
        self.password_input.returnPressed.connect(self.attempt_login)
    
    def create_buttons(self, layout):
        """Create the button section"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_COLOR};
                border: 2px solid #E1E8ED;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                min-height: 16px;
            }}
            QPushButton:hover {{
                border-color: {SECONDARY_COLOR};
                color: {SECONDARY_COLOR};
            }}
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # Login button
        self.login_button = QPushButton("Sign In")
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                min-height: 16px;
            }}
            QPushButton:hover {{
                background-color: {SECONDARY_COLOR};
            }}
            QPushButton:pressed {{
                background-color: #1a2330;
            }}
        """)
        self.login_button.clicked.connect(self.attempt_login)
        self.login_button.setDefault(True)
        button_layout.addWidget(self.login_button)
        
        layout.addLayout(button_layout)
    
    def center_window(self):
        """Center the window on the screen"""
        screen_geometry = QApplication.primaryScreen().geometry()
        window_geometry = self.geometry()
        
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        
        self.move(x, y)
    
    def attempt_login(self):
        """Attempt to authenticate user"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate input
        if not username:
            self.show_error("Please enter your username")
            self.username_input.setFocus()
            return
        
        if not password:
            self.show_error("Please enter your password")
            self.password_input.setFocus()
            return
        
        # Clear previous error
        self.status_label.hide()
        
        # Disable login button during authentication
        self.login_button.setEnabled(False)
        self.login_button.setText("Signing In...")
        
        # Attempt authentication
        try:
            if auth_manager.login(username, password):
                user = auth_manager.get_current_user()
                self.show_success(f"Welcome, {user['full_name']}!")
                
                # Emit successful login signal
                self.login_successful.emit(user)
                
                # Close dialog after brief delay
                self.accept()
            else:
                self.show_error("Invalid username or password")
                self.password_input.clear()
                self.password_input.setFocus()
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            self.show_error("Login failed. Please check your connection and try again.")
        
        finally:
            # Re-enable login button
            self.login_button.setEnabled(True)
            self.login_button.setText("Sign In")
    
    def show_error(self, message: str):
        """Show error message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {ERROR_COLOR}; font-size: 12px; font-weight: 600;")
        self.status_label.show()
    
    def show_success(self, message: str):
        """Show success message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {SUCCESS_COLOR}; font-size: 12px; font-weight: 600;")
        self.status_label.show()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

def show_login_dialog(parent=None):
    """Show login dialog and return user info if successful"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Apply application-wide styling
    app.setStyleSheet(get_application_style())
    
    dialog = LoginWindow()
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return auth_manager.get_current_user()
    
    return None

if __name__ == "__main__":
    # Test the login window
    import sys
    from PyQt6.QtWidgets import QApplication
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    app.setStyleSheet(get_application_style())
    
    # Show login dialog
    user = show_login_dialog()
    if user:
        print(f"Login successful: {user}")
    else:
        print("Login cancelled or failed")
    
    sys.exit()