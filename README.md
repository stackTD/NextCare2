# NextCare - Industrial Machine Monitoring System

NextCare is a comprehensive industrial machine monitoring and maintenance system built with Python and PostgreSQL. This system allows users to monitor machine parameters, configure alerts, and manage industrial equipment through an intuitive web dashboard.

## Table of Contents

- [Prerequisites](#prerequisites)
- [PostgreSQL Database Setup](#postgresql-database-setup)
- [Application Installation](#application-installation)
- [Configuration](#configuration)
- [Mock Sensor Setup](#mock-sensor-setup)
- [Running the Application](#running-the-application)
- [Database Management](#database-management)
- [Development Setup](#development-setup)
- [Troubleshooting](#troubleshooting)
- [Backup and Restore](#backup-and-restore)

## Prerequisites

Before setting up NextCare, ensure you have the following installed:

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Git
- pip (Python package manager)

## PostgreSQL Database Setup

### Installation

#### Windows

1. Download PostgreSQL from [official website](https://www.postgresql.org/download/windows/)
2. Run the installer and follow the setup wizard
3. During installation, remember the password you set for the `postgres` user
4. Add PostgreSQL bin directory to your PATH:
   ```cmd
   set PATH=%PATH%;C:\Program Files\PostgreSQL\15\bin
   ```

#### macOS

Using Homebrew:
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Add to PATH
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Using PostgreSQL.app:
1. Download from [postgresapp.com](https://postgresapp.com/)
2. Install and start the app
3. Add to PATH: `export PATH=$PATH:/Applications/Postgres.app/Contents/Versions/latest/bin`

#### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Linux (CentOS/RHEL/Fedora)

```bash
# For CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# For Fedora
sudo dnf install postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Database Creation and User Setup

1. **Access PostgreSQL as superuser:**

   ```bash
   # On Linux/macOS
   sudo -u postgres psql

   # On Windows (using Command Prompt as Administrator)
   psql -U postgres
   ```

2. **Create the NextCare database:**

   ```sql
   CREATE DATABASE nextcare;
   ```

3. **Create a dedicated user for NextCare:**

   ```sql
   CREATE USER nextcare_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE nextcare TO nextcare_user;
   ALTER USER nextcare_user CREATEDB;
   ```

4. **Exit PostgreSQL:**

   ```sql
   \q
   ```

### Verify Database Connection

Test the connection with the new user:

```bash
psql -h localhost -U nextcare_user -d nextcare
```

## Application Installation

### 1. Clone the Repository

```bash
git clone https://github.com/stackTD/NextCare2.git
cd NextCare2
```

### 2. Create Virtual Environment

#### Windows

```cmd
# Create virtual environment
python -m venv nextcare_env

# Activate virtual environment
nextcare_env\Scripts\activate
```

#### macOS/Linux

```bash
# Create virtual environment
python3 -m venv nextcare_env

# Activate virtual environment
source nextcare_env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database Schema

```bash
# Run database setup script
psql -h localhost -U nextcare_user -d nextcare -f database/setup.sql

# Create tables
psql -h localhost -U nextcare_user -d nextcare -f database/schema.sql

# Insert sample data
psql -h localhost -U nextcare_user -d nextcare -f database/sample_data.sql
```

## Configuration

### Database Configuration

1. **Create environment file:**

   Create a `.env` file in the project root:

   ```env
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=nextcare
   DB_USER=nextcare_user
   DB_PASSWORD=your_secure_password

   # Application Configuration
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   FLASK_ENV=development

   # Mock Sensor Configuration
   ENABLE_MOCK_SENSORS=True
   SENSOR_UPDATE_INTERVAL=5
   ```

2. **Configure database connection:**

   Update `config/database_config.py` with your database settings if needed.

### Environment Variables

For production deployments, set these environment variables:

```bash
export DB_HOST="your_db_host"
export DB_PORT="5432"
export DB_NAME="nextcare"
export DB_USER="nextcare_user"
export DB_PASSWORD="your_secure_password"
export SECRET_KEY="your_production_secret_key"
export DEBUG="False"
export FLASK_ENV="production"
```

## Mock Sensor Setup

NextCare includes mock sensors for testing and development purposes.

### Enable Mock Sensors

1. **Set environment variable:**
   ```bash
   export ENABLE_MOCK_SENSORS=True
   ```

2. **Configure sensor parameters:**
   
   Mock sensors simulate the following machine parameters:
   - Temperature (°C)
   - Pressure (PSI)
   - Vibration (Hz)
   - Speed (RPM)
   - Power Consumption (kW)

3. **Customize sensor behavior:**
   
   Edit `sensors/mock_sensors.py` to modify:
   - Update intervals
   - Value ranges
   - Alarm thresholds
   - Number of virtual machines

### Mock Sensor Configuration

```python
# Example configuration in sensors/mock_sensors.py
MOCK_MACHINES = {
    'machine_001': {
        'name': 'Production Line A',
        'parameters': {
            'temperature': {'min': 20, 'max': 80, 'alarm_high': 75},
            'pressure': {'min': 10, 'max': 50, 'alarm_high': 45},
            'vibration': {'min': 0, 'max': 10, 'alarm_high': 8},
        }
    }
}
```

## Running the Application

### Development Mode

```bash
# Activate virtual environment
source nextcare_env/bin/activate  # On Windows: nextcare_env\Scripts\activate

# Start the application
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode

```bash
# Set production environment
export FLASK_ENV=production
export DEBUG=False

# Use a production WSGI server (e.g., Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Default Login Credentials

After running the sample data script, use these credentials to log in:

- **Admin User:**
  - Username: `admin`
  - Password: `admin123`

- **Manager User:**
  - Username: `manager`
  - Password: `manager123`

- **Engineer User:**
  - Username: `engineer`
  - Password: `engineer123`

## Database Management

### Database Schema Overview

The NextCare database includes the following main tables:

- `users` - User authentication and roles
- `machines` - Machine registry and metadata
- `parameters` - Parameter definitions and thresholds
- `machine_parameters` - Association between machines and parameters
- `sensor_data` - Time-series sensor readings
- `alerts` - System alerts and notifications
- `maintenance_logs` - Maintenance history

### Adding New Machines

```sql
-- Add a new machine
INSERT INTO machines (machine_id, name, description, location, status)
VALUES ('MACHINE_004', 'Packaging Unit B', 'Secondary packaging line', 'Floor 2', 'active');

-- Add parameters to the machine
INSERT INTO machine_parameters (machine_id, parameter_id, min_value, max_value, alarm_threshold)
VALUES 
    ('MACHINE_004', 'temperature', 15.0, 85.0, 80.0),
    ('MACHINE_004', 'pressure', 5.0, 55.0, 50.0);
```

### Viewing Data

```sql
-- View all machines
SELECT * FROM machines;

-- View recent sensor data
SELECT m.name, p.name, sd.value, sd.timestamp
FROM sensor_data sd
JOIN machines m ON sd.machine_id = m.machine_id
JOIN parameters p ON sd.parameter_id = p.parameter_id
ORDER BY sd.timestamp DESC
LIMIT 20;

-- View active alerts
SELECT a.alert_id, m.name, a.message, a.severity, a.created_at
FROM alerts a
JOIN machines m ON a.machine_id = m.machine_id
WHERE a.status = 'active'
ORDER BY a.created_at DESC;
```

## Development Setup

### IDE Configuration

#### Visual Studio Code

1. Install recommended extensions:
   - Python
   - PostgreSQL
   - GitLens
   - Python Docstring Generator

2. Create `.vscode/settings.json`:
   ```json
   {
       "python.defaultInterpreterPath": "./nextcare_env/bin/python",
       "python.linting.enabled": true,
       "python.linting.pylintEnabled": true,
       "python.formatting.provider": "black"
   }
   ```

#### PyCharm

1. Open the project directory
2. Configure interpreter: File → Settings → Project → Python Interpreter
3. Add the virtual environment: Add → Existing Environment → Select `nextcare_env/bin/python`

### Code Style and Linting

```bash
# Install development dependencies
pip install black pylint pytest pytest-cov

# Format code
black .

# Lint code
pylint app.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=.
```

### Testing Procedures

1. **Unit Tests:**
   ```bash
   # Run all tests
   pytest tests/

   # Run specific test file
   pytest tests/test_database.py

   # Run with verbose output
   pytest -v
   ```

2. **Integration Tests:**
   ```bash
   # Test database connectivity
   python tests/test_db_connection.py

   # Test API endpoints
   pytest tests/test_api.py
   ```

3. **Load Testing:**
   ```bash
   # Install load testing tools
   pip install locust

   # Run load tests
   locust -f tests/load_test.py
   ```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Error:** `psql: FATAL: password authentication failed`

**Solution:**
```bash
# Reset PostgreSQL password
sudo -u postgres psql
ALTER USER postgres PASSWORD 'newpassword';
\q

# Update pg_hba.conf for local connections
sudo nano /etc/postgresql/15/main/pg_hba.conf
# Change 'peer' to 'md5' for local connections
# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### 2. Permission Denied Errors

**Error:** `permission denied for database nextcare`

**Solution:**
```sql
-- Connect as postgres superuser
sudo -u postgres psql

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE nextcare TO nextcare_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nextcare_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nextcare_user;
```

#### 3. Python Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'psycopg2'`

**Solution:**
```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# On Ubuntu/Debian, you might need:
sudo apt-get install python3-dev libpq-dev

# On CentOS/RHEL:
sudo yum install python3-devel postgresql-devel
```

#### 4. Port Already in Use

**Error:** `Address already in use: Port 5000`

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>

# Or use a different port
export FLASK_PORT=5001
python app.py
```

#### 5. Virtual Environment Issues

**Error:** `command not found: python`

**Solution:**
```bash
# Ensure virtual environment is activated
source nextcare_env/bin/activate

# Verify Python installation
which python
python --version

# Reinstall virtual environment if needed
rm -rf nextcare_env
python3 -m venv nextcare_env
source nextcare_env/bin/activate
pip install -r requirements.txt
```

### Log File Locations

- **Application Logs:** `logs/nextcare.log`
- **PostgreSQL Logs:** 
  - Linux: `/var/log/postgresql/`
  - macOS: `/usr/local/var/log/`
  - Windows: `C:\Program Files\PostgreSQL\15\data\log\`

### Debug Mode

Enable debug mode for detailed error messages:

```bash
export DEBUG=True
export FLASK_ENV=development
python app.py
```

## Backup and Restore

### Database Backup

#### Create Backup

```bash
# Full database backup
pg_dump -h localhost -U nextcare_user nextcare > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
pg_dump -h localhost -U nextcare_user -Fc nextcare > backup_$(date +%Y%m%d_%H%M%S).dump

# Schema only backup
pg_dump -h localhost -U nextcare_user -s nextcare > schema_backup.sql

# Data only backup
pg_dump -h localhost -U nextcare_user -a nextcare > data_backup.sql
```

#### Automated Backup Script

Create `scripts/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/nextcare_backup_$DATE.sql"

pg_dump -h localhost -U nextcare_user nextcare > "$BACKUP_FILE"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "nextcare_backup_*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

Set up cron job for daily backups:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/scripts/backup.sh
```

### Database Restore

#### Restore from SQL Backup

```bash
# Drop and recreate database
sudo -u postgres psql
DROP DATABASE nextcare;
CREATE DATABASE nextcare;
GRANT ALL PRIVILEGES ON DATABASE nextcare TO nextcare_user;
\q

# Restore from backup
psql -h localhost -U nextcare_user nextcare < backup_20231201_020000.sql
```

#### Restore from Custom Format

```bash
# Restore from .dump file
pg_restore -h localhost -U nextcare_user -d nextcare backup_20231201_020000.dump

# Restore with options
pg_restore -h localhost -U nextcare_user -d nextcare -c -v backup_20231201_020000.dump
```

### File System Backup

```bash
# Create application backup (excluding virtual environment)
tar -czf nextcare_app_backup_$(date +%Y%m%d).tar.gz \
    --exclude='nextcare_env' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    .
```

## Contributing

Please read our contributing guidelines before submitting pull requests:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue on GitHub
- Check the troubleshooting section above
- Review the documentation

## Version History

- **v1.0.0** - Initial release with basic monitoring capabilities
- **v1.1.0** - Added mock sensor support and improved UI
- **v1.2.0** - Enhanced database schema and alerting system