#!/bin/bash

# NextCare Database Backup Script
# This script creates backups of the NextCare database

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Load environment variables if .env exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-nextcare}"
DB_USER="${DB_USER:-nextcare_user}"
BACKUP_DIR="${BACKUP_DIR:-backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo -e "${BLUE}NextCare Database Backup${NC}"
echo "=========================="
echo "Database: $DB_NAME"
echo "Host: $DB_HOST:$DB_PORT"
echo "User: $DB_USER"
echo "Backup Directory: $BACKUP_DIR"
echo

# Generate backup filename with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/nextcare_backup_$TIMESTAMP.sql"
COMPRESSED_FILE="$BACKUP_FILE.gz"

# Function to create SQL backup
create_sql_backup() {
    echo "Creating SQL backup..."
    
    if [ -z "$DB_PASSWORD" ]; then
        echo -n "Enter database password: "
        read -s DB_PASSWORD
        echo
    fi
    
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-password \
        --clean \
        --if-exists \
        --create \
        --format=plain \
        > "$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ SQL backup created: $BACKUP_FILE${NC}"
        
        # Compress backup
        gzip "$BACKUP_FILE"
        echo -e "${GREEN}✓ Backup compressed: $COMPRESSED_FILE${NC}"
        
        # Display backup size
        BACKUP_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
        echo "Backup size: $BACKUP_SIZE"
    else
        echo -e "${RED}✗ Backup failed${NC}"
        exit 1
    fi
}

# Function to create custom format backup
create_custom_backup() {
    echo "Creating custom format backup..."
    
    CUSTOM_FILE="$BACKUP_DIR/nextcare_backup_$TIMESTAMP.dump"
    
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-password \
        --clean \
        --if-exists \
        --create \
        --format=custom \
        --compress=9 \
        --file="$CUSTOM_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Custom backup created: $CUSTOM_FILE${NC}"
        
        BACKUP_SIZE=$(du -h "$CUSTOM_FILE" | cut -f1)
        echo "Backup size: $BACKUP_SIZE"
    else
        echo -e "${RED}✗ Custom backup failed${NC}"
    fi
}

# Function to clean old backups
cleanup_old_backups() {
    echo -e "\nCleaning up old backups (older than $RETENTION_DAYS days)..."
    
    DELETED_COUNT=0
    while IFS= read -r -d '' file; do
        rm "$file"
        echo "Deleted: $(basename "$file")"
        ((DELETED_COUNT++))
    done < <(find "$BACKUP_DIR" -name "nextcare_backup_*.sql.gz" -mtime +$RETENTION_DAYS -print0)
    
    while IFS= read -r -d '' file; do
        rm "$file"
        echo "Deleted: $(basename "$file")"
        ((DELETED_COUNT++))
    done < <(find "$BACKUP_DIR" -name "nextcare_backup_*.dump" -mtime +$RETENTION_DAYS -print0)
    
    if [ $DELETED_COUNT -eq 0 ]; then
        echo "No old backups to delete"
    else
        echo -e "${GREEN}✓ Deleted $DELETED_COUNT old backup(s)${NC}"
    fi
}

# Function to test database connection
test_connection() {
    echo "Testing database connection..."
    
    if [ -z "$DB_PASSWORD" ]; then
        echo -n "Enter database password: "
        read -s DB_PASSWORD
        echo
    fi
    
    PGPASSWORD="$DB_PASSWORD" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "SELECT 'Connection successful' as status;" \
        > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Database connection successful${NC}"
        return 0
    else
        echo -e "${RED}✗ Database connection failed${NC}"
        return 1
    fi
}

# Function to display backup statistics
show_backup_stats() {
    echo -e "\nBackup Statistics:"
    echo "=================="
    
    if [ -d "$BACKUP_DIR" ]; then
        TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "nextcare_backup_*" | wc -l)
        TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
        
        echo "Total backups: $TOTAL_BACKUPS"
        echo "Total size: $TOTAL_SIZE"
        
        if [ $TOTAL_BACKUPS -gt 0 ]; then
            echo -e "\nRecent backups:"
            find "$BACKUP_DIR" -name "nextcare_backup_*" -type f | sort | tail -5 | while read file; do
                SIZE=$(du -h "$file" | cut -f1)
                DATE=$(stat -c %y "$file" | cut -d. -f1)
                echo "  $(basename "$file") - $SIZE - $DATE"
            done
        fi
    else
        echo "Backup directory does not exist"
    fi
}

# Main function
main() {
    case "${1:-full}" in
        "test")
            test_connection
            ;;
        "stats")
            show_backup_stats
            ;;
        "cleanup")
            cleanup_old_backups
            ;;
        "sql")
            test_connection && create_sql_backup && cleanup_old_backups
            ;;
        "custom")
            test_connection && create_custom_backup && cleanup_old_backups
            ;;
        "full"|*)
            test_connection && create_sql_backup && create_custom_backup && cleanup_old_backups
            ;;
    esac
}

# Help message
show_help() {
    echo "NextCare Database Backup Script"
    echo "Usage: $0 [option]"
    echo
    echo "Options:"
    echo "  full     Create both SQL and custom format backups (default)"
    echo "  sql      Create SQL format backup only"
    echo "  custom   Create custom format backup only"
    echo "  test     Test database connection"
    echo "  stats    Show backup statistics"
    echo "  cleanup  Clean up old backups only"
    echo "  help     Show this help message"
    echo
    echo "Environment variables:"
    echo "  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD"
    echo "  BACKUP_DIR, BACKUP_RETENTION_DAYS"
}

# Handle command line arguments
if [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# Run main function
main "$1"

echo -e "\n${GREEN}Backup process completed!${NC}"