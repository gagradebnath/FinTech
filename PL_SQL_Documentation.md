# FinGuard PL/SQL Optimizations Documentation

## 📋 **Overview**

This document provides comprehensive documentation for all stored procedures, functions, triggers, and views implemented in the FinGuard application. The PL/SQL optimizations provide advanced transaction processing, rollback functionality, fraud detection, and analytics capabilities.

## 🗂️ **File Structure**

- **`FinGuard_Complete_PL_SQL.sql`**: Complete PL/SQL implementation
- **`deploy_complete.bat`**: Deployment script for all PL/SQL features
- **`fix_collations.sql`**: Database collation fixes
- **`DatabaseSchema_MySQL.sql`**: Base database schema

## � **Database Views**

### 1. **v_daily_transaction_analytics**
**Purpose**: Daily transaction analytics and metrics

**Columns**:
- `transaction_date`: Date of transactions
- `total_transactions`: Total number of transactions
- `total_volume`: Total transaction volume
- `avg_transaction_amount`: Average transaction amount
- `min_transaction`: Minimum transaction amount
- `max_transaction`: Maximum transaction amount
- `unique_senders`: Number of unique senders
- `unique_receivers`: Number of unique receivers
- `transfers`: Number of transfer transactions
- `deposits`: Number of deposit transactions
- `withdrawals`: Number of withdrawal transactions

**Usage Example**:
```sql
SELECT * FROM v_daily_transaction_analytics 
WHERE transaction_date >= DATE_SUB(NOW(), INTERVAL 7 DAY);
```

### 2. **v_high_risk_users**
**Purpose**: View of users with high risk scores

**Columns**:
- `id`: User ID
- `first_name`: User's first name
- `last_name`: User's last name
- `balance`: Current account balance
- `risk_score`: Calculated risk score
- `fraud_reports`: Number of fraud reports
- `weekly_velocity`: Weekly transaction velocity
- `account_age_days`: Account age in days

**Usage Example**:
```sql
SELECT * FROM v_high_risk_users 
WHERE risk_score > 50 
ORDER BY risk_score DESC;
```

### 3. **v_monthly_transaction_report**
**Purpose**: Monthly transaction reporting with cumulative data

**Columns**:
- `year`: Transaction year
- `month`: Transaction month
- `transaction_count`: Monthly transaction count
- `total_volume`: Monthly total volume
- `avg_amount`: Monthly average amount
- `cumulative_transactions`: Cumulative transaction count
- `cumulative_volume`: Cumulative volume

**Usage Example**:
```sql
SELECT * FROM v_monthly_transaction_report 
WHERE year = YEAR(NOW()) 
ORDER BY month DESC;
```

### 4. **v_user_transaction_summary**
**Purpose**: Summary of user transaction activity

**Columns**:
- `id`: User ID
- `first_name`: User's first name
- `last_name`: User's last name
- `balance`: Current balance
- `transactions_sent`: Number of sent transactions
- `transactions_received`: Number of received transactions
- `total_sent`: Total amount sent
- `total_received`: Total amount received
- `last_transaction_date`: Date of last transaction
- `risk_score`: User's risk score

**Usage Example**:
```sql
SELECT * FROM v_user_transaction_summary 
WHERE balance > 1000 
ORDER BY total_sent DESC;
```

## 📦 **Stored Procedures**

### 1. **ProcessMoneyTransfer**
**Purpose**: Process money transfers with comprehensive validation

**Parameters**:
- `IN p_sender_id CHAR(36)`: Sender user ID
- `IN p_receiver_id CHAR(36)`: Receiver user ID  
- `IN p_amount DECIMAL(10,2)`: Transfer amount
- `IN p_payment_method VARCHAR(100)`: Payment method
- `IN p_note TEXT`: Transaction note
- `IN p_tx_type ENUM('Transfer', 'Deposit', 'Withdrawal', 'Payment', 'Refund')`: Transaction type
- `IN p_location VARCHAR(255)`: Transaction location
- `OUT p_success BOOLEAN`: Success status
- `OUT p_message VARCHAR(500)`: Result message
- `OUT p_transaction_id CHAR(36)`: Generated transaction ID

