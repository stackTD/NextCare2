@echo off
REM NextCare Database Setup Script for Windows
REM This script automates the PostgreSQL database setup process

setlocal enabledelayedexpansion

REM Configuration
set "DB_NAME=nextcare"
set "DB_USER=nextcare_user"
set "DB_HOST=localhost"
set "DB_PORT=5432"

echo NextCare Database Setup Script
echo ==================================
echo.

REM Check if PostgreSQL is accessible
echo Checking PostgreSQL connection...
pg_isready -h %DB_HOST% -p %DB_PORT% >nul 2>&1
if errorlevel 1 (
    echo Error: PostgreSQL is not running or not accessible
    echo Please ensure PostgreSQL is installed and running.
    echo You may need to start the PostgreSQL service.
    pause
    exit /b 1
)
echo ✓ PostgreSQL is running

REM Get database password
if "%DB_PASSWORD%"=="" (
    set /p "DB_PASSWORD=Enter password for PostgreSQL user '%DB_USER%': "
    if "!DB_PASSWORD!"=="" (
        echo Error: Password cannot be empty
        pause
        exit /b 1
    )
)

echo.
echo Database: %DB_NAME%
echo User: %DB_USER%
echo Host: %DB_HOST%:%DB_PORT%
echo.

REM Check if user exists
echo Checking if user exists...
psql -h %DB_HOST% -p %DB_PORT% -U postgres -t -c "SELECT 1 FROM pg_roles WHERE rolname='%DB_USER%'" | findstr "1" >nul
if errorlevel 1 (
    echo Creating database user '%DB_USER%'...
    psql -h %DB_HOST% -p %DB_PORT% -U postgres -c "CREATE USER %DB_USER% WITH PASSWORD '%DB_PASSWORD%';"
    psql -h %DB_HOST% -p %DB_PORT% -U postgres -c "ALTER USER %DB_USER% CREATEDB;"
    echo ✓ User '%DB_USER%' created
) else (
    echo User '%DB_USER%' already exists
)

REM Check if database exists
echo Checking if database exists...
psql -h %DB_HOST% -p %DB_PORT% -U postgres -lqt | findstr "%DB_NAME%" >nul
if errorlevel 1 (
    echo Creating database '%DB_NAME%'...
    psql -h %DB_HOST% -p %DB_PORT% -U postgres -c "CREATE DATABASE %DB_NAME%;"
    psql -h %DB_HOST% -p %DB_PORT% -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;"
    echo ✓ Database '%DB_NAME%' created
) else (
    echo Database '%DB_NAME%' already exists
    set /p "continue=Do you want to continue with existing database? (y/n): "
    if /i not "!continue!"=="y" (
        echo Setup cancelled.
        pause
        exit /b 0
    )
)

REM Set password for subsequent commands
set "PGPASSWORD=%DB_PASSWORD%"

REM Run setup script
if exist "database\setup.sql" (
    echo Running setup.sql...
    psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f database\setup.sql
    echo ✓ Setup script completed
)

REM Run schema script
if exist "database\schema.sql" (
    echo Running schema.sql...
    psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f database\schema.sql
    echo ✓ Schema created
)

REM Run sample data script
if exist "database\sample_data.sql" (
    set /p "loaddata=Do you want to load sample data? (y/n): "
    if /i "!loaddata!"=="y" (
        echo Running sample_data.sql...
        psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f database\sample_data.sql
        echo ✓ Sample data loaded
    )
)

REM Test database connection
echo Testing database connection...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -c "SELECT 'NextCare database connection successful!' as status;"
echo ✓ Database connection test passed

REM Create .env file
if not exist ".env" (
    set /p "createenv=Create .env file with database configuration? (y/n): "
    if /i "!createenv!"=="y" (
        (
        echo # NextCare Environment Configuration
        echo # Database Configuration
        echo DB_HOST=%DB_HOST%
        echo DB_PORT=%DB_PORT%
        echo DB_NAME=%DB_NAME%
        echo DB_USER=%DB_USER%
        echo DB_PASSWORD=%DB_PASSWORD%
        echo.
        echo # Application Configuration
        echo FLASK_ENV=development
        echo SECRET_KEY=your-secret-key-here
        echo DEBUG=True
        echo.
        echo # Mock Sensor Configuration
        echo ENABLE_MOCK_SENSORS=True
        echo SENSOR_UPDATE_INTERVAL=60
        ) > .env
        echo ✓ .env file created
        echo Note: Please review and modify .env file as needed
    )
) else (
    echo Note: .env file already exists
)

echo.
echo Database setup completed successfully!
echo.
echo Next steps:
echo 1. Create and activate a Python virtual environment:
echo    python -m venv nextcare_env
echo    nextcare_env\Scripts\activate
echo 2. Install dependencies: pip install -r requirements.txt
echo 3. Start the NextCare application
echo.
echo Default login credentials (if sample data was loaded):
echo   Admin: admin / admin123
echo   Manager: manager / manager123
echo   Engineer: engineer / engineer123
echo.
pause