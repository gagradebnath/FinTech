# FinGuard Rollback Functionality

## Overview

This document describes the comprehensive rollback functionality added to the FinGuard fintech application. The rollback system provides transaction safety, data recovery, and audit capabilities to ensure data integrity and prevent financial losses.

## Features

### 1. Transaction Rollback
- **Manual Rollback**: Admins can manually rollback completed transactions
- **Auto-Rollback**: Automatically rollback failed transactions after a specified time threshold
- **Status Checking**: Check if a transaction can be rolled back before attempting rollback
- **Reason Tracking**: All rollbacks include a reason for audit purposes

### 2. Data Backup and Recovery
- **Transaction Backups**: Automatic backup of user balances before each transaction
- **User Balance Backup**: Manual backup of individual user balances
- **Balance Restoration**: Restore user balances from backups
- **Backup Verification**: Verify backup integrity before restoration

### 3. Audit and Monitoring
- **System Audit Log**: Comprehensive logging of all rollback operations
- **Failed Transaction Log**: Track all failed transactions with reasons
- **Transaction Status Tracking**: Monitor transaction states (PENDING, COMPLETED, FAILED, ROLLED_BACK)
- **Real-time Monitoring**: Dashboard for monitoring rollback operations

### 4. Safety Mechanisms
- **Time-based Restrictions**: Transactions can only be rolled back within 72 hours
- **Fraud Prevention**: Enhanced fraud detection during transactions
- **Balance Validation**: Ensure sufficient funds before transactions
- **Spending Limits**: Enforce daily spending limits and risk-based limits

## Database Schema Changes

### New Tables

#### transaction_backups
```sql
CREATE TABLE transaction_backups (
    backup_id CHAR(36) PRIMARY KEY,
    original_transaction_id CHAR(36),
    sender_id CHAR(36),
    receiver_id CHAR(36),
    sender_balance_before DECIMAL(10,2),
    receiver_balance_before DECIMAL(10,2),
    sender_balance_after DECIMAL(10,2),
    receiver_balance_after DECIMAL(10,2),
    transaction_amount DECIMAL(10,2),
    backup_timestamp DATETIME,
    rollback_timestamp DATETIME,
    rollback_reason TEXT
);
```

#### failed_transactions
```sql
CREATE TABLE failed_transactions (
    id CHAR(36) PRIMARY KEY,
    attempted_transaction_id CHAR(36),
    sender_id CHAR(36),
    receiver_id CHAR(36),
    amount DECIMAL(10,2),
    payment_method VARCHAR(100),
    failure_reason TEXT,
    failure_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### system_audit_log
```sql
CREATE TABLE system_audit_log (
    id CHAR(36) PRIMARY KEY,
    operation_type VARCHAR(50),
    entity_type VARCHAR(50),
    entity_id CHAR(36),
    user_id CHAR(36),
    old_values JSON,
    new_values JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);
```

### Schema Updates

#### transactions table
- Added `status` column: ENUM('PENDING', 'COMPLETED', 'FAILED', 'ROLLED_BACK')

## Stored Procedures

### ProcessMoneyTransferEnhanced
Enhanced transaction processing with comprehensive rollback support:
- Automatic backup creation before transaction
- Enhanced error handling with detailed logging
- Fraud detection and risk assessment
- Spending limit enforcement
- Atomic transaction processing

### RollbackTransaction
Rollback a completed transaction:
```sql
CALL RollbackTransaction(
    IN transaction_id CHAR(36),
    IN reason TEXT,
    OUT success BOOLEAN,
    OUT message VARCHAR(500)
);
```

### GetTransactionStatus
Check transaction status and rollback capability:
```sql
CALL GetTransactionStatus(
    IN transaction_id CHAR(36),
    OUT status VARCHAR(20),
    OUT can_rollback BOOLEAN,
    OUT message VARCHAR(500)
);
```

### BackupUserBalance
Create a backup of user balance:
```sql
CALL BackupUserBalance(
    IN user_id CHAR(36),
    IN operation_type VARCHAR(50),
    OUT backup_id CHAR(36),
    OUT success BOOLEAN,
    OUT message VARCHAR(500)
);
```

### RestoreUserBalance
Restore user balance from backup:
```sql
CALL RestoreUserBalance(
    IN backup_id CHAR(36),
    IN reason TEXT,
    OUT success BOOLEAN,
    OUT message VARCHAR(500)
);
```

### AutoRollbackFailedTransactions
Automatically rollback failed transactions:
```sql
CALL AutoRollbackFailedTransactions(
    IN hours_threshold INT DEFAULT 24,
    OUT rolled_back_count INT,
    OUT message VARCHAR(500)
);
```

## API Endpoints

### Admin Rollback Management

#### GET /rollback/dashboard
Access the rollback management dashboard (Admin only)

#### POST /rollback/transaction
Rollback a specific transaction
```json
{
    "transaction_id": "uuid",
    "reason": "Reason for rollback"
}
```

#### GET /rollback/status/{transaction_id}
Check if a transaction can be rolled back
```json
{
    "success": true,
    "status": "COMPLETED",
    "can_rollback": true,
    "message": "Transaction can be rolled back"
}
```

#### POST /rollback/backup/user
Create a backup of user balance
```json
{
    "user_id": "uuid",
    "operation_type": "Manual backup"
}
```

#### POST /rollback/restore/user
Restore user balance from backup
```json
{
    "backup_id": "uuid",
    "reason": "Manual restore"
}
```

#### POST /rollback/auto
Auto-rollback failed transactions
```json
{
    "hours_threshold": 24
}
```

### Monitoring Endpoints

#### GET /rollback/history/{user_id}
Get transaction history with rollback status

#### GET /rollback/failed
Get failed transactions for admin review

#### GET /rollback/audit
Get system audit log

## Python API

### Transaction Functions

```python
from app.utils.transaction_utils import (
    rollback_transaction,
    get_transaction_status,
    backup_user_balance,
    restore_user_balance,
    auto_rollback_failed_transactions
)

