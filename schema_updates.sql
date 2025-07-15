-- Schema updates for PL/SQL optimizations
-- Run this after the main schema to add missing columns

USE fin_guard;

-- Add missing columns to users table using compatible syntax
-- Check and add columns one by one to avoid syntax errors
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'users' 
     AND COLUMN_NAME = 'last_activity') > 0,
    'SELECT 1',
    'ALTER TABLE users ADD COLUMN last_activity DATETIME'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'users' 
     AND COLUMN_NAME = 'is_suspended') > 0,
    'SELECT 1',
    'ALTER TABLE users ADD COLUMN is_suspended BOOLEAN DEFAULT FALSE'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add transaction status and rollback tracking
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'transactions' 
     AND COLUMN_NAME = 'status') > 0,
    'SELECT 1',
    'ALTER TABLE transactions ADD COLUMN status ENUM(''PENDING'', ''COMPLETED'', ''FAILED'', ''ROLLED_BACK'') DEFAULT ''PENDING'''
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'transactions' 
     AND COLUMN_NAME = 'rollback_reason') > 0,
    'SELECT 1',
    'ALTER TABLE transactions ADD COLUMN rollback_reason VARCHAR(500) NULL'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'transactions' 
     AND COLUMN_NAME = 'rollback_timestamp') > 0,
    'SELECT 1',
    'ALTER TABLE transactions ADD COLUMN rollback_timestamp DATETIME NULL'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'transactions' 
     AND COLUMN_NAME = 'original_transaction_id') > 0,
    'SELECT 1',
    'ALTER TABLE transactions ADD COLUMN original_transaction_id CHAR(36) NULL'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add transaction backup table for rollback purposes
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
    INDEX idx_original_transaction (original_transaction_id),
    INDEX idx_backup_timestamp (backup_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add failed transaction log table
CREATE TABLE IF NOT EXISTS failed_transactions (
    id CHAR(36) PRIMARY KEY,
    attempted_transaction_id CHAR(36),
    sender_id CHAR(36),
    receiver_id CHAR(36),
    amount DECIMAL(10,2),
    payment_method VARCHAR(100),
    failure_reason TEXT,
    failure_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    retry_count INT DEFAULT 0,
    INDEX idx_sender (sender_id),
    INDEX idx_failure_timestamp (failure_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add system audit log for critical operations
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
    error_message TEXT,
    INDEX idx_operation_type (operation_type),
    INDEX idx_entity_type (entity_type),
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Update transaction_backups table to include rollback fields
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'transaction_backups' 
     AND COLUMN_NAME = 'rollback_timestamp') > 0,
    'SELECT 1',
    'ALTER TABLE transaction_backups ADD COLUMN rollback_timestamp DATETIME NULL'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'transaction_backups' 
     AND COLUMN_NAME = 'rollback_reason') > 0,
    'SELECT 1',
    'ALTER TABLE transaction_backups ADD COLUMN rollback_reason TEXT NULL'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add indexes for better performance using compatible syntax
-- Check and create indexes one by one to avoid syntax errors

-- Index for users last_activity
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'users' 
     AND INDEX_NAME = 'idx_users_last_activity') > 0,
    'SELECT 1',
    'CREATE INDEX idx_users_last_activity ON users (last_activity)'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Index for users suspended status
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'users' 
     AND INDEX_NAME = 'idx_users_suspended') > 0,
    'SELECT 1',
    'CREATE INDEX idx_users_suspended ON users (is_suspended)'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Index for transactions sender and timestamp
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'transactions' 
     AND INDEX_NAME = 'idx_transactions_sender_timestamp') > 0,
    'SELECT 1',
    'CREATE INDEX idx_transactions_sender_timestamp ON transactions (sender_id, timestamp)'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Index for transactions receiver and timestamp
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'transactions' 
     AND INDEX_NAME = 'idx_transactions_receiver_timestamp') > 0,
    'SELECT 1',
    'CREATE INDEX idx_transactions_receiver_timestamp ON transactions (receiver_id, timestamp)'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Index for transactions date
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'transactions' 
     AND INDEX_NAME = 'idx_transactions_date') > 0,
    'SELECT 1',
    'CREATE INDEX idx_transactions_date ON transactions (DATE(timestamp))'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Index for transactions status
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'transactions' 
     AND INDEX_NAME = 'idx_transactions_status') > 0,
    'SELECT 1',
    'CREATE INDEX idx_transactions_status ON transactions (status)'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Index for fraud_list reported_user
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'fraud_list' 
     AND INDEX_NAME = 'idx_fraud_list_reported_user') > 0,
    'SELECT 1',
    'CREATE INDEX idx_fraud_list_reported_user ON fraud_list (reported_user_id)'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Index for fraud_list reporter
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'fraud_list' 
     AND INDEX_NAME = 'idx_fraud_list_reporter') > 0,
    'SELECT 1',
    'CREATE INDEX idx_fraud_list_reporter ON fraud_list (user_id)'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Index for admin_logs timestamp
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'admin_logs' 
     AND INDEX_NAME = 'idx_admin_logs_timestamp') > 0,
    'SELECT 1',
    'CREATE INDEX idx_admin_logs_timestamp ON admin_logs (timestamp)'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Index for budgets user_id
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
     WHERE TABLE_SCHEMA = DATABASE() 
     AND TABLE_NAME = 'budgets' 
     AND INDEX_NAME = 'idx_budgets_user_id') > 0,
    'SELECT 1',
    'CREATE INDEX idx_budgets_user_id ON budgets (user_id)'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
