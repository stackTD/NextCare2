"""
Authentication and authorization utilities
"""

from typing import Optional, Dict, Any
import logging

# Use try/except to handle both relative and absolute imports
try:
    from ..database.operations import db_ops
    from .constants import ROLES
except ImportError:
    # Fallback to absolute imports when running directly
    from database.operations import db_ops
    from utils.constants import ROLES

logger = logging.getLogger(__name__)

class AuthManager:
    """Authentication and session management"""
    
    def __init__(self):
        self.current_user = None
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate user and create session"""
        user = db_ops.authenticate_user(username, password)
        if user:
            self.current_user = user
            logger.info(f"User {username} logged in successfully with role {user['role']}")
            return True
        
        logger.warning(f"Failed login attempt for username: {username}")
        return False
    
    def logout(self):
        """Clear current session"""
        if self.current_user:
            logger.info(f"User {self.current_user['username']} logged out")
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current user information"""
        return self.current_user
    
    def get_user_role(self) -> Optional[str]:
        """Get current user role"""
        return self.current_user['role'] if self.current_user else None
    
    def has_role(self, role: str) -> bool:
        """Check if current user has specific role"""
        current_role = self.get_user_role()
        return current_role == role if current_role else False
    
    def has_admin_access(self) -> bool:
        """Check if current user has admin access"""
        return self.has_role('admin')
    
    def has_manager_access(self) -> bool:
        """Check if current user has manager or admin access"""
        role = self.get_user_role()
        return role in ['admin', 'manager'] if role else False
    
    def has_engineer_access(self) -> bool:
        """Check if current user has any access (engineer, manager, or admin)"""
        role = self.get_user_role()
        return role in ROLES if role else False
    
    def can_manage_machines(self) -> bool:
        """Check if user can create/edit/delete machines"""
        return self.has_manager_access()
    
    def can_manage_users(self) -> bool:
        """Check if user can create/edit/delete users"""
        return self.has_admin_access()
    
    def can_access_machine(self, machine_id: int) -> bool:
        """Check if current user can access specific machine"""
        if not self.current_user:
            return False
        
        role = self.get_user_role()
        
        # Admins and managers have access to all machines
        if role in ['admin', 'manager']:
            return True
        
        # Engineers need explicit access
        if role == 'engineer':
            user_machines = db_ops.get_user_machines(self.current_user['id'])
            return any(machine['id'] == machine_id for machine in user_machines)
        
        return False

# Global authentication manager
auth_manager = AuthManager()