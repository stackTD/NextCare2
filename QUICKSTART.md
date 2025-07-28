# NextCare Quick Start Guide

This guide will get you up and running with NextCare in under 10 minutes.

## Prerequisites

Before starting, ensure you have:
- Python 3.8+ installed
- PostgreSQL 12+ installed and running
- Git (optional, for cloning)

## Quick Setup

### 1. Download/Clone the Project

```bash
# If using Git
git clone https://github.com/stackTD/NextCare2.git
cd NextCare2

# Or download and extract the ZIP file
```

### 2. Run the Automated Setup

**Linux/macOS:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Windows:**
```cmd
scripts\setup_database.bat
```

The setup script will:
- Create a Python virtual environment
- Install all dependencies
- Set up the PostgreSQL database
- Create sample data
- Test the installation

### 3. Configure Your Environment

Edit the `.env` file created during setup:

```bash
nano .env  # or use your preferred editor
```

Key settings to update:
- `DB_PASSWORD`: Your PostgreSQL password
- `SECRET_KEY`: Change for production
- `ENABLE_MOCK_SENSORS`: Set to `True` for demo

### 4. Start NextCare

```bash
# Activate virtual environment
source nextcare_env/bin/activate  # Linux/macOS
# OR
nextcare_env\Scripts\activate     # Windows

# Test the setup
python tests/test_setup.py

# Start the application
python app.py
```

### 5. Access the Application

Open your browser and go to: http://localhost:5000

**Default Login Credentials:**
- Admin: `admin` / `admin123`
- Manager: `manager` / `manager123`
- Engineer: `engineer` / `engineer123`

## Manual Setup (Alternative)

If the automated setup doesn't work, follow these manual steps:

### 1. Create Virtual Environment

```bash
python3 -m venv nextcare_env
source nextcare_env/bin/activate  # Linux/macOS
# OR
nextcare_env\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Database

```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql

-- Create database and user
CREATE DATABASE nextcare;
CREATE USER nextcare_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE nextcare TO nextcare_user;
\q
```

```bash
# Run database scripts
psql -h localhost -U nextcare_user -d nextcare -f database/setup.sql
psql -h localhost -U nextcare_user -d nextcare -f database/schema.sql
psql -h localhost -U nextcare_user -d nextcare -f database/sample_data.sql
```

### 4. Create Environment File

Copy `.env.template` to `.env` and update with your settings.

## Troubleshooting

### Common Issues

**Database Connection Failed:**
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Check credentials in `.env` file
- Verify database exists: `psql -l`

**Python Module Errors:**
- Activate virtual environment: `source nextcare_env/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Permission Denied:**
- Make scripts executable: `chmod +x scripts/*.sh`
- Check file permissions: `ls -la`

### Getting Help

1. Check the full README.md for detailed documentation
2. Run setup verification: `python tests/test_setup.py`
3. Check logs in the `logs/` directory
4. Review configuration in `.env` file

## What's Next?

After successful setup:

1. **Explore the Dashboard**: Navigate through machines, parameters, and alerts
2. **Monitor Sensors**: Watch real-time mock sensor data
3. **Configure Alerts**: Set up custom alert thresholds
4. **Add Machines**: Define your own equipment monitoring
5. **Customize**: Modify mock sensors or add real sensor integration

## Production Deployment

For production use:

1. Set `FLASK_ENV=production` in `.env`
2. Change `SECRET_KEY` to a secure random value
3. Use a production WSGI server: `gunicorn -w 4 app:app`
4. Set up proper SSL/TLS certificates
5. Configure email notifications
6. Set up automated backups: `./scripts/backup.sh`

## Architecture Overview

NextCare consists of:

- **Web Application**: Flask-based dashboard
- **Database**: PostgreSQL with comprehensive schema
- **Mock Sensors**: Python-based sensor simulation
- **Configuration**: Environment-based settings
- **Monitoring**: Real-time data collection and alerting

## File Structure

```
NextCare2/
├── README.md              # Complete documentation
├── QUICKSTART.md          # This quick start guide
├── requirements.txt       # Python dependencies
├── .env.template         # Environment configuration template
├── config/               # Application configuration
├── database/             # SQL scripts and schema
├── sensors/              # Mock sensor system
├── scripts/              # Setup and maintenance scripts
├── tests/                # Test and verification scripts
└── logs/                 # Application logs
```

---

**🎉 Congratulations! You now have NextCare running.**

For detailed documentation, see [README.md](README.md).
For questions or issues, check the troubleshooting section.