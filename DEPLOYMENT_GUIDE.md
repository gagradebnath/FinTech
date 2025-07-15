# Manual Deployment Steps for FinGuard Rollback Functionality

## Step 1: Apply Simple Schema Updates
```bash
mysql -u root -p fin_guard < schema_updates_simple.sql
```

## Step 2: Apply PL/SQL Optimizations
```bash
mysql -u root -p fin_guard < PL_SQL_Optimizations.sql
```

## Step 3: Test the Deployment
```bash
python test_rollback.py
```

## Step 4: Start the Application
```bash
python run.py
```

## Step 5: Access Rollback Dashboard
- Login as admin
- Navigate to: http://localhost:5000/rollback/dashboard

## Alternative: Use Batch Script
```bash
deploy_mysql57.bat  # For MySQL 5.7+ compatibility
# OR
deploy_rollback.bat # For newer MySQL versions
```

## Quick Database Check:
```sql
-- Check your database name
SHOW DATABASES;

-- If database doesn't exist, create it
CREATE DATABASE fin_guard;
USE fin_guard;
```

## Troubleshooting

### Database Name Issues:
Make sure you're using the correct database name:
- If your database is named `fin_guard`, use: `mysql -u root -p fin_guard`
- If your database is named `finguard`, use: `mysql -u root -p finguard`
- Check your database name with: `SHOW DATABASES;`

### If schema_updates_simple.sql fails:
1. Check if the database exists: `SHOW DATABASES;`
2. Check if you're using the correct database: `USE fin_guard;`
3. Try the step-by-step approach below

### Manual Step-by-Step Schema Updates:
```sql
-- Connect to MySQL
mysql -u root -p

-- Use the database
USE fin_guard;

-- Add columns to users table (one by one)
ALTER TABLE users ADD COLUMN last_activity DATETIME;
ALTER TABLE users ADD COLUMN is_suspended BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN suspension_reason TEXT;

-- Add columns to transactions table (one by one)
ALTER TABLE transactions ADD COLUMN status VARCHAR(20) DEFAULT 'COMPLETED';
ALTER TABLE transactions ADD COLUMN rollback_reason VARCHAR(500) NULL;
ALTER TABLE transactions ADD COLUMN rollback_timestamp DATETIME NULL;

-- Create rollback tables
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
    backup_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    rollback_executed BOOLEAN DEFAULT FALSE,
    rollback_timestamp DATETIME NULL,
    rollback_reason TEXT NULL
);

CREATE TABLE failed_transactions (
    id CHAR(36) PRIMARY KEY,
    attempted_transaction_id CHAR(36),
    sender_id CHAR(36),
    receiver_id CHAR(36),
    amount DECIMAL(10,2),
    payment_method VARCHAR(100),
    failure_reason TEXT,
    failure_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    retry_count INT DEFAULT 0
);

CREATE TABLE system_audit_log (
    id CHAR(36) PRIMARY KEY,
    operation_type VARCHAR(50),
    entity_type VARCHAR(50),
    entity_id CHAR(36),
    old_values TEXT,
    new_values TEXT,
    user_id CHAR(36),
    ip_address VARCHAR(45),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

-- Exit MySQL
EXIT;
```

### Then apply the PL/SQL optimizations:
```bash
mysql -u root -p fin_guard < PL_SQL_Optimizations.sql
```

## Verification Commands:
```sql
-- Check if tables exist
SHOW TABLES LIKE '%rollback%';
SHOW TABLES LIKE '%backup%';
SHOW TABLES LIKE '%audit%';

-- Check if columns were added
DESCRIBE users;
DESCRIBE transactions;

-- Check if procedures exist
SHOW PROCEDURE STATUS WHERE Db = 'fin_guard';
```

## Support Files:
- `schema_updates_simple.sql` - Simplified schema updates
- `schema_updates_compatible.sql` - Original compatible version
- `PL_SQL_Optimizations.sql` - Stored procedures and functions
- `deploy_rollback.bat` - Automated deployment script
- `test_rollback.py` - Test script to verify deployment
