-- Schema updates for FinGuard rollback functionality
-- Compatible with MySQL 5.7+ 

USE fin_guard;

-- Set SQL mode to be more permissive for older MySQL versions
SET SESSION sql_mode = 'TRADITIONAL,NO_AUTO_VALUE_ON_ZERO';

-- Drop and recreate procedure for adding columns if they don't exist
DROP PROCEDURE IF EXISTS AddColumnIfNotExists;

DELIMITER $$
CREATE PROCEDURE AddColumnIfNotExists(
    IN table_name VARCHAR(128),
    IN column_name VARCHAR(128),
    IN column_definition TEXT
)
BEGIN
    DECLARE col_exists INT DEFAULT 0;
    
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
    END IF;
END$$

DELIMITER ;

-- Add columns to users table
CALL AddColumnIfNotExists('users', 'last_activity', 'DATETIME');
CALL AddColumnIfNotExists('users', 'is_suspended', 'BOOLEAN DEFAULT FALSE');
CALL AddColumnIfNotExists('users', 'suspension_reason', 'TEXT');
CALL AddColumnIfNotExists('users', 'created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP');
CALL AddColumnIfNotExists('users', 'updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP');

-- Add columns to transactions table
CALL AddColumnIfNotExists('transactions', 'status', 'ENUM(\'PENDING\', \'COMPLETED\', \'FAILED\', \'ROLLED_BACK\') DEFAULT \'COMPLETED\'');
CALL AddColumnIfNotExists('transactions', 'rollback_reason', 'VARCHAR(500) NULL');
CALL AddColumnIfNotExists('transactions', 'rollback_timestamp', 'DATETIME NULL');
CALL AddColumnIfNotExists('transactions', 'original_transaction_id', 'CHAR(36) NULL');

-- Drop the helper procedure
DROP PROCEDURE IF EXISTS AddColumnIfNotExists;

-- Create transaction backup table
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create failed transactions table
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create system audit log table
CREATE TABLE IF NOT EXISTS system_audit_log (
    id CHAR(36) PRIMARY KEY,
    operation_type VARCHAR(50),
    entity_type VARCHAR(50),
    entity_id CHAR(36),
    old_values JSON,
    new_values JSON,
    user_id CHAR(36),
    ip_address VARCHAR(45),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Drop and recreate procedure for adding indexes if they don't exist
DROP PROCEDURE IF EXISTS AddIndexIfNotExists;

DELIMITER $$
CREATE PROCEDURE AddIndexIfNotExists(
    IN table_name VARCHAR(128),
    IN index_name VARCHAR(128),
    IN index_definition TEXT
)
BEGIN
    DECLARE idx_exists INT DEFAULT 0;
    
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
    END IF;
END$$

DELIMITER ;

-- Add indexes for performance
CALL AddIndexIfNotExists('users', 'idx_users_last_activity', '(last_activity)');
CALL AddIndexIfNotExists('users', 'idx_users_suspended', '(is_suspended)');
CALL AddIndexIfNotExists('transactions', 'idx_transactions_sender_timestamp', '(sender_id, timestamp)');
CALL AddIndexIfNotExists('transactions', 'idx_transactions_receiver_timestamp', '(receiver_id, timestamp)');
CALL AddIndexIfNotExists('transactions', 'idx_transactions_status', '(status)');
CALL AddIndexIfNotExists('transaction_backups', 'idx_backup_original_transaction', '(original_transaction_id)');
CALL AddIndexIfNotExists('transaction_backups', 'idx_backup_timestamp', '(backup_timestamp)');
CALL AddIndexIfNotExists('failed_transactions', 'idx_failed_sender', '(sender_id)');
CALL AddIndexIfNotExists('failed_transactions', 'idx_failed_timestamp', '(failure_timestamp)');
CALL AddIndexIfNotExists('system_audit_log', 'idx_audit_operation_type', '(operation_type)');
CALL AddIndexIfNotExists('system_audit_log', 'idx_audit_timestamp', '(timestamp)');
CALL AddIndexIfNotExists('system_audit_log', 'idx_audit_user_id', '(user_id)');

-- Attempt to add indexes to existing tables (may fail if tables don't exist)
CALL AddIndexIfNotExists('fraud_list', 'idx_fraud_list_reported_user', '(reported_user_id)');
CALL AddIndexIfNotExists('fraud_list', 'idx_fraud_list_reporter', '(user_id)');
CALL AddIndexIfNotExists('budgets', 'idx_budgets_user_id', '(user_id)');

-- Drop the helper procedure
DROP PROCEDURE IF EXISTS AddIndexIfNotExists;

-- Update existing transactions to have COMPLETED status if they don't have one
-- But only if the status column exists
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'transactions' 
     AND COLUMN_NAME = 'status') > 0,
    'UPDATE transactions SET status = ''COMPLETED'' WHERE status IS NULL OR status = ''''',
    'SELECT ''Status column does not exist, skipping update'' as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Ensure proper charset and collation for rollback tables
ALTER TABLE transaction_backups CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE failed_transactions CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE system_audit_log CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Display completion message
SELECT 'Schema updates completed successfully!' as message;