**Functionality**:
- ✅ Validates transaction parameters
- ✅ Checks user existence and balances
- ✅ Fraud detection for receiver
- ✅ Updates user balances atomically
- ✅ Comprehensive error handling
- ✅ Transaction record creation

**Usage Example**:
```sql
CALL ProcessMoneyTransfer(
    'sender-uuid', 'receiver-uuid', 100.00, 'Bank Transfer', 
    'Payment for services', 'Transfer', 'New York', 
    @success, @message, @transaction_id
);
```

### 2. **RollbackTransaction**
**Purpose**: Rollback a completed transaction by restoring original balances from backup data

**Parameters**:
- `IN p_transaction_id CHAR(36)`: Transaction ID to rollback
- `IN p_reason TEXT`: Reason for rollback
- `OUT p_success BOOLEAN`: Success status
- `OUT p_message VARCHAR(500)`: Result message

**Functionality**:
- ✅ Validates transaction exists and is completed
- ✅ Checks for existing backup data
- ✅ Restores original balances from backup
- ✅ Updates transaction status to 'ROLLED_BACK'
- ✅ Creates audit log entries
- ✅ Comprehensive error handling

**Usage Example**:
```sql
CALL RollbackTransaction('transaction-uuid', 'Fraud detected', @success, @message);
```

### 3. **RegisterUser**
**Purpose**: Register new users with comprehensive validation

**Parameters**:
- `IN p_role_name VARCHAR(50)`: User role name
- `IN p_first_name VARCHAR(255)`: First name
- `IN p_last_name VARCHAR(255)`: Last name
- `IN p_dob DATE`: Date of birth
- `IN p_age INT`: Age
- `IN p_gender VARCHAR(50)`: Gender
- `IN p_marital_status VARCHAR(50)`: Marital status
- `IN p_blood_group VARCHAR(10)`: Blood group
- `IN p_email VARCHAR(255)`: Email address
- `IN p_phone VARCHAR(20)`: Phone number
- `IN p_password VARCHAR(255)`: Password hash
- `OUT p_user_id CHAR(36)`: Generated user ID
- `OUT p_success BOOLEAN`: Success status
- `OUT p_message VARCHAR(500)`: Result message

**Usage Example**:
```sql
CALL RegisterUser('user', 'John', 'Doe', '1990-01-01', 30, 'Male', 'Single', 'O+', 
    'john@example.com', '1234567890', 'hashed_password', @user_id, @success, @message);
```

### 4. **ProcessFraudReport**
**Purpose**: Process fraud reports with risk assessment

**Parameters**:
- `IN p_reporter_id CHAR(36)`: Reporter user ID
- `IN p_reported_user_id CHAR(36)`: Reported user ID
- `IN p_reason VARCHAR(500)`: Fraud report reason
- `OUT p_success BOOLEAN`: Success status
- `OUT p_message VARCHAR(500)`: Result message

**Functionality**:
- ✅ Validates reporter and reported users exist
- ✅ Prevents duplicate reports
- ✅ Creates fraud report record
- ✅ Calculates risk score
- ✅ Auto-suspends high-risk users
- ✅ Audit trail creation

**Usage Example**:
```sql
CALL ProcessFraudReport('reporter-uuid', 'reported-uuid', 'Suspicious activity', @success, @message);
```

### 5. **GetUserDashboardData**
**Purpose**: Retrieve comprehensive user dashboard data

**Parameters**:
- `IN p_user_id CHAR(36)`: User ID
- `OUT p_current_balance DECIMAL(10,2)`: Current balance
- `OUT p_total_sent DECIMAL(15,2)`: Total amount sent
- `OUT p_total_received DECIMAL(15,2)`: Total amount received
- `OUT p_transaction_count INT`: Total transaction count
- `OUT p_risk_score DECIMAL(5,2)`: User risk score

**Usage Example**:
```sql
CALL GetUserDashboardData('user-uuid', @balance, @sent, @received, @count, @risk);
```

