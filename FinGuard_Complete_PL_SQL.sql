-- FinGuard Comprehensive PL/SQL Implementation
-- This file contains all optimized procedures, functions, triggers, and views

-- Set delimiter for procedures
DELIMITER //

-- Database utility procedures
DROP PROCEDURE IF EXISTS AddColumnIfNotExists//
CREATE PROCEDURE AddColumnIfNotExists(
    IN table_name VARCHAR(64),
    IN column_name VARCHAR(64),
    IN column_definition TEXT
)
BEGIN
    DECLARE col_exists INT DEFAULT 0;
    
    SELECT COUNT(*) INTO col_exists
    FROM information_schema.columns 
    WHERE table_schema = DATABASE() 
    AND table_name = table_name 
    AND column_name = column_name;
    
    IF col_exists = 0 THEN
        SET @sql = CONCAT('ALTER TABLE ', table_name, ' ADD COLUMN ', column_name, ' ', column_definition);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END//

-- Enhanced Money Transfer Procedure
DROP PROCEDURE IF EXISTS ProcessMoneyTransferEnhanced//
CREATE PROCEDURE ProcessMoneyTransferEnhanced(
    IN p_sender_id CHAR(36),
    IN p_receiver_id CHAR(36),
    IN p_amount DECIMAL(15,2),
    IN p_payment_method VARCHAR(50),
    IN p_description TEXT,
    OUT p_transaction_id CHAR(36),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500)
)
BEGIN
    DECLARE v_sender_balance DECIMAL(15,2) DEFAULT 0;
    DECLARE v_receiver_balance DECIMAL(15,2) DEFAULT 0;
    DECLARE v_transaction_uuid CHAR(36);
    
    START TRANSACTION;
    
    SET v_transaction_uuid = UUID();
    SET p_transaction_id = v_transaction_uuid;
    
    -- Check sender balance
    SELECT balance INTO v_sender_balance FROM users WHERE id = p_sender_id;
    
    IF v_sender_balance < p_amount THEN
        SET p_success = FALSE;
        SET p_message = 'Insufficient balance';
        ROLLBACK;
        RETURN;
    END IF;
    
    -- Update balances
    UPDATE users SET balance = balance - p_amount WHERE id = p_sender_id;
    UPDATE users SET balance = balance + p_amount WHERE id = p_receiver_id;
    
    -- Create transaction record
    INSERT INTO transactions (
        id, sender_id, receiver_id, amount, payment_method, 
        description, timestamp
    ) VALUES (
        v_transaction_uuid, p_sender_id, p_receiver_id, p_amount, 
        p_payment_method, p_description, NOW()
    );
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = 'Transfer completed successfully';
END//

-- User Risk Score Function
DROP FUNCTION IF EXISTS GetUserRiskScore//
CREATE FUNCTION GetUserRiskScore(p_user_id CHAR(36)) 
RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_fraud_reports INT DEFAULT 0;
    DECLARE v_risk_score INT DEFAULT 0;
    
    SELECT COUNT(*) INTO v_fraud_reports
    FROM fraud_list 
    WHERE reported_user_id = p_user_id;
    
    SET v_risk_score = v_fraud_reports * 25;
    
    IF v_risk_score > 100 THEN
        SET v_risk_score = 100;
    END IF;
    
    RETURN v_risk_score;
END//

-- Transaction Audit Trigger
DROP TRIGGER IF EXISTS tr_transaction_audit//
CREATE TRIGGER tr_transaction_audit
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    -- Log transaction details for audit trail
    INSERT INTO admin_logs (
        id, admin_id, action, details, timestamp
    ) VALUES (
        UUID(), 
        NEW.sender_id, 
        'TRANSACTION_CREATED',
        CONCAT('Transaction ID: ', NEW.id, ', Amount: ', NEW.amount, ', Receiver: ', NEW.receiver_id),
        NOW()
    );
END//

-- Balance Update Trigger
DROP TRIGGER IF EXISTS tr_balance_validation//
CREATE TRIGGER tr_balance_validation
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    -- Prevent negative balance
    IF NEW.balance < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Balance cannot be negative';
    END IF;
    
    -- Log significant balance changes
    IF ABS(NEW.balance - OLD.balance) > 10000 THEN
        INSERT INTO admin_logs (
            id, admin_id, action, details, timestamp
        ) VALUES (
            UUID(),
            NEW.id,
            'LARGE_BALANCE_CHANGE',
            CONCAT('Balance changed from ', OLD.balance, ' to ', NEW.balance),
            NOW()
        );
    END IF;
END//

-- Fraud Detection Trigger
DROP TRIGGER IF EXISTS tr_fraud_detection//
CREATE TRIGGER tr_fraud_detection
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    DECLARE v_transaction_count INT DEFAULT 0;
    DECLARE v_total_amount DECIMAL(15,2) DEFAULT 0;
    
    -- Check for suspicious activity (more than 5 transactions in 1 hour)
    SELECT COUNT(*), COALESCE(SUM(amount), 0) INTO v_transaction_count, v_total_amount
    FROM transactions 
    WHERE sender_id = NEW.sender_id 
    AND timestamp >= DATE_SUB(NOW(), INTERVAL 1 HOUR);
    
    -- Flag suspicious activity
    IF v_transaction_count > 5 OR v_total_amount > 50000 THEN
        INSERT INTO fraud_list (
            id, reported_user_id, reporter_id, reason, 
            report_date, status, investigation_notes
        ) VALUES (
            UUID(),
            NEW.sender_id,
            'SYSTEM',
            CONCAT('Suspicious activity detected: ', v_transaction_count, ' transactions totaling ', v_total_amount, ' in 1 hour'),
            NOW(),
            'PENDING',
            'Auto-flagged by fraud detection system'
        );
    END IF;
