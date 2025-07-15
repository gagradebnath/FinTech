@echo off
echo ========================================
echo  FinGuard Database Setup Check
echo ========================================
echo.

echo Checking MySQL connection...
mysql -u root -p -e "SELECT 'MySQL connection successful' as status;"

if %errorlevel% neq 0 (
    echo ERROR: Could not connect to MySQL. Please check your connection settings.
    pause
    exit /b 1
)

echo.
echo Checking for databases...
echo Please choose your database:
echo 1. fin_guard
echo 2. finguard
echo 3. Create new database
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    set DB_NAME=fin_guard
    echo Using database: fin_guard
) else if "%choice%"=="2" (
    set DB_NAME=finguard
    echo Using database: finguard
) else if "%choice%"=="3" (
    set /p DB_NAME="Enter new database name: "
    echo Creating database: %DB_NAME%
    mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS %DB_NAME%;"
) else (
    echo Invalid choice. Exiting...
    pause
    exit /b 1
)

echo.
echo Checking if database exists...
mysql -u root -p -e "USE %DB_NAME%; SELECT 'Database exists' as status;"

if %errorlevel% neq 0 (
    echo ERROR: Database %DB_NAME% does not exist or cannot be accessed.
    echo Creating database...
    mysql -u root -p -e "CREATE DATABASE %DB_NAME%;"
    
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create database.
        pause
        exit /b 1
    )
)

echo.
echo Database %DB_NAME% is ready!
echo.
echo Now run one of these deployment scripts:
echo - deploy_mysql57.bat (for MySQL 5.7+ compatibility)
echo - deploy_rollback.bat (for newer MySQL versions)
echo.
echo Make sure to update the database name in the deployment scripts if needed.
echo.
pause
