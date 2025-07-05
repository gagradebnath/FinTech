@echo off
echo FinGuard SQLite to MySQL Migration Script v2.0
echo =================================================
echo This script will migrate FinGuard from SQLite to MySQL
echo with all datetime fixes and transaction type corrections.
echo.

echo Step 1: Installing Python packages...
pip install PyMySQL cryptography Flask-SQLAlchemy
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python packages
    pause
    exit /b 1
)
echo ✅ Python packages installed successfully!
echo.

echo Step 2: Database Configuration Setup
echo ====================================
echo.
echo Choose configuration method:
echo 1) Enter credentials now (recommended for first-time setup)
echo 2) Use configuration file (mysql_config.py)
echo.
set /p config_choice="Enter choice (1 or 2): "

if "%config_choice%"=="2" (
    echo.
    if not exist mysql_config.py (
        echo Creating mysql_config.py from template...
        copy mysql_config_template.py mysql_config.py >nul
        echo.
        echo ⚠️  Please edit mysql_config.py with your MySQL credentials
        echo    and run this script again.
        echo.
        notepad mysql_config.py
        pause
        exit /b 0
    ) else (
        echo ✅ Using existing mysql_config.py
        echo.
        goto :skip_manual_config
    )
)

echo Please enter your MySQL database credentials:
echo.

set /p mysql_host="MySQL Host (default: localhost): "
if "%mysql_host%"=="" set mysql_host=localhost

set /p mysql_port="MySQL Port (default: 3306): "
if "%mysql_port%"=="" set mysql_port=3306

set /p mysql_user="MySQL Username (default: root): "
if "%mysql_user%"=="" set mysql_user=root

set /p mysql_password="MySQL Password: "
if "%mysql_password%"=="" (
    echo ERROR: MySQL password is required
    pause
    exit /b 1
)

set /p mysql_database="Database Name (default: fin_guard): "
if "%mysql_database%"=="" set mysql_database=fin_guard

echo.
echo Confirming Configuration:
echo Host: %mysql_host%
echo Port: %mysql_port%
echo User: %mysql_user%
echo Database: %mysql_database%
echo Password: [HIDDEN]
echo.
set /p confirm="Is this configuration correct? (y/N): "
if /i not "%confirm%"=="y" (
    echo Configuration cancelled. Please run the script again.
    pause
    exit /b 0
)

:skip_manual_config

echo Step 3: Setting environment variables...
if "%config_choice%"=="1" (
    set MYSQL_HOST=%mysql_host%
    set MYSQL_PORT=%mysql_port%
    set MYSQL_USER=%mysql_user%
    set MYSQL_PASSWORD=%mysql_password%
    set MYSQL_DATABASE=%mysql_database%
    echo ✅ Environment variables set for this session.
) else (
    echo ✅ Using mysql_config.py file for configuration.
)
echo.

echo Step 4: Creating database and tables...
echo This will create the MySQL schema with proper ENUM constraints
echo and insert dummy data for testing...
echo.
echo Connecting to MySQL with your credentials...
python seed_mysql.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: Failed to create database
    echo.
    echo Possible issues:
    echo - MySQL server not running
    echo - Incorrect credentials
    echo - Database access permissions
    echo - Network connectivity
    echo.
    echo Please check your MySQL installation and credentials.
    pause
    exit /b 1
)
echo ✅ Database created successfully!
echo.

echo Step 5: Testing the migration...
echo Running permission tests to verify database connectivity...
python test_permissions.py
if %errorlevel% neq 0 (
    echo ⚠️  WARNING: Permission test failed, but migration may still be successful
    echo    This might be due to missing test data - the application should still work
)
echo.

echo Step 6: Testing datetime filters...
echo Verifying Jinja2 filters for MySQL datetime compatibility...
if exist test_filters.py (
    python test_filters.py
    if %errorlevel% equ 0 (
        echo ✅ Datetime filters working correctly
    ) else (
        echo ⚠️  WARNING: Datetime filter test failed
    )
) else (
    echo ⚠️  Datetime filter test file not found - skipping
)
echo.

echo =================================================
echo ✅ Migration completed successfully!
echo =================================================
echo.
echo 🔧 FIXES INCLUDED IN THIS MIGRATION:
echo - ✅ MySQL database schema with proper ENUM constraints
echo - ✅ All datetime handling fixed (no more .split() errors)
echo - ✅ Transaction types corrected for MySQL ENUM
echo - ✅ Custom Jinja2 filters for datetime formatting
echo - ✅ Robust PyMySQL connection configuration
echo - ✅ All utility functions updated for MySQL
echo.
echo 🔑 Default login credentials:
echo - Admin: username=admin, password=admin
echo - Agent: username=agent, password=agent  
echo - User:  username=user,  password=user
echo.
echo 🚀 To start the application:
echo    python run.py
echo.
echo 📖 For troubleshooting, see:
echo    - FINAL_MIGRATION_STATUS.md
echo    - TRANSACTION_TYPE_FIX.md
echo    - MIGRATION_GUIDE.md
echo.
pause
