@echo off
echo ========================================
echo  FinGuard MySQL 5.7 Compatible Deployment
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
echo Step 1: Deploying schema updates (if not already done)...
mysql -u root -p fin_guard < schema_updates_simple.sql

if %errorlevel% neq 0 (
    echo WARNING: Schema updates failed or already exist. Continuing...
)

echo.
echo Step 2: Deploying MySQL 5.7 Compatible PL/SQL optimizations...
mysql -u root -p fin_guard < PL_SQL_Optimizations_MySQL57.sql

if %errorlevel% neq 0 (
    echo ERROR: Failed to deploy MySQL 5.7 compatible optimizations.
    pause
    exit /b 1
)

echo.
echo Step 3: Verifying deployment...
mysql -u root -p fin_guard -e "SHOW PROCEDURE STATUS WHERE Db='fin_guard';"

echo.
echo ========================================
echo  Deployment completed successfully!
echo ========================================
echo.
echo Available procedures:
echo - ProcessMoneyTransferEnhanced
echo - RollbackTransaction
echo - GetTransactionStatus
echo - BackupUserBalance
echo - RestoreUserBalance
echo - AutoRollbackFailedTransactions
echo.
echo Available functions:
echo - GetUserRiskScore
echo.
echo You can now use the rollback functionality in your FinGuard application.
echo.
pause