### 6. **GetUserTransactionHistory**
**Purpose**: Retrieve paginated user transaction history

**Parameters**:
- `IN p_user_id CHAR(36)`: User ID
- `IN p_limit INT`: Number of records to return
- `IN p_offset INT`: Starting offset

**Usage Example**:
```sql
CALL GetUserTransactionHistory('user-uuid', 10, 0);
```

### 7. **CalculateUserStatistics**
**Purpose**: Calculate comprehensive user statistics

**Parameters**:
- `IN p_user_id CHAR(36)`: User ID
- `OUT p_total_sent DECIMAL(15,2)`: Total sent amount
- `OUT p_total_received DECIMAL(15,2)`: Total received amount
- `OUT p_transaction_count INT`: Transaction count
- `OUT p_avg_transaction DECIMAL(10,2)`: Average transaction amount
- `OUT p_last_transaction_date DATETIME`: Last transaction date

**Usage Example**:
```sql
CALL CalculateUserStatistics('user-uuid', @sent, @received, @count, @avg, @last_date);
```

### 8. **AdminBatchBalanceUpdate**
**Purpose**: Admin batch balance updates

**Parameters**:
- `IN p_admin_id CHAR(36)`: Admin user ID
- `IN p_user_ids TEXT`: Comma-separated user IDs
- `IN p_amounts TEXT`: Comma-separated amounts
- `IN p_reason TEXT`: Update reason
- `OUT p_success BOOLEAN`: Success status
- `OUT p_message VARCHAR(500)`: Result message
- `OUT p_updated_count INT`: Number of updated users

**Usage Example**:
```sql
CALL AdminBatchBalanceUpdate('admin-uuid', 'user1,user2', '100.00,200.00', 'Bonus', @success, @message, @count);
```

### 9. **BulkBalanceUpdate**
**Purpose**: Bulk balance updates with validation

**Parameters**:
- `IN p_admin_id CHAR(36)`: Admin user ID
- `IN p_user_ids TEXT`: Comma-separated user IDs
- `IN p_amounts TEXT`: Comma-separated amounts
- `IN p_reason TEXT`: Update reason
- `OUT p_success BOOLEAN`: Success status
- `OUT p_message VARCHAR(500)`: Result message

**Usage Example**:
```sql
CALL BulkBalanceUpdate('admin-uuid', 'user1,user2', '100.00,200.00', 'Adjustment', @success, @message);
```

### 10. **CreateFullBudget**
**Purpose**: Create comprehensive budgets

**Parameters**:
- `IN p_user_id CHAR(36)`: User ID
- `IN p_budget_name VARCHAR(255)`: Budget name
- `IN p_currency VARCHAR(10)`: Currency code
- `IN p_income_sources TEXT`: Income sources
- `IN p_total_income DECIMAL(15,2)`: Total income
- `IN p_expenses_json TEXT`: Expenses JSON data
- `OUT p_budget_id CHAR(36)`: Generated budget ID
- `OUT p_success BOOLEAN`: Success status
- `OUT p_message VARCHAR(500)`: Result message

**Usage Example**:
```sql
CALL CreateFullBudget('user-uuid', 'Monthly Budget', 'USD', 'Salary', 5000.00, '{}', @budget_id, @success, @message);
```

### 11. **SaveOrUpdateBudget**
**Purpose**: Save or update user budgets

**Parameters**:
- `IN p_user_id CHAR(36)`: User ID
- `IN p_name VARCHAR(255)`: Budget name
- `IN p_currency VARCHAR(10)`: Currency
- `IN p_income_source VARCHAR(255)`: Income source
- `IN p_amount DECIMAL(15,2)`: Budget amount
- `OUT p_budget_id CHAR(36)`: Budget ID
- `OUT p_success BOOLEAN`: Success status
- `OUT p_message VARCHAR(500)`: Result message

**Usage Example**:
```sql
CALL SaveOrUpdateBudget('user-uuid', 'Monthly Budget', 'USD', 'Salary', 5000.00, @budget_id, @success, @message);
```

