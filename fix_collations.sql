-- Script to fix collation issues in FinGuard database

-- Check current collations
SELECT 
    table_name,
    column_name,
    collation_name,
    data_type
FROM information_schema.columns 
WHERE table_schema = 'fin_guard' 
AND collation_name IS NOT NULL
ORDER BY table_name, column_name;

-- Fix collation for key tables
-- Users table
ALTER TABLE users CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Fraud_list table
ALTER TABLE fraud_list CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Transactions table
ALTER TABLE transactions CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Budgets table
ALTER TABLE budgets CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Chat_messages table
ALTER TABLE chat_messages CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- All other tables
ALTER TABLE roles CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE user_passwords CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE contact_info CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Fix any new tables that might have been created with different collations
ALTER TABLE transaction_backups CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE failed_transactions CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE system_audit_log CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Set default collation for the database
ALTER DATABASE fin_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

SELECT 'Collation fix completed' as status;
