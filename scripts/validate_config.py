#!/usr/bin/env python3
"""
NextCare Configuration Validator

This script validates the NextCare configuration and environment setup.
"""

import os
import sys
import re
from typing import List, Tuple, Dict, Any


class ConfigValidator:
    """Configuration validation class"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.config: Dict[str, Any] = {}
        
    def load_env_file(self, filename: str = '.env') -> bool:
        """Load environment file"""
        if not os.path.exists(filename):
            self.errors.append(f"Environment file {filename} not found")
            return False
        
        try:
            with open(filename, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            self.config[key.strip()] = value.strip()
                        else:
                            self.warnings.append(f"Line {line_num}: Invalid format: {line}")
            return True
        except Exception as e:
            self.errors.append(f"Error reading {filename}: {e}")
            return False
    
    def validate_database_config(self) -> None:
        """Validate database configuration"""
        required_db_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        
        for var in required_db_vars:
            if var not in self.config or not self.config[var]:
                self.errors.append(f"Required database variable {var} is missing or empty")
        
        # Validate DB_PORT is numeric
        if 'DB_PORT' in self.config:
            try:
                port = int(self.config['DB_PORT'])
                if port < 1 or port > 65535:
                    self.errors.append("DB_PORT must be between 1 and 65535")
            except ValueError:
                self.errors.append("DB_PORT must be a valid number")
        
        # Validate database name format
        if 'DB_NAME' in self.config:
            db_name = self.config['DB_NAME']
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', db_name):
                self.errors.append("DB_NAME must start with a letter and contain only letters, numbers, and underscores")
        
        # Check password strength
        if 'DB_PASSWORD' in self.config:
            password = self.config['DB_PASSWORD']
            if len(password) < 8:
                self.warnings.append("DB_PASSWORD should be at least 8 characters long")
            if password in ['password', '123456', 'admin', 'root']:
                self.errors.append("DB_PASSWORD is too weak - avoid common passwords")
    
    def validate_app_config(self) -> None:
        """Validate application configuration"""
        # Check Flask environment
        if 'FLASK_ENV' in self.config:
            valid_envs = ['development', 'production', 'testing']
            if self.config['FLASK_ENV'] not in valid_envs:
                self.warnings.append(f"FLASK_ENV should be one of: {', '.join(valid_envs)}")
        
        # Check secret key
        if 'SECRET_KEY' in self.config:
            secret_key = self.config['SECRET_KEY']
            if len(secret_key) < 16:
                self.errors.append("SECRET_KEY should be at least 16 characters long")
            if secret_key in ['your-secret-key-here', 'dev-secret-key-change-in-production']:
                self.errors.append("SECRET_KEY should be changed from the default value")
        else:
            self.errors.append("SECRET_KEY is required")
        
        # Check boolean values
        boolean_vars = ['DEBUG', 'ENABLE_MOCK_SENSORS', 'MAIL_USE_TLS']
        for var in boolean_vars:
            if var in self.config:
                value = self.config[var].lower()
                if value not in ['true', 'false', '1', '0', 'yes', 'no']:
                    self.warnings.append(f"{var} should be 'true' or 'false'")
        
        # Check numeric values
        numeric_vars = {
            'SENSOR_UPDATE_INTERVAL': (1, 3600),
            'MAX_ALERTS_PER_MACHINE': (1, 1000),
            'ALERT_RETENTION_DAYS': (1, 365),
            'SENSOR_DATA_RETENTION_DAYS': (1, 3650)
        }
        
        for var, (min_val, max_val) in numeric_vars.items():
            if var in self.config:
                try:
                    value = int(self.config[var])
                    if value < min_val or value > max_val:
                        self.warnings.append(f"{var} should be between {min_val} and {max_val}")
                except ValueError:
                    self.errors.append(f"{var} must be a valid number")
    
    def validate_email_config(self) -> None:
        """Validate email configuration"""
        email_vars = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD']
        email_configured = any(var in self.config and self.config[var] for var in email_vars)
        
        if email_configured:
            # If any email config is present, validate all required fields
            required_email_vars = ['MAIL_SERVER', 'MAIL_PORT']
            for var in required_email_vars:
                if var not in self.config or not self.config[var]:
                    self.warnings.append(f"Email configuration incomplete: {var} is missing")
            
            # Validate mail port
            if 'MAIL_PORT' in self.config:
                try:
                    port = int(self.config['MAIL_PORT'])
                    if port not in [25, 465, 587, 993, 995]:
                        self.warnings.append("MAIL_PORT should typically be 25, 465, 587, 993, or 995")
                except ValueError:
                    self.errors.append("MAIL_PORT must be a valid number")
            
            # Validate email address format
            if 'MAIL_USERNAME' in self.config:
                email = self.config['MAIL_USERNAME']
                if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                    self.warnings.append("MAIL_USERNAME should be a valid email address")
    
    def validate_file_paths(self) -> None:
        """Validate file paths and directories"""
        path_vars = {
            'LOG_FILE': 'file',
            'UPLOAD_FOLDER': 'directory'
        }
        
        for var, path_type in path_vars.items():
            if var in self.config:
                path = self.config[var]
                if path_type == 'directory':
                    if not os.path.exists(path):
                        self.warnings.append(f"Directory {path} does not exist (will be created automatically)")
                elif path_type == 'file':
                    directory = os.path.dirname(path)
                    if directory and not os.path.exists(directory):
                        self.warnings.append(f"Log directory {directory} does not exist (will be created automatically)")
    
    def validate_all(self, filename: str = '.env') -> Tuple[List[str], List[str]]:
        """Run all validations"""
        self.errors.clear()
        self.warnings.clear()
        
        if not self.load_env_file(filename):
            return self.errors, self.warnings
        
        self.validate_database_config()
        self.validate_app_config()
        self.validate_email_config()
        self.validate_file_paths()
        
        return self.errors, self.warnings
    
    def print_results(self) -> bool:
        """Print validation results"""
        print("NextCare Configuration Validation")
        print("=" * 50)
        
        if not self.errors and not self.warnings:
            print("✅ Configuration is valid!")
            return True
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        print(f"\nValidation Summary:")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")
        print(f"  Status: {'❌ FAILED' if self.errors else '⚠️  PASSED WITH WARNINGS'}")
        
        return len(self.errors) == 0


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate NextCare configuration')
    parser.add_argument('--env-file', default='.env', help='Environment file to validate')
    parser.add_argument('--fix', action='store_true', help='Suggest fixes for common issues')
    
    args = parser.parse_args()
    
    validator = ConfigValidator()
    errors, warnings = validator.validate_all(args.env_file)
    
    success = validator.print_results()
    
    if args.fix and (errors or warnings):
        print("\n🔧 SUGGESTED FIXES:")
        
        if not os.path.exists(args.env_file):
            print("  1. Create .env file from template:")
            print("     cp .env.template .env")
        
        if any('SECRET_KEY' in error for error in errors):
            print("  2. Generate a secure secret key:")
            print("     python -c \"import secrets; print('SECRET_KEY=' + secrets.token_hex(32))\"")
        
        if any('DB_PASSWORD' in error for error in errors):
            print("  3. Set a secure database password:")
            print("     Edit .env and set DB_PASSWORD=your_secure_password")
        
        if any('MAIL_' in warning for warning in warnings):
            print("  4. Complete email configuration or remove mail settings")
    
    print(f"\nFor detailed setup instructions, see README.md")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())