### 12. **AddColumnIfNotExists**
**Purpose**: Safely add columns to tables

**Parameters**:
- `IN p_table_name VARCHAR(64)`: Table name
- `IN p_column_name VARCHAR(64)`: Column name
- `IN p_column_definition TEXT`: Column definition

**Usage Example**:
```sql
CALL AddColumnIfNotExists('users', 'new_column', 'VARCHAR(100) DEFAULT NULL');
```

### 13. **SafeAddColumn**
**Purpose**: Safe column addition with error handling

**Parameters**:
- `IN table_name VARCHAR(128)`: Table name
- `IN column_name VARCHAR(128)`: Column name
- `IN column_definition TEXT`: Column definition

**Usage Example**:
```sql
CALL SafeAddColumn('users', 'status', 'VARCHAR(50) DEFAULT "active"');
```

### 14. **SafeAddIndex**
**Purpose**: Safe index addition with error handling

**Parameters**:
- `IN table_name VARCHAR(128)`: Table name
- `IN index_name VARCHAR(128)`: Index name
- `IN index_definition TEXT`: Index definition

**Usage Example**:
```sql
CALL SafeAddIndex('transactions', 'idx_timestamp', '(timestamp)');
```

## 🔧 **Functions**

### 1. **GetUserRiskScore**
**Purpose**: Calculate user risk score based on multiple factors

**Parameters**:
- `p_user_id CHAR(36)`: User ID

**Returns**: `DECIMAL(5,2)` - Risk score (0-100)

**Functionality**:
- ✅ Fraud reports factor (30 points per report)
- ✅ High-amount transactions factor (10 points per transaction)
- ✅ Account age adjustment (older accounts get lower scores)
- ✅ Maximum score capped at 100

**Usage Example**:
```sql
SELECT GetUserRiskScore('user-uuid') as risk_score;
```

### 2. **CalculateAccountAge**
**Purpose**: Calculate account age in days

**Parameters**:
- `p_user_id CHAR(36)`: User ID

**Returns**: `INT` - Account age in days

**Usage Example**:
```sql
SELECT CalculateAccountAge('user-uuid') as account_age;
```

### 3. **CalculateTransactionVelocity**
**Purpose**: Calculate transaction velocity over specified period

**Parameters**:
- `p_user_id CHAR(36)`: User ID
- `p_days INT`: Number of days to calculate velocity for

**Returns**: `DECIMAL(10,2)` - Transactions per day

**Usage Example**:
```sql
SELECT CalculateTransactionVelocity('user-uuid', 7) as weekly_velocity;
```

## 🎯 **Triggers**

### 1. **tr_transactions_blockchain**
**Purpose**: Automatically create blockchain entries for new transactions

**Trigger Type**: AFTER INSERT on `transactions`

**Functionality**:
- ✅ Calculates next blockchain index
- ✅ Retrieves previous block hash
- ✅ Generates new block hash using SHA256
- ✅ Inserts blockchain record with transaction reference

**Blockchain Hash Generation**:
```sql
SHA2(CONCAT(index, transaction_id, amount, timestamp, previous_hash), 256)
```

### 2. **tr_balance_validation**
**Purpose**: Validate balance constraints before updates

**Trigger Type**: BEFORE UPDATE on `users`

**Functionality**:
- ✅ Prevents negative balance updates
- ✅ Skips admin_logs to avoid foreign key issues
- ✅ Raises error for invalid balance changes

## 🔐 **Security Features**

### Transaction Security
- **Atomic Operations**: All transactions use START TRANSACTION/COMMIT/ROLLBACK
- **Input Validation**: Comprehensive parameter validation
- **Fraud Detection**: Real-time fraud checking before transfers
- **Balance Validation**: Prevents negative balances and insufficient funds
- **Audit Trail**: Complete audit logging for all operations

### User Security
- **Duplicate Prevention**: Email/phone uniqueness validation
- **Risk Assessment**: Automated risk scoring and monitoring
- **Auto-Suspension**: High-risk users automatically suspended
- **Password Security**: Secure password storage and validation

