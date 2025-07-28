"""
Database operations and business logic
"""

import bcrypt
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
try:
    from .connection import db_manager
except ImportError:
    from database.connection import db_manager

logger = logging.getLogger(__name__)

class DatabaseOperations:
    """High-level database operations"""
    
    def __init__(self):
        self.db = db_manager
    
    # User Management
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user info"""
        query = """
        SELECT id, username, password_hash, role, full_name, email, is_active
        FROM users 
        WHERE username = %s AND is_active = TRUE
        """
        
        users = self.db.execute_query(query, (username,))
        if not users:
            return None
        
        user = users[0]
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'full_name': user['full_name'],
                'email': user['email']
            }
        
        return None
    
    def create_user(self, username: str, password: str, role: str, full_name: str, email: str = None) -> bool:
        """Create a new user"""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        command = """
        INSERT INTO users (username, password_hash, role, full_name, email)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        return self.db.execute_command(command, (username, password_hash, role, full_name, email))
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get all active users"""
        query = """
        SELECT id, username, role, full_name, email, created_at, is_active
        FROM users 
        WHERE is_active = TRUE
        ORDER BY full_name
        """
        
        return self.db.execute_query(query) or []
    
    # Machine Management
    def get_machines(self, user_id: int = None, role: str = None) -> List[Dict[str, Any]]:
        """Get machines based on user role and access"""
        if role == 'admin' or role == 'manager':
            # Admins and managers see all machines
            query = """
            SELECT m.*, u.full_name as created_by_name
            FROM machines m
            LEFT JOIN users u ON m.created_by = u.id
            WHERE m.is_active = TRUE
            ORDER BY m.name
            """
            return self.db.execute_query(query) or []
        
        elif role == 'engineer' and user_id:
            # Engineers see only machines they have access to
            query = """
            SELECT m.*, u.full_name as created_by_name
            FROM machines m
            LEFT JOIN users u ON m.created_by = u.id
            INNER JOIN user_machine_access uma ON m.id = uma.machine_id
            WHERE m.is_active = TRUE AND uma.user_id = %s
            ORDER BY m.name
            """
            return self.db.execute_query(query, (user_id,)) or []
        
        return []
    
    def create_machine(self, name: str, description: str, location: str, machine_type: str, created_by: int) -> Optional[int]:
        """Create a new machine and return its ID"""
        command = """
        INSERT INTO machines (name, description, location, machine_type, created_by)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(command, (name, description, location, machine_type, created_by))
        return result[0]['id'] if result else None
    
    def update_machine(self, machine_id: int, name: str, description: str, location: str, machine_type: str) -> bool:
        """Update machine information"""
        command = """
        UPDATE machines 
        SET name = %s, description = %s, location = %s, machine_type = %s
        WHERE id = %s
        """
        
        return self.db.execute_command(command, (name, description, location, machine_type, machine_id))
    
    def delete_machine(self, machine_id: int) -> bool:
        """Soft delete a machine"""
        command = "UPDATE machines SET is_active = FALSE WHERE id = %s"
        return self.db.execute_command(command, (machine_id,))
    
    # Parameter Management
    def get_parameters(self, machine_id: int) -> List[Dict[str, Any]]:
        """Get parameters for a specific machine"""
        query = """
        SELECT * FROM parameters 
        WHERE machine_id = %s AND is_active = TRUE
        ORDER BY name
        """
        
        return self.db.execute_query(query, (machine_id,)) or []
    
    def create_parameter(self, machine_id: int, name: str, register_address: str, 
                        unit: str, min_value: float, max_value: float, 
                        alarm_low: float, alarm_high: float) -> bool:
        """Create a new parameter"""
        command = """
        INSERT INTO parameters (machine_id, name, register_address, unit, min_value, max_value, alarm_low, alarm_high)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        return self.db.execute_command(command, (
            machine_id, name, register_address, unit, min_value, max_value, alarm_low, alarm_high
        ))
    
    def update_parameter(self, parameter_id: int, name: str, register_address: str,
                        unit: str, min_value: float, max_value: float,
                        alarm_low: float, alarm_high: float) -> bool:
        """Update parameter information"""
        command = """
        UPDATE parameters 
        SET name = %s, register_address = %s, unit = %s, min_value = %s, max_value = %s, alarm_low = %s, alarm_high = %s
        WHERE id = %s
        """
        
        return self.db.execute_command(command, (
            name, register_address, unit, min_value, max_value, alarm_low, alarm_high, parameter_id
        ))
    
    def delete_parameter(self, parameter_id: int) -> bool:
        """Soft delete a parameter"""
        command = "UPDATE parameters SET is_active = FALSE WHERE id = %s"
        return self.db.execute_command(command, (parameter_id,))
    
    # Sensor Data Management
    def insert_sensor_data(self, parameter_id: int, value: float, quality: bool = True) -> bool:
        """Insert sensor data"""
        command = """
        INSERT INTO sensor_data (parameter_id, value, quality)
        VALUES (%s, %s, %s)
        """
        
        return self.db.execute_command(command, (parameter_id, value, quality))
    
    def get_latest_sensor_data(self, machine_id: int) -> List[Dict[str, Any]]:
        """Get latest sensor data for all parameters of a machine"""
        query = """
        SELECT p.id as parameter_id, p.name as parameter_name, p.unit, p.alarm_low, p.alarm_high,
               sd.value, sd.timestamp, sd.quality
        FROM parameters p
        LEFT JOIN LATERAL (
            SELECT value, timestamp, quality
            FROM sensor_data 
            WHERE parameter_id = p.id 
            ORDER BY timestamp DESC 
            LIMIT 1
        ) sd ON true
        WHERE p.machine_id = %s AND p.is_active = TRUE
        ORDER BY p.name
        """
        
        return self.db.execute_query(query, (machine_id,)) or []
    
    def get_parameter_history(self, parameter_id: int, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical data for a parameter"""
        query = """
        SELECT value, timestamp, quality
        FROM sensor_data
        WHERE parameter_id = %s AND timestamp >= %s
        ORDER BY timestamp DESC
        LIMIT 1000
        """
        
        start_time = datetime.now() - timedelta(hours=hours)
        return self.db.execute_query(query, (parameter_id, start_time)) or []
    
    # User Access Management
    def grant_machine_access(self, user_id: int, machine_id: int) -> bool:
        """Grant user access to a machine"""
        command = """
        INSERT INTO user_machine_access (user_id, machine_id)
        VALUES (%s, %s)
        ON CONFLICT (user_id, machine_id) DO NOTHING
        """
        
        return self.db.execute_command(command, (user_id, machine_id))
    
    def revoke_machine_access(self, user_id: int, machine_id: int) -> bool:
        """Revoke user access to a machine"""
        command = "DELETE FROM user_machine_access WHERE user_id = %s AND machine_id = %s"
        return self.db.execute_command(command, (user_id, machine_id))
    
    def get_user_machines(self, user_id: int) -> List[Dict[str, Any]]:
        """Get machines accessible to a specific user"""
        query = """
        SELECT m.*, uma.granted_at
        FROM machines m
        INNER JOIN user_machine_access uma ON m.id = uma.machine_id
        WHERE uma.user_id = %s AND m.is_active = TRUE
        ORDER BY m.name
        """
        
        return self.db.execute_query(query, (user_id,)) or []

# Global database operations instance
db_ops = DatabaseOperations()