END//

-- User Registration Trigger
DROP TRIGGER IF EXISTS tr_user_registration//
CREATE TRIGGER tr_user_registration
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    -- Set default role if not specified
    IF NEW.role_id IS NULL THEN
        UPDATE users 
        SET role_id = (SELECT id FROM roles WHERE name = 'USER' LIMIT 1)
        WHERE id = NEW.id;
    END IF;
    
    -- Log user registration
    INSERT INTO admin_logs (
        id, admin_id, action, details, timestamp
    ) VALUES (
        UUID(),
        NEW.id,
        'USER_REGISTERED',
        CONCAT('New user registered: ', NEW.first_name, ' ', NEW.last_name),
        NOW()
    );
END//

-- Budget Expense Tracking Trigger
DROP TRIGGER IF EXISTS tr_budget_expense_tracking//
CREATE TRIGGER tr_budget_expense_tracking
AFTER INSERT ON budget_expense_items
FOR EACH ROW
BEGIN
    DECLARE v_budget_limit DECIMAL(15,2) DEFAULT 0;
    DECLARE v_total_expenses DECIMAL(15,2) DEFAULT 0;
    DECLARE v_user_id CHAR(36);
    
    -- Get budget limit and user
    SELECT b.budget_limit, b.user_id INTO v_budget_limit, v_user_id
    FROM budgets b
    WHERE b.id = NEW.budget_id;
    
    -- Calculate total expenses for this budget
    SELECT COALESCE(SUM(amount), 0) INTO v_total_expenses
    FROM budget_expense_items
    WHERE budget_id = NEW.budget_id;
    
    -- Alert if budget exceeded
    IF v_total_expenses > v_budget_limit THEN
        INSERT INTO admin_logs (
            id, admin_id, action, details, timestamp
        ) VALUES (
            UUID(),
            v_user_id,
            'BUDGET_EXCEEDED',
            CONCAT('Budget limit exceeded: ', v_total_expenses, ' / ', v_budget_limit),
            NOW()
        );
    END IF;
END//

-- Password Change Trigger
DROP TRIGGER IF EXISTS tr_password_change//
CREATE TRIGGER tr_password_change
AFTER UPDATE ON user_passwords
FOR EACH ROW
BEGIN
    -- Log password changes for security
    IF OLD.password_hash != NEW.password_hash THEN
        INSERT INTO admin_logs (
            id, admin_id, action, details, timestamp
        ) VALUES (
            UUID(),
            NEW.user_id,
            'PASSWORD_CHANGED',
            'User password was changed',
            NOW()
        );
    END IF;
END//

-- Blockchain Transaction Trigger
DROP TRIGGER IF EXISTS tr_blockchain_transaction//
CREATE TRIGGER tr_blockchain_transaction
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    DECLARE v_previous_hash VARCHAR(64) DEFAULT '';
    DECLARE v_current_hash VARCHAR(64);
    
    -- Get previous block hash
    SELECT hash INTO v_previous_hash 
    FROM blockchain 
    ORDER BY timestamp DESC 
    LIMIT 1;
    
    -- Generate new hash (simplified - in real implementation use proper cryptographic hash)
    SET v_current_hash = SHA2(CONCAT(NEW.id, NEW.amount, NEW.timestamp, v_previous_hash), 256);
    
    -- Insert blockchain record
    INSERT INTO blockchain (
        id, transaction_id, previous_hash, hash, timestamp
    ) VALUES (
        UUID(),
        NEW.id,
        v_previous_hash,
        v_current_hash,
        NOW()
    );
END//

-- Account Lock Trigger (for security)
DROP TRIGGER IF EXISTS tr_account_security//
CREATE TRIGGER tr_account_security
AFTER UPDATE ON fraud_list
FOR EACH ROW
BEGIN
    -- If fraud status changes to CONFIRMED, log it
    IF OLD.status != NEW.status AND NEW.status = 'CONFIRMED' THEN
        INSERT INTO admin_logs (
            id, admin_id, action, details, timestamp
        ) VALUES (
            UUID(),
            NEW.reported_user_id,
            'FRAUD_CONFIRMED',
            CONCAT('Fraud confirmed for user: ', NEW.reported_user_id, ' - Reason: ', NEW.reason),
            NOW()
        );
    END IF;
END//

-- Transaction Timestamp Trigger
DROP TRIGGER IF EXISTS tr_transaction_timestamp//
CREATE TRIGGER tr_transaction_timestamp
BEFORE INSERT ON transactions
FOR EACH ROW
BEGIN
    -- Ensure timestamp is set
    IF NEW.timestamp IS NULL THEN
        SET NEW.timestamp = NOW();
    END IF;
    
    -- Generate UUID if not provided
    IF NEW.id IS NULL OR NEW.id = '' THEN
        SET NEW.id = UUID();
    END IF;
END//

-- Reset delimiter
DELIMITER ;

-- Final status message
SELECT 'FinGuard PL/SQL Deployment with Triggers Completed Successfully!' as message;
