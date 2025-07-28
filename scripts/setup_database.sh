#!/bin/bash

# NextCare Database Setup Script for Linux/macOS
# This script automates the PostgreSQL database setup process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DB_NAME="${DB_NAME:-nextcare}"
DB_USER="${DB_USER:-nextcare_user}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

echo -e "${BLUE}NextCare Database Setup Script${NC}"
echo "=================================="

# Function to check if PostgreSQL is running
check_postgresql() {
    if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" > /dev/null 2>&1; then
        echo -e "${RED}Error: PostgreSQL is not running or not accessible${NC}"
        echo "Please ensure PostgreSQL is installed and running."
        
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "Try: sudo systemctl start postgresql"
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            echo "Try: brew services start postgresql"
        fi
        exit 1
    fi
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
}

# Function to get database password
get_password() {
    if [ -z "$DB_PASSWORD" ]; then
        echo -n "Enter password for PostgreSQL user '$DB_USER': "
        read -s DB_PASSWORD
        echo
        
        if [ -z "$DB_PASSWORD" ]; then
            echo -e "${RED}Error: Password cannot be empty${NC}"
            exit 1
        fi
    fi
}

# Function to check if database exists
database_exists() {
    psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"
}

# Function to check if user exists
user_exists() {
    psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -t -c "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1
}

# Function to create database user
create_user() {
    echo "Creating database user '$DB_USER'..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
    psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "ALTER USER $DB_USER CREATEDB;"
    echo -e "${GREEN}✓ User '$DB_USER' created${NC}"
}

# Function to create database
create_database() {
    echo "Creating database '$DB_NAME'..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "CREATE DATABASE $DB_NAME;"
    psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    echo -e "${GREEN}✓ Database '$DB_NAME' created${NC}"
}

# Function to run SQL scripts
run_sql_scripts() {
    echo "Setting up database schema..."
    
    # Run setup script
    if [ -f "database/setup.sql" ]; then
        echo "Running setup.sql..."
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f database/setup.sql
        echo -e "${GREEN}✓ Setup script completed${NC}"
    fi
    
    # Run schema script
    if [ -f "database/schema.sql" ]; then
        echo "Running schema.sql..."
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f database/schema.sql
        echo -e "${GREEN}✓ Schema created${NC}"
    fi
    
    # Run sample data script
    if [ -f "database/sample_data.sql" ]; then
        read -p "Do you want to load sample data? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Running sample_data.sql..."
            PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f database/sample_data.sql
            echo -e "${GREEN}✓ Sample data loaded${NC}"
        fi
    fi
}

# Function to test database connection
test_connection() {
    echo "Testing database connection..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 'NextCare database connection successful!' as status;"
    echo -e "${GREEN}✓ Database connection test passed${NC}"
}

# Function to create .env file
create_env_file() {
    if [ ! -f ".env" ]; then
        read -p "Create .env file with database configuration? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cat > .env << EOF
# NextCare Environment Configuration
# Database Configuration
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# Application Configuration
FLASK_ENV=development
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=True

# Mock Sensor Configuration
ENABLE_MOCK_SENSORS=True
SENSOR_UPDATE_INTERVAL=60
EOF
            echo -e "${GREEN}✓ .env file created${NC}"
            echo -e "${YELLOW}Note: Please review and modify .env file as needed${NC}"
        fi
    else
        echo -e "${YELLOW}Note: .env file already exists${NC}"
    fi
}

# Main execution
main() {
    echo "Starting database setup..."
    echo "Database: $DB_NAME"
    echo "User: $DB_USER"
    echo "Host: $DB_HOST:$DB_PORT"
    echo

    # Check prerequisites
    check_postgresql
    get_password

    # Create user if it doesn't exist
    if user_exists; then
        echo -e "${YELLOW}User '$DB_USER' already exists${NC}"
    else
        create_user
    fi

    # Create database if it doesn't exist
    if database_exists; then
        echo -e "${YELLOW}Database '$DB_NAME' already exists${NC}"
        read -p "Do you want to continue with existing database? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Setup cancelled."
            exit 0
        fi
    else
        create_database
    fi

    # Run SQL scripts
    run_sql_scripts

    # Test connection
    test_connection

    # Create .env file
    create_env_file

    echo
    echo -e "${GREEN}Database setup completed successfully!${NC}"
    echo
    echo "Next steps:"
    echo "1. Create and activate a Python virtual environment"
    echo "2. Install dependencies: pip install -r requirements.txt"
    echo "3. Start the NextCare application"
    echo
    echo "Default login credentials (if sample data was loaded):"
    echo "  Admin: admin / admin123"
    echo "  Manager: manager / manager123"
    echo "  Engineer: engineer / engineer123"
}

# Run main function
main "$@"