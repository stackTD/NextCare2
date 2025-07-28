"""
Application constants and configuration
"""

# Application Information
APP_NAME = "NextCare2"
APP_VERSION = "1.0.0"
APP_TITLE = "NextCare Predictive Maintenance"

# User Roles
ROLE_ADMIN = "admin"
ROLE_MANAGER = "manager"
ROLE_ENGINEER = "engineer"

ROLES = [ROLE_ADMIN, ROLE_MANAGER, ROLE_ENGINEER]

# Database Configuration
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = 5432
DEFAULT_DB_NAME = "nextcare2"
DEFAULT_DB_USER = "nextcare_user"

# Communication Settings
SENSOR_HOST = "localhost"
SENSOR_PORT = 8888
DATA_POLLING_INTERVAL = 1000  # milliseconds

# UI Configuration
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
LOGIN_WINDOW_WIDTH = 450
LOGIN_WINDOW_HEIGHT = 500

# Colors (Professional Industrial Theme)
PRIMARY_COLOR = "#2E3B4E"      # Dark blue-gray
SECONDARY_COLOR = "#3D5A80"    # Medium blue
ACCENT_COLOR = "#98C1D9"       # Light blue
SUCCESS_COLOR = "#2ECC71"      # Green
WARNING_COLOR = "#F39C12"      # Orange
ERROR_COLOR = "#E74C3C"        # Red
BACKGROUND_COLOR = "#FFFFFF"   # Light gray
TEXT_COLOR = "#000000"         # Dark gray
CARD_COLOR = "#FFFFFF"         # White

# Register Addresses (PLC Simulation)
REGISTER_MAP = {
    "D20": {"name": "Temperature", "unit": "°C", "min": 0, "max": 100},
    "D21": {"name": "Pressure", "unit": "bar", "min": 0, "max": 10},
    "D22": {"name": "Vibration", "unit": "mm/s", "min": 0, "max": 50},
    "D23": {"name": "Speed", "unit": "RPM", "min": 0, "max": 3000},
    "D24": {"name": "Current", "unit": "A", "min": 0, "max": 100},
    "D25": {"name": "Voltage", "unit": "V", "min": 0, "max": 500},
}