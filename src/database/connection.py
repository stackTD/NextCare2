"""
Database connection and management
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any
import logging
try:
    from ..utils.constants import DEFAULT_DB_HOST, DEFAULT_DB_PORT, DEFAULT_DB_NAME, DEFAULT_DB_USER
except ImportError:
    from utils.constants import DEFAULT_DB_HOST, DEFAULT_DB_PORT, DEFAULT_DB_NAME, DEFAULT_DB_USER

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection and management"""
    
    def __init__(self):
        self.connection = None
        self.host = os.getenv('DB_HOST', DEFAULT_DB_HOST)
        self.port = os.getenv('DB_PORT', DEFAULT_DB_PORT)
        self.database = os.getenv('DB_NAME', DEFAULT_DB_NAME)
        self.user = os.getenv('DB_USER', DEFAULT_DB_USER)
        self.password = os.getenv('DB_PASSWORD', 'nextcare_password')
        
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                cursor_factory=RealDictCursor
            )
            self.connection.autocommit = True
            logger.info("Database connection established")
            return True
        except psycopg2.Error as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[list]:
        """Execute a SELECT query and return results"""
        try:
            if not self.connection:
                if not self.connect():
                    return None
                    
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Query execution failed: {e}")
            return None
    
    def execute_command(self, command: str, params: tuple = None) -> bool:
        """Execute an INSERT, UPDATE, or DELETE command"""
        try:
            if not self.connection:
                if not self.connect():
                    return False
                    
            with self.connection.cursor() as cursor:
                cursor.execute(command, params)
                return True
        except psycopg2.Error as e:
            logger.error(f"Command execution failed: {e}")
            return False
    
    def execute_many(self, command: str, params_list: list) -> bool:
        """Execute multiple commands with different parameters"""
        try:
            if not self.connection:
                if not self.connect():
                    return False
                    
            with self.connection.cursor() as cursor:
                cursor.executemany(command, params_list)
                return True
        except psycopg2.Error as e:
            logger.error(f"Batch command execution failed: {e}")
            return False
    
    def create_database_if_not_exists(self) -> bool:
        """Create database if it doesn't exist"""
        try:
            # Connect to default postgres database first
            temp_connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database='postgres',
                user=self.user,
                password=self.password
            )
            temp_connection.autocommit = True
            
            with temp_connection.cursor() as cursor:
                # Check if database exists
                cursor.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    (self.database,)
                )
                if not cursor.fetchone():
                    cursor.execute(f'CREATE DATABASE "{self.database}"')
                    logger.info(f"Database '{self.database}' created")
                else:
                    logger.info(f"Database '{self.database}' already exists")
            
            temp_connection.close()
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Database creation failed: {e}")
            return False
    
    def initialize_schema(self) -> bool:
        """Initialize database schema with tables and initial data"""
        from .models import ALL_TABLES, ALL_INDEXES, INITIAL_DATA
        
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            # Create tables
            for table_sql in ALL_TABLES:
                if not self.execute_command(table_sql):
                    return False
            
            # Create indexes
            for index_sql in ALL_INDEXES:
                if not self.execute_command(index_sql):
                    return False
            
            # Insert initial data
            for data_sql in INITIAL_DATA:
                if not self.execute_command(data_sql):
                    return False
            
            logger.info("Database schema initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        """Test database connection and return status"""
        result = {
            'connected': False,
            'error': None,
            'database_info': None
        }
        
        try:
            if self.connect():
                # Get database info
                db_info = self.execute_query("SELECT version(), current_database(), current_user")
                if db_info:
                    result['connected'] = True
                    result['database_info'] = db_info[0]
                else:
                    result['error'] = "Failed to retrieve database information"
            else:
                result['error'] = "Failed to establish connection"
                
        except Exception as e:
            result['error'] = str(e)
        
        return result

# Global database manager instance
db_manager = DatabaseManager()