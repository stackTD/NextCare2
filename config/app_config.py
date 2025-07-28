"""
NextCare Application Configuration

This module contains the main application configuration classes for different environments.
"""

import os
from datetime import timedelta
from typing import Type
from config.database_config import get_database_config


class Config:
    """Base configuration class"""
    
    # Application settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database settings
    _db_config = get_database_config()
    SQLALCHEMY_DATABASE_URI = _db_config.get_sqlalchemy_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': _db_config.pool_size,
        'max_overflow': _db_config.max_overflow,
        'pool_timeout': _db_config.pool_timeout,
        'pool_recycle': _db_config.pool_recycle,
        'pool_pre_ping': True
    }
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Mail settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@nextcare.com')
    
    # NextCare specific settings
    NEXTCARE_VERSION = '1.0.0'
    NEXTCARE_APP_NAME = 'NextCare'
    
    # Mock sensor settings
    ENABLE_MOCK_SENSORS = os.getenv('ENABLE_MOCK_SENSORS', 'False').lower() == 'true'
    SENSOR_UPDATE_INTERVAL = int(os.getenv('SENSOR_UPDATE_INTERVAL', '60'))
    
    # Alert settings
    MAX_ALERTS_PER_MACHINE = int(os.getenv('MAX_ALERTS_PER_MACHINE', '100'))
    ALERT_RETENTION_DAYS = int(os.getenv('ALERT_RETENTION_DAYS', '90'))
    
    # Data retention settings
    SENSOR_DATA_RETENTION_DAYS = int(os.getenv('SENSOR_DATA_RETENTION_DAYS', '365'))
    
    # Pagination settings
    RECORDS_PER_PAGE = int(os.getenv('RECORDS_PER_PAGE', '50'))
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/nextcare.log')
    
    # Cache settings
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    
    @staticmethod
    def init_app(app):
        """Initialize the application with this configuration"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    
    # Less strict security for development
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False  # Disable CSRF for easier API testing
    
    # Enable mock sensors by default in development
    ENABLE_MOCK_SENSORS = True
    SENSOR_UPDATE_INTERVAL = 30  # More frequent updates for testing
    
    # Shorter data retention for development
    SENSOR_DATA_RETENTION_DAYS = 30
    ALERT_RETENTION_DAYS = 30
    
    # Development-specific logging
    LOG_LEVEL = 'DEBUG'
    
    @staticmethod
    def init_app(app):
        """Initialize development-specific settings"""
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Set up file logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/nextcare_dev.log', 
            maxBytes=10240, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.DEBUG)
        app.logger.info('NextCare development startup')


class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Production security settings
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    WTF_CSRF_ENABLED = True
    
    # Production secrets must be provided via environment
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Disable mock sensors in production by default
    ENABLE_MOCK_SENSORS = os.getenv('ENABLE_MOCK_SENSORS', 'False').lower() == 'true'
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    @staticmethod
    def init_app(app):
        """Initialize production-specific settings"""
        import logging
        from logging.handlers import RotatingFileHandler, SMTPHandler
        
        # File logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/nextcare_prod.log',
            maxBytes=1024*1024,  # 1MB
            backupCount=20
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
        
        # Email logging for critical errors
        if os.getenv('MAIL_SERVER'):
            auth = None
            if os.getenv('MAIL_USERNAME') or os.getenv('MAIL_PASSWORD'):
                auth = (os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
            
            secure = None
            if os.getenv('MAIL_USE_TLS'):
                secure = ()
            
            mail_handler = SMTPHandler(
                mailhost=(os.getenv('MAIL_SERVER'), os.getenv('MAIL_PORT', 587)),
                fromaddr=os.getenv('MAIL_DEFAULT_SENDER', 'noreply@nextcare.com'),
                toaddrs=os.getenv('ADMIN_EMAIL', 'admin@nextcare.com').split(','),
                subject='NextCare Application Error',
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            mail_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            app.logger.addHandler(mail_handler)
        
        app.logger.setLevel(logging.WARNING)
        app.logger.info('NextCare production startup')


class TestingConfig(Config):
    """Testing configuration"""
    
    DEBUG = True
    TESTING = True
    
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Fast intervals for testing
    SENSOR_UPDATE_INTERVAL = 1
    
    # Shorter retention for testing
    SENSOR_DATA_RETENTION_DAYS = 1
    ALERT_RETENTION_DAYS = 1
    
    # Simple cache for testing
    CACHE_TYPE = 'simple'
    
    @staticmethod
    def init_app(app):
        """Initialize testing-specific settings"""
        app.logger.setLevel(logging.CRITICAL)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Type[Config]:
    """
    Get configuration class based on environment
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
                    If None, uses FLASK_ENV environment variable
    
    Returns:
        Configuration class
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    return config.get(config_name, config['default'])


# Example environment file template
ENV_TEMPLATE = """
# NextCare Environment Configuration Template
# Copy this to .env and modify the values as needed

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nextcare
DB_USER=nextcare_user
DB_PASSWORD=your_database_password
DB_SSL_MODE=prefer
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Application Settings
ENABLE_MOCK_SENSORS=True
SENSOR_UPDATE_INTERVAL=60
MAX_ALERTS_PER_MACHINE=100
ALERT_RETENTION_DAYS=90
SENSOR_DATA_RETENTION_DAYS=365

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=noreply@nextcare.com
ADMIN_EMAIL=admin@nextcare.com

# Security Settings
SESSION_TIMEOUT_HOURS=24

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/nextcare.log

# File Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Cache Settings
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://
"""


if __name__ == "__main__":
    """Generate example .env file"""
    print("NextCare Configuration")
    print("=" * 50)
    
    # Show current configuration
    current_config = get_config()
    print(f"Current environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Configuration class: {current_config.__name__}")
    print(f"Debug mode: {current_config.DEBUG}")
    print(f"Testing mode: {current_config.TESTING}")
    print(f"Mock sensors enabled: {current_config.ENABLE_MOCK_SENSORS}")
    
    # Option to generate .env template
    generate_env = input("\nGenerate .env template file? (y/n): ").lower().strip()
    if generate_env == 'y':
        with open('.env.template', 'w') as f:
            f.write(ENV_TEMPLATE)
        print("✓ .env.template file generated!")
        print("Copy this file to .env and modify the values as needed.")