### Admin Security
- **Batch Operations**: Secure batch balance updates
- **Admin Logging**: Complete admin action audit trail
- **Permission Validation**: Role-based access control
- **Error Handling**: Comprehensive error handling and logging

## 📈 **Performance Optimizations**

### Indexing Strategy
- **Primary Keys**: All tables have optimized primary keys
- **Foreign Keys**: Proper foreign key relationships
- **Query Optimization**: Indexes on frequently queried columns
- **Compound Indexes**: Multi-column indexes for complex queries

### Query Optimization
- **Prepared Statements**: Dynamic SQL with prepared statements
- **Batch Operations**: Efficient batch processing
- **View Optimization**: Materialized views for complex analytics
- **Connection Pooling**: Efficient database connection management

## 🚀 **Deployment Guidelines**

### Prerequisites
- MySQL 8.0 or higher
- InnoDB storage engine
- UTF8MB4 character set support
- Sufficient privileges for stored procedures/functions

### Deployment Steps
1. **Run Base Schema**: Execute `DatabaseSchema_MySQL.sql`
2. **Deploy PL/SQL**: Run `FinGuard_Complete_PL_SQL.sql`
3. **Fix Collations**: Execute `fix_collations.sql`
4. **Verify Deployment**: Run test procedures
5. **Seed Data**: Execute `database_seed.py`

### Verification Commands
```sql
-- Check procedures
SHOW PROCEDURE STATUS WHERE Name LIKE '%Transfer%';

-- Check functions
SHOW FUNCTION STATUS WHERE Name LIKE '%Risk%';

-- Check triggers
SHOW TRIGGERS;

-- Check views
SHOW FULL TABLES WHERE Table_Type = 'VIEW';
```

## 🔍 **Monitoring and Maintenance**

### Performance Monitoring
- **Slow Query Log**: Monitor procedure execution times
- **Index Usage**: Track index utilization
- **Transaction Volume**: Monitor transaction throughput
- **Error Rates**: Track procedure success/failure rates

### Maintenance Tasks
- **Statistics Update**: Regular table statistics updates
- **Index Maintenance**: Periodic index optimization
- **Log Rotation**: Audit log cleanup and archival
- **Backup Strategy**: Regular backup of procedures and data

## 📊 **Analytics and Reporting**

### Built-in Analytics Views
- **Daily Analytics**: `v_daily_transaction_analytics`
- **Monthly Reports**: `v_monthly_transaction_report`
- **User Summaries**: `v_user_transaction_summary`
- **Risk Assessment**: `v_high_risk_users`

### Custom Analytics
- **Risk Scoring**: Advanced risk calculation algorithms
- **Transaction Velocity**: Real-time velocity calculations
- **Account Age Analysis**: Account maturity assessments
- **Fraud Pattern Detection**: Pattern-based fraud detection

## 🛡️ **Error Handling and Recovery**

### Error Categories
- **Validation Errors**: Input parameter validation
- **Business Logic Errors**: Business rule violations
- **Database Errors**: SQL execution errors
- **System Errors**: Infrastructure-related errors

### Recovery Procedures
- **Transaction Rollback**: Automatic rollback on errors
- **Balance Restoration**: Backup-based balance recovery
- **Audit Trail**: Complete error audit logging
- **Alert System**: Error notification and alerting

## 🎯 **Best Practices**

### Development
- **Code Reviews**: Peer review all stored procedures
- **Testing**: Comprehensive unit and integration testing
- **Documentation**: Maintain up-to-date documentation
- **Version Control**: Track all database changes

### Operations
- **Monitoring**: Real-time performance monitoring
- **Backup**: Regular backup and recovery testing
- **Security**: Regular security audits and updates
- **Performance**: Ongoing performance optimization

## 📋 **Troubleshooting Guide**

### Common Issues
1. **Foreign Key Constraints**: Check referential integrity
2. **Duplicate Key Errors**: Verify unique constraints
3. **Timeout Issues**: Optimize query performance
4. **Permission Errors**: Verify user privileges

