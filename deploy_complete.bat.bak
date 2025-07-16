@echo off
echo ========================================
echo  FinGuard Complete PL/SQL Deployment
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
echo Deploying comprehensive FinGuard PL/SQL optimizations...
echo This includes:
echo - Schema utilities
echo - Transaction procedures
echo - Rollback functionality
echo - Analysis functions
echo - Triggers and views
echo.

mysql -u root -p fin_guard < FinGuard_Complete_PL_SQL.sql

if %errorlevel% neq 0 (
    echo ERROR: Failed to deploy PL/SQL optimizations.
    pause
    exit /b 1
)

echo.
echo Verifying deployment...
mysql -u root -p fin_guard -e "SHOW PROCEDURE STATUS WHERE Db='fin_guard';"

echo.
echo Checking functions...
mysql -u root -p fin_guard -e "SHOW FUNCTION STATUS WHERE Db='fin_guard';"

echo.
echo Checking views...
mysql -u root -p fin_guard -e "SHOW FULL TABLES WHERE Table_Type = 'VIEW';"

echo.
echo Checking triggers...
mysql -u root -p fin_guard -e "SHOW TRIGGERS;"

echo.
echo ========================================
echo  Complete PL/SQL Deployment Successful!
echo ========================================
echo.
echo Available Features:
echo.
echo PROCEDURES:
echo - ProcessMoneyTransferEnhanced: Enhanced money transfer with rollback
echo - RollbackTransaction: Rollback completed transactions
echo - GetTransactionStatus: Check transaction status and rollback eligibility
echo - BackupUserBalance: Create user balance backups
echo - RestoreUserBalance: Restore user balance from backup
echo - AutoRollbackFailedTransactions: Auto-rollback failed transactions
echo - CleanupOldFraudReports: Clean up old fraud reports
echo.
echo FUNCTIONS:
echo - GetUserRiskScore: Calculate user risk score
echo - GetUserDailySpending: Get daily spending amount
echo - IsWithinSpendingLimit: Check spending limits
echo - GetUserTransactionCount: Get transaction count for period
echo.
echo VIEWS:
echo - v_transaction_analytics: Transaction analysis view
echo - v_user_risk_analysis: User risk analysis view
echo - v_rollback_monitoring: Rollback monitoring view
echo.
echo TRIGGERS:
echo - tr_transaction_balance_update: Auto-update balances
echo - tr_fraud_report_audit: Audit fraud reports
echo - tr_user_update_audit: Audit user updates
echo.
echo The FinGuard application now has complete PL/SQL optimization!
echo.
pause
