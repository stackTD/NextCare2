"""
Test script for role-based access control functionality
"""

import sys
import os

# Add src directory to path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_dir)

from database.operations import db_ops
from utils.auth import auth_manager

def test_role_based_permissions():
    """Test role-based permission system"""
    
    print("=== Testing Role-Based Access Control ===\n")
    
    # Test different user roles
    test_users = [
        ('admin', 'admin'),
        ('manager1', 'manager1'),
        ('engineer1', 'engineer1')
    ]
    
    for username, password in test_users:
        print(f"Testing user: {username}")
        
        # Try to login
        if auth_manager.login(username, password):
            user = auth_manager.get_current_user()
            role = user['role']
            print(f"  ✓ Login successful - Role: {role}")
            
            # Test permissions
            print(f"  Permissions for {role}:")
            print(f"    - Can manage machines: {auth_manager.can_manage_machines()}")
            print(f"    - Can manage users: {auth_manager.can_manage_users()}")
            print(f"    - Can manage engineers: {auth_manager.can_manage_engineers()}")
            print(f"    - Can access settings: {auth_manager.can_access_settings()}")
            print(f"    - Can assign machines: {auth_manager.can_assign_machines()}")
            
            # Test machine access
            accessible_machines = auth_manager.get_accessible_machines()
            print(f"    - Accessible machine count: {len(accessible_machines)}")
            
            # Test database operations
            try:
                users = db_ops.get_users()
                print(f"    - Can query users: ✓ ({len(users)} users)")
            except Exception as e:
                print(f"    - Can query users: ✗ ({str(e)})")
            
            try:
                machines = db_ops.get_machines(user['id'], user['role'])
                print(f"    - Can query machines: ✓ ({len(machines)} machines)")
            except Exception as e:
                print(f"    - Can query machines: ✗ ({str(e)})")
            
            auth_manager.logout()
        else:
            print(f"  ✗ Login failed for {username}")
        
        print()

def test_database_operations():
    """Test database operations"""
    
    print("=== Testing Database Operations ===\n")
    
    # Login as admin for testing
    if auth_manager.login('admin', 'admin'):
        print("Testing as admin user...")
        
        # Test user management
        try:
            users = db_ops.get_users()
            print(f"✓ Retrieved {len(users)} users")
            
            engineers = db_ops.get_users(role='engineer')
            print(f"✓ Retrieved {len(engineers)} engineers")
            
            managers = db_ops.get_users(role='manager')
            print(f"✓ Retrieved {len(managers)} managers")
            
        except Exception as e:
            print(f"✗ Error testing user operations: {e}")
        
        # Test machine operations
        try:
            machines = db_ops.get_machines()
            print(f"✓ Retrieved {len(machines)} machines")
            
            for machine in machines[:1]:  # Test first machine only
                parameters = db_ops.get_parameters(machine['id'])
                print(f"✓ Machine '{machine['name']}' has {len(parameters)} parameters")
                
                # Test machine access
                machine_users = db_ops.get_machine_users(machine['id'])
                print(f"✓ Machine '{machine['name']}' has {len(machine_users)} assigned users")
                
        except Exception as e:
            print(f"✗ Error testing machine operations: {e}")
        
        auth_manager.logout()
    else:
        print("✗ Could not login as admin for testing")

def main():
    """Main test function"""
    print("NextCare2 Role-Based Access Control Test")
    print("=" * 50)
    
    try:
        # Test database connection
        from database.connection import db_manager
        result = db_manager.test_connection()
        
        if result['connected']:
            print("✓ Database connection successful")
            print()
            
            # Run tests
            test_role_based_permissions()
            test_database_operations()
            
        else:
            print(f"✗ Database connection failed: {result['error']}")
            print("Make sure PostgreSQL is running and configured correctly.")
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("This test requires PyQt6 and other dependencies.")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    print("Test completed.")

if __name__ == "__main__":
    main()