### Debug Procedures
```sql
-- Check procedure status
SHOW PROCEDURE STATUS WHERE Name = 'ProcedureName';

-- View procedure definition
SHOW CREATE PROCEDURE ProcedureName;

-- Check for locks
SHOW PROCESSLIST;

-- Monitor performance
SELECT * FROM performance_schema.events_statements_summary_by_digest 
WHERE DIGEST_TEXT LIKE '%ProcedureName%';
```

## 🔄 **Version History**

### Version 1.0
- Initial stored procedure implementation
- Basic transaction processing
- User registration and authentication

### Version 2.0
- Enhanced fraud detection
- Rollback functionality
- Advanced analytics views
- Blockchain integration

### Version 3.0
- Batch operations
- Performance optimizations
- Enhanced security features
- Comprehensive error handling

---

## 📞 **Support and Contact**

For technical support or questions regarding the PL/SQL implementation:

- **Development Team**: FinGuard Development Team
- **Documentation**: This file and inline code comments
- **Testing**: Comprehensive test suite available
- **Deployment**: Automated deployment scripts provided

---

**Last Updated**: July 2025  
**Version**: 3.0  
**Status**: Production Ready

**Parameters**:
- `IN p_transaction_id CHAR(36)`: Transaction ID to rollback
- `IN p_reason TEXT`: Reason for rollback
- `OUT p_success BOOLEAN`: Success status
- `OUT p_message VARCHAR(500)`: Result message

**Functionality**:
- ✅ Validates transaction exists and is eligible
- ✅ Restores original balances from backup
- ✅ Updates transaction status to 'ROLLED_BACK'
- ✅ Creates audit log entry
- ✅ 72-hour rollback window enforcement

**Usage Example**:
```sql
CALL RollbackTransaction('transaction-uuid', 'Customer request', @success, @message);
```

### 3. **GetTransactionStatus**
**Purpose**: Check transaction status and rollback eligibility

**Parameters**:
- `IN p_transaction_id CHAR(36)`: Transaction ID
- `OUT p_status VARCHAR(20)`: Current transaction status
- `OUT p_can_rollback BOOLEAN`: Rollback eligibility
- `OUT p_message VARCHAR(500)`: Status message

**Functionality**:
- ✅ Checks transaction existence
- ✅ Validates rollback eligibility
- ✅ Calculates time since transaction
- ✅ Checks backup data availability

**Usage Example**:
```sql
CALL GetTransactionStatus('transaction-uuid', @status, @can_rollback, @message);
```

### 4. **BackupUserBalance**
**Purpose**: Create a backup of user balance before operations

**Parameters**:
- `IN p_user_id CHAR(36)`: User ID
- `IN p_operation_type VARCHAR(50)`: Operation description
- `OUT p_backup_id CHAR(36)`: Generated backup ID
- `OUT p_success BOOLEAN`: Success status
- `OUT p_message VARCHAR(500)`: Result message

**Functionality**:
- ✅ Creates balance snapshot
- ✅ Generates unique backup ID
- ✅ Audit logging
- ✅ Error handling

**Usage Example**:
```sql
CALL BackupUserBalance('user-uuid', 'Manual backup', @backup_id, @success, @message);
```

### 5. **RestoreUserBalance**
**Purpose**: Restore user balance from a backup

**Parameters**:
- `IN p_backup_id CHAR(36)`: Backup ID
- `IN p_reason TEXT`: Restore reason
- `OUT p_success BOOLEAN`: Success status
- `OUT p_message VARCHAR(500)`: Result message

**Functionality**:
- ✅ Validates backup existence
- ✅ Restores balance from backup
- ✅ Updates audit log
- ✅ Timestamps restore operation

**Usage Example**:
```sql
CALL RestoreUserBalance('backup-uuid', 'System error recovery', @success, @message);
```

### 6. **AutoRollbackFailedTransactions**
**Purpose**: Automatically rollback failed transactions older than threshold