# Rollback a transaction
success, message = rollback_transaction(transaction_id, reason)

# Check transaction status
status, can_rollback, message = get_transaction_status(transaction_id)

# Backup user balance
success, message, backup_id = backup_user_balance(user_id, operation_type)

# Restore user balance
success, message = restore_user_balance(backup_id, reason)

# Auto-rollback failed transactions
success, message, count = auto_rollback_failed_transactions(hours_threshold)
```

## Deployment

### Prerequisites
- MySQL 5.7+ with event scheduler enabled
- Python 3.7+
- Required packages: pymysql, mysql-connector-python

### Step 1: Update Database Schema
```bash
python deploy_rollback_optimizations.py
```

### Step 2: Verify Deployment
The deployment script will automatically:
1. Create database backups
2. Apply schema updates
3. Deploy stored procedures
4. Create maintenance jobs
5. Verify all components

### Step 3: Configure Maintenance
The system automatically creates an event scheduler job that:
- Runs every hour
- Auto-rolls back failed transactions older than 24 hours
- Logs maintenance activities

## Security Considerations

### Access Control
- Only admins can access rollback functionality
- All rollback operations are logged
- User authentication required for all operations

### Data Protection
- Backups are created before all transactions
- Rollback operations are atomic
- All operations include audit trails

### Time Restrictions
- Transactions can only be rolled back within 72 hours
- Failed transactions are auto-rolled back after 24 hours
- Backup data is retained for audit purposes

## Monitoring and Alerting

### Dashboard Features
- Real-time transaction status monitoring
- Failed transaction alerts
- Rollback operation history
- System audit log visualization

### Automated Maintenance
- Daily cleanup of old backup data
- Automatic rollback of failed transactions
- System health monitoring

## Best Practices

### When to Use Rollback
1. **Technical Failures**: Database errors, network issues
2. **Fraud Detection**: Suspicious activity detected post-transaction
3. **User Disputes**: Legitimate customer complaints
4. **System Errors**: Application bugs causing incorrect transactions

### When NOT to Use Rollback
1. **Normal Business Operations**: Regular transaction reversals
2. **User Regret**: Customer changed their mind
3. **Old Transactions**: Transactions older than 72 hours
4. **Already Processed**: Transactions already reconciled

### Monitoring Guidelines
1. Monitor failed transaction rates
2. Review rollback patterns for system issues
3. Regular audit of rollback operations
4. Performance monitoring of rollback procedures

## Troubleshooting

### Common Issues

#### Transaction Cannot Be Rolled Back
- Check transaction status using GetTransactionStatus
- Verify transaction is within 72-hour window
- Ensure backup data exists
- Check if transaction is already rolled back

#### Backup Not Found
- Verify backup_id is correct
- Check transaction_backups table
- Ensure backup was created during original transaction

#### Auto-Rollback Not Working
- Check event scheduler status: `SHOW VARIABLES LIKE 'event_scheduler'`
- Verify event exists: `SHOW EVENTS`
- Check system_audit_log for maintenance activities

### Error Codes
- `45000`: General rollback error
- `45001`: Transaction not found
- `45002`: Backup not found
- `45003`: Transaction too old for rollback

## Performance Considerations

### Optimization Tips
1. Regular cleanup of old backup data
2. Index optimization on backup tables
3. Monitor rollback procedure performance
4. Batch processing for auto-rollback operations

### Scaling Considerations
- Partition backup tables by date
- Archive old audit logs
- Consider separate backup database for large volumes
- Implement asynchronous rollback processing for high-volume systems

## Support and Maintenance

### Regular Tasks
1. Monthly review of rollback statistics
2. Quarterly audit of rollback procedures
3. Annual backup data archival
4. Regular testing of rollback functionality

### Emergency Procedures
1. Manual rollback for critical transactions
2. Bulk rollback for system-wide issues
3. Emergency backup restoration
4. System recovery procedures

## License
This rollback functionality is part of the FinGuard application and follows the same licensing terms.
