#!/bin/bash

# NextCare Complete Setup Script
# This script sets up the entire NextCare application from scratch

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.8"
VENV_NAME="nextcare_env"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════╗"
echo "║       NextCare Setup Script          ║"
echo "║   Complete Application Installation   ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

# Function to print section headers
print_section() {
    echo -e "\n${CYAN}$1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

# Function to check prerequisites
check_prerequisites() {
    print_section "Checking Prerequisites"
    
    # Check Python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VER=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        echo -e "${GREEN}✓ Python3 found: $(python3 --version)${NC}"
        
        # Check if version is sufficient
        if [ "$(printf '%s\n' "$PYTHON_VERSION" "$PYTHON_VER" | sort -V | head -n1)" = "$PYTHON_VERSION" ]; then
            echo -e "${GREEN}✓ Python version is sufficient${NC}"
        else
            echo -e "${RED}✗ Python $PYTHON_VERSION or higher required, found $PYTHON_VER${NC}"
            exit 1
        fi
    else
        echo -e "${RED}✗ Python3 not found${NC}"
        echo "Please install Python 3.8 or higher"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ pip3 found${NC}"
    else
        echo -e "${RED}✗ pip3 not found${NC}"
        echo "Please install pip3"
        exit 1
    fi
    
    # Check PostgreSQL
    if command -v psql >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL client found${NC}"
    else
        echo -e "${RED}✗ PostgreSQL client not found${NC}"
        echo "Please install PostgreSQL"
        exit 1
    fi
    
    # Check if PostgreSQL is running
    if pg_isready >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL server is running${NC}"
    else
        echo -e "${YELLOW}⚠ PostgreSQL server not detected or not running${NC}"
        echo "Please ensure PostgreSQL is installed and running"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check Git
    if command -v git >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Git found${NC}"
    else
        echo -e "${YELLOW}⚠ Git not found (optional)${NC}"
    fi
}

# Function to create virtual environment
setup_virtual_environment() {
    print_section "Setting Up Python Virtual Environment"
    
    if [ -d "$VENV_NAME" ]; then
        echo -e "${YELLOW}Virtual environment '$VENV_NAME' already exists${NC}"
        read -p "Remove and recreate? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_NAME"
        else
            echo "Using existing virtual environment"
            return 0
        fi
    fi
    
    echo "Creating virtual environment '$VENV_NAME'..."
    python3 -m venv "$VENV_NAME"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    
    echo "Activating virtual environment..."
    source "$VENV_NAME/bin/activate"
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
    
    echo "Upgrading pip..."
    pip install --upgrade pip
    echo -e "${GREEN}✓ pip upgraded${NC}"
}

# Function to install dependencies
install_dependencies() {
    print_section "Installing Python Dependencies"
    
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}✗ requirements.txt not found${NC}"
        exit 1
    fi
    
    echo "Installing packages from requirements.txt..."
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
}

# Function to setup database
setup_database() {
    print_section "Setting Up Database"
    
    if [ -f "scripts/setup_database.sh" ]; then
        echo "Running database setup script..."
        bash scripts/setup_database.sh
    else
        echo -e "${YELLOW}Database setup script not found${NC}"
        echo "Please run database setup manually"
    fi
}

# Function to create necessary directories
create_directories() {
    print_section "Creating Application Directories"
    
    directories=("logs" "uploads" "backups" "temp")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            echo -e "${GREEN}✓ Created directory: $dir${NC}"
        else
            echo -e "${YELLOW}Directory already exists: $dir${NC}"
        fi
    done
}

# Function to setup environment file
setup_environment_file() {
    print_section "Setting Up Environment Configuration"
    
    if [ -f ".env" ]; then
        echo -e "${YELLOW}.env file already exists${NC}"
        read -p "Do you want to backup and recreate it? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
            echo -e "${GREEN}✓ Backed up existing .env file${NC}"
        else
            return 0
        fi
    fi
    
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo -e "${GREEN}✓ Created .env file from template${NC}"
        echo -e "${YELLOW}Please edit .env file to configure your settings${NC}"
    else
        echo -e "${YELLOW}.env.template not found, creating basic .env file${NC}"
        cat > .env << EOF
# NextCare Environment Configuration
FLASK_ENV=development
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "change-this-secret-key")
DEBUG=True

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nextcare
DB_USER=nextcare_user
DB_PASSWORD=

# Application Settings
ENABLE_MOCK_SENSORS=True
SENSOR_UPDATE_INTERVAL=60
EOF
        echo -e "${GREEN}✓ Created basic .env file${NC}"
    fi
}

# Function to run tests
run_tests() {
    print_section "Running Setup Tests"
    
    if [ -f "tests/test_setup.py" ]; then
        echo "Running setup verification tests..."
        python tests/test_setup.py
    else
        echo -e "${YELLOW}Setup test script not found${NC}"
        echo "Skipping tests"
    fi
}

# Function to display completion message
display_completion() {
    print_section "Setup Complete!"
    
    echo -e "${GREEN}"
    echo "🎉 NextCare setup completed successfully!"
    echo -e "${NC}"
    
    echo "Next steps:"
    echo "1. Review and edit the .env file:"
    echo "   nano .env"
    echo
    echo "2. Activate the virtual environment:"
    echo "   source $VENV_NAME/bin/activate"
    echo
    echo "3. Test the setup:"
    echo "   python tests/test_setup.py"
    echo
    echo "4. Start the application:"
    echo "   python app.py"
    echo
    
    if [ -f "database/sample_data.sql" ]; then
        echo "Default login credentials (if sample data was loaded):"
        echo "  Admin:    admin / admin123"
        echo "  Manager:  manager / manager123"
        echo "  Engineer: engineer / engineer123"
        echo
    fi
    
    echo "Documentation: README.md"
    echo "Configuration: .env"
    echo "Logs: logs/"
    echo
    echo -e "${CYAN}Happy monitoring with NextCare! 🏭📊${NC}"
}

# Function to handle cleanup on error
cleanup_on_error() {
    echo -e "\n${RED}Setup failed. Cleaning up...${NC}"
    if [ -d "$VENV_NAME" ] && [ -f "$VENV_NAME/pyvenv.cfg" ]; then
        read -p "Remove created virtual environment? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_NAME"
            echo "Virtual environment removed"
        fi
    fi
}

# Trap errors for cleanup
trap cleanup_on_error ERR

# Main execution
main() {
    check_prerequisites
    setup_virtual_environment
    install_dependencies
    create_directories
    setup_environment_file
    setup_database
    run_tests
    display_completion
}

# Run main function
main "$@"