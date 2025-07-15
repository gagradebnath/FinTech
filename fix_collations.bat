@echo off
echo ========================================
echo  FinGuard Collation Fix
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
echo Applying collation fixes to prevent charset conflicts...
mysql -u root -p fin_guard < fix_collations.sql

if %errorlevel% neq 0 (
    echo ERROR: Failed to apply collation fixes.
    pause
    exit /b 1
)

echo.
echo Verifying collation fixes...
mysql -u root -p fin_guard -e "SELECT table_name, column_name, collation_name FROM information_schema.columns WHERE table_schema='fin_guard' AND collation_name IS NOT NULL ORDER BY table_name;"

echo.
echo ========================================
echo  Collation fixes completed successfully!
echo ========================================
echo.
echo All tables now use utf8mb4_unicode_ci collation.
echo This should resolve the collation conflict errors.
echo.
pause
