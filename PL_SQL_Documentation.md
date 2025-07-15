# FinGuard PL/SQL Optimizations Documentation

## 📋 **Overview**

This document provides comprehensive documentation for all stored procedures, functions, triggers, and views implemented in the FinGuard application. The PL/SQL optimizations provide advanced transaction processing, rollback functionality, fraud detection, and analytics capabilities.

## 🗂️ **File Structure**

- **`FinGuard_Complete_PL_SQL.sql`**: Complete PL/SQL implementation
- **`deploy_complete.bat`**: Deployment script for all PL/SQL features
- **`fix_collations.sql`**: Database collation fixes
- **`DatabaseSchema_MySQL.sql`**: Base database schema

## 📦 **Stored Procedures**

### 1. **ProcessMoneyTransferEnhanced**
**Purpose**: Enhanced money transfer with fraud detection and rollback support

**Parameters**:
- `IN p_sender_id CHAR(36)`: Sender user ID
- `IN p_receiver_id CHAR(36)`: Receiver user ID  
- `IN p_amount DECIMAL(10,2)`: Transfer amount
- `IN p_payment_method VARCHAR(100)`: Payment method
- `IN p_note TEXT`: Transaction note
- `IN p_tx_type VARCHAR(20)`: Transaction type
- `IN p_location VARCHAR(255)`: Transaction location
- `OUT p_success BOOLEAN`: Success status
- `OUT p_message VARCHAR(500)`: Result message
- `OUT p_transaction_id CHAR(36)`: Generated transaction ID

**Functionality**:
- ✅ Validates transaction parameters
- ✅ Checks user existence and balances
- ✅ Fraud detection for receiver
- ✅ Creates automatic backup before transfer
- ✅ Updates user balances atomically
- ✅ Comprehensive error handling and logging
- ✅ Audit trail generation

**Usage Example**:
```sql
CALL ProcessMoneyTransferEnhanced(
    'sender-uuid', 'receiver-uuid', 100.00, 'Bank Transfer', 
    'Payment for services', 'Transfer', 'New York', 
    @success, @message, @transaction_id
);
```

### 2. **RollbackTransaction**
**Purpose**: Rollback a completed transaction by restoring original balances

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