**Parameters**:
- `IN p_hours_threshold INT`: Age threshold in hours (default: 24)
- `OUT p_rolled_back_count INT`: Number of transactions rolled back
- `OUT p_message VARCHAR(500)`: Operation summary

**Functionality**:
- ✅ Finds failed transactions older than threshold
- ✅ Attempts rollback for each transaction
- ✅ Counts successful rollbacks
- ✅ System audit logging

**Usage Example**:
```sql
CALL AutoRollbackFailedTransactions(24, @count, @message);
```

### 7. **CleanupOldFraudReports**
**Purpose**: Clean up fraud reports older than specified days

**Parameters**:
- `IN p_days_threshold INT`: Age threshold in days (default: 90)

**Functionality**:
- ✅ Deletes old fraud reports
- ✅ Logs cleanup operation
- ✅ Returns deletion count

**Usage Example**:
```sql
CALL CleanupOldFraudReports(90);
```

## 🔧 **Functions**

### 1. **GetUserRiskScore**
**Purpose**: Calculate user risk score based on fraud reports and transaction patterns

**Parameters**:
- `p_user_id CHAR(36)`: User ID

**Returns**: `DECIMAL(5,2)` - Risk score (0-100)

**Calculation**:
- Fraud reports against user: 25 points each
- High transaction volume (>50/month): 15 points
- High-value transactions (>$1000/week): 10 points each
- Maximum score: 100

**Usage Example**:
```sql
SELECT GetUserRiskScore('user-uuid') as risk_score;
```

### 2. **GetUserDailySpending**
**Purpose**: Calculate user's total spending for current day

**Parameters**:
- `p_user_id CHAR(36)`: User ID

**Returns**: `DECIMAL(10,2)` - Daily spending amount

**Usage Example**:
```sql
SELECT GetUserDailySpending('user-uuid') as daily_spending;
```

### 3. **IsWithinSpendingLimit**
**Purpose**: Check if user is within daily spending limit

**Parameters**:
- `p_user_id CHAR(36)`: User ID
- `p_amount DECIMAL(10,2)`: Transaction amount

**Returns**: `BOOLEAN` - True if within limit

**Default Limit**: $10,000 per day

**Usage Example**:
```sql
SELECT IsWithinSpendingLimit('user-uuid', 500.00) as within_limit;
```

### 4. **GetUserTransactionCount**
**Purpose**: Get transaction count for user in specified period

**Parameters**:
- `p_user_id CHAR(36)`: User ID
- `p_days INT`: Number of days to look back

**Returns**: `INT` - Transaction count

**Usage Example**:
```sql
SELECT GetUserTransactionCount('user-uuid', 30) as monthly_transactions;
```

## 👁️ **Views**

### 1. **v_transaction_analytics**
**Purpose**: Comprehensive transaction analysis view

**Columns**:
- Transaction details (ID, amount, method, timestamp, type, status)
- User information (sender/receiver names)
- Risk scores for both parties
- Backup and rollback information

**Usage Example**:
```sql
SELECT * FROM v_transaction_analytics WHERE amount > 1000;
```

### 2. **v_user_risk_analysis**
**Purpose**: User risk and spending analysis view

**Columns**:
- User details (ID, name, balance)
- Risk score
- Daily spending
- Transaction counts (weekly/monthly)
- Fraud report statistics

**Usage Example**:
```sql
SELECT * FROM v_user_risk_analysis WHERE risk_score > 50;
```

### 3. **v_rollback_monitoring**
**Purpose**: Rollback eligibility monitoring view

**Columns**:
- Transaction details
- Backup information
- Rollback status and timestamps
- Hours since transaction
- Rollback eligibility status

**Usage Example**:
```sql
SELECT * FROM v_rollback_monitoring WHERE rollback_status = 'ELIGIBLE';
```

## 🔔 **Triggers**

### 1. **tr_transaction_balance_update**
**Purpose**: Auto-update balances and create audit logs on transaction insert

**Trigger Type**: AFTER INSERT ON transactions

**Functionality**:
- ✅ Logs completed transactions
- ✅ Creates audit trail
- ✅ Handles transaction status updates

