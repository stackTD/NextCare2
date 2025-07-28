"""
NextCare Database Configuration

This module handles database connection configuration for the NextCare application.
It supports both development and production environments with proper error handling.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from urllib.parse import quote_plus
import psycopg2
from psycopg2.extras import RealDictCursor


@dataclass
class DatabaseConfig:
    """Database configuration dataclass"""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = 'prefer'
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


class DatabaseConnection:
    """Database connection manager for NextCare"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database connection manager
        
        Args:
            config: Database configuration object. If None, loads from environment.
        """
        self.config = config or self._load_config_from_env()
        self.logger = logging.getLogger(__name__)
        
    def _load_config_from_env(self) -> DatabaseConfig:
        """Load database configuration from environment variables"""
        return DatabaseConfig(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'nextcare'),
            username=os.getenv('DB_USER', 'nextcare_user'),
            password=os.getenv('DB_PASSWORD', ''),
            ssl_mode=os.getenv('DB_SSL_MODE', 'prefer'),
            pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20')),
            pool_timeout=int(os.getenv('DB_POOL_TIMEOUT', '30')),
            pool_recycle=int(os.getenv('DB_POOL_RECYCLE', '3600'))
        )
    
    def get_connection_string(self, include_password: bool = True) -> str:
        """
        Generate PostgreSQL connection string
        
        Args:
            include_password: Whether to include password in connection string
            
        Returns:
            PostgreSQL connection string
        """
        password_part = f":{quote_plus(self.config.password)}" if include_password and self.config.password else ""
        
        return (
            f"postgresql://{self.config.username}{password_part}@"
            f"{self.config.host}:{self.config.port}/{self.config.database}"
            f"?sslmode={self.config.ssl_mode}"
        )
    
    def get_sqlalchemy_url(self) -> str:
        """Get SQLAlchemy-compatible database URL"""
        return self.get_connection_string(include_password=True)
    
    def get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters for psycopg2"""
        return {
            'host': self.config.host,
            'port': self.config.port,
            'database': self.config.database,
            'user': self.config.username,
            'password': self.config.password,
            'sslmode': self.config.ssl_mode,
            'cursor_factory': RealDictCursor
        }
    
    def test_connection(self) -> tuple[bool, Optional[str]]:
        """
        Test database connection
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            with psycopg2.connect(**self.get_connection_params()) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()
                    self.logger.info(f"Database connection successful: {version['version']}")
                    return True, None
        except psycopg2.Error as e:
            error_msg = f"Database connection failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during connection test: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_database_info(self) -> Optional[Dict[str, Any]]:
        """
        Get database information and statistics
        
        Returns:
            Dictionary with database information or None if connection fails
        """
        try:
            with psycopg2.connect(**self.get_connection_params()) as conn:
                with conn.cursor() as cursor:
                    # Get database version
                    cursor.execute("SELECT version();")
                    version_info = cursor.fetchone()
                    
                    # Get database size
                    cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
                    db_size = cursor.fetchone()
                    
                    # Get table count
                    cursor.execute("""
                        SELECT count(*) 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
                    """)
                    table_count = cursor.fetchone()
                    
                    # Get connection count
                    cursor.execute("""
                        SELECT count(*) 
                        FROM pg_stat_activity 
                        WHERE datname = current_database();
                    """)
                    connection_count = cursor.fetchone()
                    
                    return {
                        'version': version_info['version'],
                        'database_size': db_size['pg_size_pretty'],
                        'table_count': table_count['count'],
                        'active_connections': connection_count['count'],
                        'database_name': self.config.database,
                        'host': self.config.host,
                        'port': self.config.port
                    }
        except Exception as e:
            self.logger.error(f"Failed to get database info: {str(e)}")
            return None


# Factory functions for common configurations
def create_development_config() -> DatabaseConfig:
    """Create development database configuration"""
    return DatabaseConfig(
        host='localhost',
        port=5432,
        database='nextcare_dev',
        username='nextcare_user',
        password='dev_password',
        ssl_mode='disable',
        pool_size=5,
        max_overflow=10
    )


def create_production_config() -> DatabaseConfig:
    """Create production database configuration from environment"""
    config = DatabaseConfig(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '5432')),
        database=os.getenv('DB_NAME', 'nextcare'),
        username=os.getenv('DB_USER', 'nextcare_user'),
        password=os.getenv('DB_PASSWORD', ''),
        ssl_mode=os.getenv('DB_SSL_MODE', 'require'),
        pool_size=int(os.getenv('DB_POOL_SIZE', '20')),
        max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '50')),
        pool_timeout=int(os.getenv('DB_POOL_TIMEOUT', '30')),
        pool_recycle=int(os.getenv('DB_POOL_RECYCLE', '3600'))
    )
    
    # Validate required environment variables for production
    required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return config


def get_database_config() -> DatabaseConfig:
    """
    Get database configuration based on environment
    
    Returns:
        DatabaseConfig instance
    """
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return create_production_config()
    else:
        return create_development_config() if env == 'development' else DatabaseConfig(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'nextcare'),
            username=os.getenv('DB_USER', 'nextcare_user'),
            password=os.getenv('DB_PASSWORD', ''),
        )


# Global database connection instance
db_connection = DatabaseConnection()


def get_db_connection() -> DatabaseConnection:
    """Get the global database connection instance"""
    return db_connection


# Example usage and testing functions
if __name__ == "__main__":
    # Example usage
    print("NextCare Database Configuration Test")
    print("=" * 50)
    
    # Test connection
    conn = DatabaseConnection()
    success, error = conn.test_connection()
    
    if success:
        print("✓ Database connection successful!")
        
        # Get database info
        info = conn.get_database_info()
        if info:
            print("\nDatabase Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        
        print(f"\nConnection String (without password): {conn.get_connection_string(include_password=False)}")
    else:
        print(f"✗ Database connection failed: {error}")
        print("\nPlease check your database configuration and ensure PostgreSQL is running.")
        print("Required environment variables:")
        print("  DB_HOST (default: localhost)")
        print("  DB_PORT (default: 5432)")
        print("  DB_NAME (default: nextcare)")
        print("  DB_USER (default: nextcare_user)")
        print("  DB_PASSWORD (required)")