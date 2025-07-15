@echo off
echo ========================================
echo FinGuard Rollback Schema Deployment
echo ========================================
echo.

echo Applying schema updates...
mysql -u root -p fin_guard < schema_updates_simple.sql

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Schema updates failed!
    echo Please check the error message above and fix any issues.
    echo.
    echo Alternative: Try running schema_updates_compatible.sql instead
    echo mysql -u root -p fin_guard ^< schema_updates_compatible.sql
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Schema updates completed successfully!
echo ========================================
echo.

echo Now applying PL/SQL optimizations...
mysql -u root -p fin_guard < PL_SQL_Optimizations.sql

if %errorlevel% neq 0 (
    echo.
    echo ERROR: PL/SQL optimizations failed!
    echo Please check the error message above and fix any issues.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Deployment completed successfully!
echo ========================================
echo.
echo All rollback functionality has been deployed:
echo   - Transaction backup system
echo   - Failed transaction logging
echo   - System audit logging
echo   - Enhanced stored procedures
echo   - Rollback management procedures
echo.
echo You can now access the rollback dashboard at:
echo   http://localhost:5000/rollback/dashboard
echo.
echo To test the rollback functionality:
echo   1. Run the Flask application: python run.py
echo   2. Login as admin
echo   3. Navigate to the rollback dashboard
echo   4. Test transaction status checking
echo.
pause
