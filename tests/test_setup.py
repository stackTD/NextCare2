#!/usr/bin/env python3
"""
NextCare Database Connection Test

This script tests the database connection and verifies the setup.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database_config import DatabaseConnection
from sensors.mock_sensors import get_mock_sensor_system
import logging

def test_database_connection():
    """Test database connection"""
    print("Testing Database Connection")
    print("=" * 50)
    
    try:
        db_conn = DatabaseConnection()
        success, error = db_conn.test_connection()
        
        if success:
            print("✓ Database connection successful!")
            
            # Get database information
            info = db_conn.get_database_info()
            if info:
                print("\nDatabase Information:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
            
            return True
        else:
            print(f"✗ Database connection failed: {error}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing database connection: {e}")
        return False

def test_mock_sensors():
    """Test mock sensor system"""
    print("\n\nTesting Mock Sensor System")
    print("=" * 50)
    
    try:
        system = get_mock_sensor_system()
        status = system.get_system_status()
        
        print(f"✓ Mock sensor system initialized")
        print(f"  Total machines: {status['total_machines']}")
        print(f"  Active machines: {status['active_machines']}")
        print(f"  Total sensors: {status['total_sensors']}")
        print(f"  Update interval: {status['update_interval']} seconds")
        
        # Get sample readings
        readings = system.get_current_readings()
        if readings:
            print(f"\nSample sensor readings ({len(readings)} total):")
            for reading in readings[:5]:  # Show first 5
                print(f"  {reading.machine_id}.{reading.parameter_id}: {reading.value:.2f}")
            if len(readings) > 5:
                print(f"  ... and {len(readings) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing mock sensors: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n\nTesting Configuration")
    print("=" * 50)
    
    try:
        from config.app_config import get_config
        
        config_class = get_config()
        print(f"✓ Configuration loaded: {config_class.__name__}")
        print(f"  Debug mode: {config_class.DEBUG}")
        print(f"  Testing mode: {config_class.TESTING}")
        print(f"  Mock sensors enabled: {config_class.ENABLE_MOCK_SENSORS}")
        print(f"  Database URI configured: {'Yes' if config_class.SQLALCHEMY_DATABASE_URI else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing configuration: {e}")
        return False

def main():
    """Run all tests"""
    print("NextCare Setup Verification")
    print("=" * 70)
    
    # Set up basic logging
    logging.basicConfig(level=logging.WARNING)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Configuration", test_configuration),
        ("Mock Sensors", test_mock_sensors),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ Unexpected error in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print("\n\nTest Summary")
    print("=" * 70)
    
    passed = 0
    total = len(tests)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{test_name}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! NextCare setup appears to be working correctly.")
        print("\nYou can now:")
        print("1. Start the mock sensor system")
        print("2. Run the NextCare application")
        print("3. Access the web interface")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check your setup.")
        print("\nCommon issues:")
        print("- PostgreSQL not running or not accessible")
        print("- Database credentials incorrect")
        print("- Missing Python dependencies")
        print("- Environment variables not set")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)