### 2. **tr_fraud_report_audit**
**Purpose**: Audit fraud report submissions

**Trigger Type**: AFTER INSERT ON fraud_list

**Functionality**:
- ✅ Logs fraud report creation
- ✅ Records reporter and reported user
- ✅ Timestamps fraud reports

### 3. **tr_user_update_audit**
**Purpose**: Audit user account changes, especially balance updates

**Trigger Type**: AFTER UPDATE ON users

**Functionality**:
- ✅ Logs balance changes
- ✅ Records old and new values
- ✅ Timestamps user updates

## 📊 **Database Tables**

### **transaction_backups**
Stores backup data for rollback functionality
- `backup_id`: Unique backup identifier
- `original_transaction_id`: Reference to original transaction
- `sender_id`, `receiver_id`: User IDs
- `sender_balance_before/after`: Balance snapshots
- `rollback_timestamp`: When rollback occurred
- `rollback_reason`: Reason for rollback

### **failed_transactions**
Logs failed transaction attempts
- `id`: Unique failure record ID
- `attempted_transaction_id`: Failed transaction ID
- `failure_reason`: Reason for failure
- `retry_count`: Number of retry attempts

### **system_audit_log**
Comprehensive audit logging
- `id`: Unique audit record ID
- `operation_type`: Type of operation
- `entity_type`: Type of entity affected
- `old_values/new_values`: Change tracking
- `timestamp`: When operation occurred
- `success`: Whether operation succeeded

## 🚀 **Deployment Instructions**

1. **Complete Deployment**:
   ```bash
   deploy_complete.bat
   ```

2. **Fix Collation Issues** (if needed):
   ```bash
   fix_collations.bat
   ```

3. **Manual Deployment**:
   ```bash
   mysql -u root -p fin_guard < FinGuard_Complete_PL_SQL.sql
   ```

## 🔍 **Performance Considerations**

- **Indexes**: Optimized indexes on frequently queried columns
- **Transactions**: Atomic operations with proper rollback handling
- **Locks**: Row-level locking for concurrent access
- **Audit**: Efficient audit logging without performance impact

## 🛡️ **Security Features**

- **Fraud Detection**: Real-time fraud checking
- **Risk Assessment**: Continuous risk scoring
- **Audit Trail**: Complete operation logging
- **Rollback Window**: 72-hour rollback limitation
- **Balance Validation**: Insufficient balance prevention

## 📈 **Monitoring and Analytics**

- **Real-time Risk Scoring**: Continuous user risk assessment
- **Transaction Analytics**: Comprehensive transaction insights
- **Rollback Monitoring**: Track rollback eligibility and usage
- **Fraud Reporting**: Automated fraud detection and reporting

## 🎯 **Best Practices**

1. **Always use procedures** for money transfers
2. **Check rollback eligibility** before attempting rollbacks
3. **Monitor risk scores** regularly
4. **Clean up old data** using cleanup procedures
5. **Review audit logs** for security monitoring

## 🆘 **Troubleshooting**

### **Common Issues**
- **Collation errors**: Run `fix_collations.bat`
- **Procedure not found**: Redeploy using `deploy_complete.bat`
- **Transaction rollback failed**: Check backup data exists
- **Risk score calculation errors**: Verify fraud_list table data

### **Support Commands**
```sql
-- Check procedures
SHOW PROCEDURE STATUS WHERE Db='fin_guard';

-- Check functions
SHOW FUNCTION STATUS WHERE Db='fin_guard';

-- Check triggers
SHOW TRIGGERS;

-- Check views
SHOW FULL TABLES WHERE Table_Type = 'VIEW';
```

## 📝 **Version History**

- **v1.0**: Initial PL/SQL implementation
- **v1.1**: Added rollback functionality
- **v1.2**: Enhanced fraud detection
- **v1.3**: Comprehensive audit logging
- **v2.0**: Complete consolidation and optimization

---

*This documentation covers all PL/SQL features implemented in the FinGuard application. For additional support, refer to the main README.md file.*
