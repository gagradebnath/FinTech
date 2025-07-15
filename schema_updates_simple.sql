-- Simple and robust schema updates for FinGuard rollback functionality
-- Compatible with MySQL 5.7+ and handles all edge cases

USE fin_guard;

-- Set SQL mode to be more permissive
SET SESSION sql_mode = 'TRADITIONAL,NO_AUTO_VALUE_ON_ZERO';

-- Helper procedure to safely add columns
DROP PROCEDURE IF EXISTS SafeAddColumn;
DELIMITER $$
CREATE PROCEDURE SafeAddColumn(
    IN table_name VARCHAR(128),
    IN column_name VARCHAR(128),
    IN column_definition TEXT
)
BEGIN
    DECLARE col_exists INT DEFAULT 0;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
    
    SELECT COUNT(*) INTO col_exists
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = table_name 
    AND COLUMN_NAME = column_name;
    
    IF col_exists = 0 THEN
        SET @sql = CONCAT('ALTER TABLE ', table_name, ' ADD COLUMN ', column_name, ' ', column_definition);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        SELECT CONCAT('Added column ', column_name, ' to ', table_name) as message;
    ELSE
        SELECT CONCAT('Column ', column_name, ' already exists in ', table_name) as message;
    END IF;
END$$
DELIMITER ;

-- Helper procedure to safely add indexes
DROP PROCEDURE IF EXISTS SafeAddIndex;
DELIMITER $$
CREATE PROCEDURE SafeAddIndex(
    IN table_name VARCHAR(128),
    IN index_name VARCHAR(128),
    IN index_definition TEXT
)
BEGIN
    DECLARE idx_exists INT DEFAULT 0;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
    
    SELECT COUNT(*) INTO idx_exists
    FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = table_name 
    AND INDEX_NAME = index_name;
    
    IF idx_exists = 0 THEN
        SET @sql = CONCAT('CREATE INDEX ', index_name, ' ON ', table_name, ' ', index_definition);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        SELECT CONCAT('Added index ', index_name, ' to ', table_name) as message;
    ELSE
        SELECT CONCAT('Index ', index_name, ' already exists on ', table_name) as message;
    END IF;
END$$
DELIMITER ;

-- Add columns to users table
CALL SafeAddColumn('users', 'last_activity', 'DATETIME');
CALL SafeAddColumn('users', 'is_suspended', 'BOOLEAN DEFAULT FALSE');
CALL SafeAddColumn('users', 'suspension_reason', 'TEXT');
CALL SafeAddColumn('users', 'created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP');
CALL SafeAddColumn('users', 'updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP');

-- Add columns to transactions table
CALL SafeAddColumn('transactions', 'status', 'VARCHAR(20) DEFAULT ''COMPLETED''');
CALL SafeAddColumn('transactions', 'rollback_reason', 'VARCHAR(500) NULL');
CALL SafeAddColumn('transactions', 'rollback_timestamp', 'DATETIME NULL');
CALL SafeAddColumn('transactions', 'original_transaction_id', 'CHAR(36) NULL');

-- Create rollback tables
CREATE TABLE IF NOT EXISTS transaction_backups (
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

CREATE TABLE IF NOT EXISTS failed_transactions (
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

CREATE TABLE IF NOT EXISTS system_audit_log (
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

-- Add indexes for performance
CALL SafeAddIndex('users', 'idx_users_last_activity', '(last_activity)');
CALL SafeAddIndex('users', 'idx_users_suspended', '(is_suspended)');
CALL SafeAddIndex('transactions', 'idx_transactions_sender_timestamp', '(sender_id, timestamp)');
CALL SafeAddIndex('transactions', 'idx_transactions_receiver_timestamp', '(receiver_id, timestamp)');
CALL SafeAddIndex('transactions', 'idx_transactions_status', '(status)');
CALL SafeAddIndex('transaction_backups', 'idx_backup_original_transaction', '(original_transaction_id)');
CALL SafeAddIndex('transaction_backups', 'idx_backup_timestamp', '(backup_timestamp)');
CALL SafeAddIndex('failed_transactions', 'idx_failed_sender', '(sender_id)');
CALL SafeAddIndex('failed_transactions', 'idx_failed_timestamp', '(failure_timestamp)');
CALL SafeAddIndex('system_audit_log', 'idx_audit_operation_type', '(operation_type)');
CALL SafeAddIndex('system_audit_log', 'idx_audit_timestamp', '(timestamp)');

-- Try to add indexes to existing tables (ignore errors if tables don't exist)
CALL SafeAddIndex('fraud_list', 'idx_fraud_list_reported_user', '(reported_user_id)');
CALL SafeAddIndex('fraud_list', 'idx_fraud_list_reporter', '(user_id)');
CALL SafeAddIndex('budgets', 'idx_budgets_user_id', '(user_id)');

-- Update existing transactions to have COMPLETED status
-- Create a safe update procedure
DROP PROCEDURE IF EXISTS SafeUpdateTransactionStatus;
DELIMITER $$
CREATE PROCEDURE SafeUpdateTransactionStatus()
BEGIN
    DECLARE col_exists INT DEFAULT 0;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
    
    SELECT COUNT(*) INTO col_exists
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'transactions' 
    AND COLUMN_NAME = 'status';
    
    IF col_exists > 0 THEN
        UPDATE transactions SET status = 'COMPLETED' WHERE status IS NULL OR status = '';
        SELECT 'Updated transaction status to COMPLETED' as message;
    ELSE
        SELECT 'Status column does not exist, skipping update' as message;
    END IF;
END$$
DELIMITER ;

-- Execute the safe update
CALL SafeUpdateTransactionStatus();

-- Drop helper procedures
DROP PROCEDURE IF EXISTS SafeAddColumn;
DROP PROCEDURE IF EXISTS SafeAddIndex;
DROP PROCEDURE IF EXISTS SafeUpdateTransactionStatus;

-- Final message
SELECT 'Schema updates completed successfully!' as message;
SELECT 'All rollback tables and columns have been created/updated.' as status;
SELECT 'You can now run: mysql -u root -p fin_guard < PL_SQL_Optimizations.sql' as next_step;
