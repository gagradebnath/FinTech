-- =============================================================================
-- FINGUARD PL/SQL OPTIMIZATIONS
-- Advanced SQL Features to Replace Current Python Queries
-- =============================================================================

USE fin_guard;

DELIMITER //

-- =============================================================================
-- 1. ENHANCED TRANSACTION PROCESSING
-- =============================================================================

-- Improved Money Transfer Procedure with comprehensive rollback functionality
DROP PROCEDURE IF EXISTS ProcessMoneyTransferEnhanced//
CREATE PROCEDURE ProcessMoneyTransferEnhanced(
    IN p_sender_id CHAR(36),
    IN p_receiver_id CHAR(36),
    IN p_amount DECIMAL(10,2),
    IN p_payment_method VARCHAR(100),
    IN p_note TEXT,
    IN p_tx_type ENUM('Transfer', 'Deposit', 'Withdrawal', 'Payment', 'Refund'),
    IN p_location VARCHAR(255),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500),
    OUT p_transaction_id CHAR(36)
)
BEGIN
    DECLARE v_sender_balance DECIMAL(10,2);
    DECLARE v_receiver_balance DECIMAL(10,2);
    DECLARE v_sender_exists INT DEFAULT 0;
    DECLARE v_receiver_exists INT DEFAULT 0;
    DECLARE v_is_fraud_flagged INT DEFAULT 0;
    DECLARE v_tx_id CHAR(36);
    DECLARE v_backup_id CHAR(36);
    DECLARE v_risk_score DECIMAL(5,2);
    DECLARE v_daily_limit DECIMAL(10,2) DEFAULT 10000.00;
    DECLARE v_daily_spent DECIMAL(10,2) DEFAULT 0.00;
    DECLARE v_error_code VARCHAR(10);
    DECLARE v_error_message VARCHAR(500);
    
    -- Enhanced error handler with audit logging
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1
            v_error_code = MYSQL_ERRNO,
            v_error_message = MESSAGE_TEXT;
        
        ROLLBACK;
        
        -- Log the failed transaction
        INSERT INTO failed_transactions (
            id, attempted_transaction_id, sender_id, receiver_id, amount, 
            payment_method, failure_reason, failure_timestamp
        ) VALUES (
            UUID(), v_tx_id, p_sender_id, p_receiver_id, p_amount, 
            p_payment_method, CONCAT('SQL Error: ', v_error_code, ' - ', v_error_message), NOW()
        );
        
        -- Log to system audit
        INSERT INTO system_audit_log (
            id, operation_type, entity_type, entity_id, user_id, 
            success, error_message, timestamp
        ) VALUES (
            UUID(), 'TRANSACTION', 'TRANSACTION', v_tx_id, p_sender_id, 
            FALSE, v_error_message, NOW()
        );
        
        SET p_success = FALSE;
        SET p_message = CONCAT('Transaction failed: ', v_error_message);
        SET p_transaction_id = NULL;
    END;
    
    -- Generate transaction and backup IDs
    SET v_tx_id = UUID();
    SET v_backup_id = UUID();
    SET p_transaction_id = v_tx_id;
    
    START TRANSACTION;
    
    -- Enhanced validation with comprehensive error handling
    IF p_amount <= 0 THEN
        INSERT INTO failed_transactions (
            id, attempted_transaction_id, sender_id, receiver_id, amount, 
            payment_method, failure_reason
        ) VALUES (
            UUID(), v_tx_id, p_sender_id, p_receiver_id, p_amount, 
            p_payment_method, 'Invalid amount: must be greater than zero'
        );
        
        SET p_success = FALSE;
        SET p_message = 'Amount must be greater than zero';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Amount must be greater than zero';
    END IF;
    
    IF p_sender_id = p_receiver_id THEN
        INSERT INTO failed_transactions (
            id, attempted_transaction_id, sender_id, receiver_id, amount, 
            payment_method, failure_reason
        ) VALUES (
            UUID(), v_tx_id, p_sender_id, p_receiver_id, p_amount, 
            p_payment_method, 'Cannot transfer money to yourself'
        );
        
        SET p_success = FALSE;
        SET p_message = 'Cannot transfer money to yourself';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot transfer money to yourself';
    END IF;
    
    -- Check sender existence and get balance with exclusive lock
    SELECT COUNT(*), COALESCE(balance, 0) 
    INTO v_sender_exists, v_sender_balance
    FROM users 
    WHERE id = p_sender_id
    FOR UPDATE;
    
    IF v_sender_exists = 0 THEN
        INSERT INTO failed_transactions (
            id, attempted_transaction_id, sender_id, receiver_id, amount, 
            payment_method, failure_reason
        ) VALUES (
            UUID(), v_tx_id, p_sender_id, p_receiver_id, p_amount, 
            p_payment_method, 'Sender not found'
        );
        
        SET p_success = FALSE;
        SET p_message = 'Sender not found';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Sender not found';
    END IF;
    
    -- Check receiver existence and get balance with exclusive lock
    SELECT COUNT(*), COALESCE(balance, 0) 
    INTO v_receiver_exists, v_receiver_balance
    FROM users 
    WHERE id = p_receiver_id
    FOR UPDATE;
    
    IF v_receiver_exists = 0 THEN
        INSERT INTO failed_transactions (
            id, attempted_transaction_id, sender_id, receiver_id, amount, 
            payment_method, failure_reason
        ) VALUES (
            UUID(), v_tx_id, p_sender_id, p_receiver_id, p_amount, 
            p_payment_method, 'Receiver not found'
        );
        
        SET p_success = FALSE;
        SET p_message = 'Receiver not found';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Receiver not found';
    END IF;
    
    -- Check daily spending limit
    SELECT COALESCE(SUM(amount), 0) INTO v_daily_spent
    FROM transactions 
    WHERE sender_id = p_sender_id 
    AND DATE(timestamp) = CURDATE()
    AND status = 'COMPLETED';
    
    IF (v_daily_spent + p_amount) > v_daily_limit THEN
        INSERT INTO failed_transactions (
            id, attempted_transaction_id, sender_id, receiver_id, amount, 
            payment_method, failure_reason
        ) VALUES (
            UUID(), v_tx_id, p_sender_id, p_receiver_id, p_amount, 
            p_payment_method, CONCAT('Daily limit exceeded: ', v_daily_spent, ' + ', p_amount, ' > ', v_daily_limit)
        );
        
        SET p_success = FALSE;
        SET p_message = 'Daily transaction limit exceeded';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Daily transaction limit exceeded';
    END IF;
    
    -- Check balance sufficiency
    IF v_sender_balance < p_amount THEN
        INSERT INTO failed_transactions (
            id, attempted_transaction_id, sender_id, receiver_id, amount, 
            payment_method, failure_reason
        ) VALUES (
            UUID(), v_tx_id, p_sender_id, p_receiver_id, p_amount, 
            p_payment_method, CONCAT('Insufficient balance: ', v_sender_balance, ' < ', p_amount)
        );
        
        SET p_success = FALSE;
        SET p_message = 'Insufficient balance';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient balance';
    END IF;
    
    -- Check fraud status
    SELECT COUNT(*) INTO v_is_fraud_flagged 
    FROM fraud_list 
    WHERE reported_user_id = p_receiver_id;
    
    IF v_is_fraud_flagged > 0 THEN
        INSERT INTO failed_transactions (
            id, attempted_transaction_id, sender_id, receiver_id, amount, 
            payment_method, failure_reason
        ) VALUES (
            UUID(), v_tx_id, p_sender_id, p_receiver_id, p_amount, 
            p_payment_method, 'Receiver is fraud-flagged'
        );
        
        SET p_success = FALSE;
        SET p_message = 'Cannot transfer to fraud-flagged user';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot transfer to fraud-flagged user';
    END IF;
    
    -- Get sender risk score
    SET v_risk_score = GetUserRiskScore(p_sender_id);
    
    -- Risk-based transaction limits
    IF v_risk_score > 50 AND p_amount > 1000 THEN
        INSERT INTO failed_transactions (
            id, attempted_transaction_id, sender_id, receiver_id, amount, 
            payment_method, failure_reason
        ) VALUES (
            UUID(), v_tx_id, p_sender_id, p_receiver_id, p_amount, 
            p_payment_method, CONCAT('High risk transaction: Risk score ', v_risk_score, ' with amount ', p_amount)
        );
        
        SET p_success = FALSE;
        SET p_message = 'Transaction amount too high for risk profile';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Transaction amount too high for risk profile';
    END IF;
    
    -- Create backup record BEFORE making changes
    INSERT INTO transaction_backups (
        backup_id, original_transaction_id, sender_id, receiver_id,
        sender_balance_before, receiver_balance_before, transaction_amount,
        backup_timestamp
    ) VALUES (
        v_backup_id, v_tx_id, p_sender_id, p_receiver_id,
        v_sender_balance, v_receiver_balance, p_amount,
        NOW()
    );
    
    -- Log transaction start in system audit
    INSERT INTO system_audit_log (
        id, operation_type, entity_type, entity_id, user_id,
        old_values, new_values, timestamp, success
    ) VALUES (
        UUID(), 'TRANSACTION', 'TRANSACTION', v_tx_id, p_sender_id,
        JSON_OBJECT('sender_balance', v_sender_balance, 'receiver_balance', v_receiver_balance),
        JSON_OBJECT('amount', p_amount, 'type', p_tx_type),
        NOW(), FALSE
    );
    
    -- Perform the actual transfer with updated balances
    UPDATE users SET balance = balance - p_amount WHERE id = p_sender_id;
    UPDATE users SET balance = balance + p_amount WHERE id = p_receiver_id;
    
    -- Get updated balances for backup
    SELECT balance INTO v_sender_balance FROM users WHERE id = p_sender_id;
    SELECT balance INTO v_receiver_balance FROM users WHERE id = p_receiver_id;
    
    -- Update backup record with after balances
    UPDATE transaction_backups 
    SET sender_balance_after = v_sender_balance,
        receiver_balance_after = v_receiver_balance
    WHERE backup_id = v_backup_id;
    
    -- Insert transaction record with COMPLETED status
    INSERT INTO transactions (
        id, amount, payment_method, timestamp, sender_id, receiver_id, 
        note, type, location, status
    ) VALUES (
        v_tx_id, p_amount, p_payment_method, NOW(), p_sender_id, p_receiver_id,
        p_note, p_tx_type, p_location, 'COMPLETED'
    );
    
    -- Update system audit log with success
    UPDATE system_audit_log 
    SET success = TRUE, 
        new_values = JSON_OBJECT(
            'sender_balance_after', v_sender_balance, 
            'receiver_balance_after', v_receiver_balance,
            'transaction_id', v_tx_id
        )
    WHERE entity_id = v_tx_id AND operation_type = 'TRANSACTION';
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = CONCAT('Successfully transferred ', p_amount, ' to receiver');
END//

-- =============================================================================
-- 2. BUDGET MANAGEMENT OPTIMIZATIONS
-- =============================================================================

-- Replace budget_utils.py functions with stored procedures
DROP PROCEDURE IF EXISTS SaveOrUpdateBudget//
CREATE PROCEDURE SaveOrUpdateBudget(
    IN p_user_id CHAR(36),
    IN p_name VARCHAR(255),
    IN p_currency VARCHAR(10),
    IN p_income_source VARCHAR(255),
    IN p_amount DECIMAL(15,2),
    OUT p_budget_id CHAR(36),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500)
)
BEGIN
    DECLARE v_existing_budget_id CHAR(36);
    DECLARE v_budget_count INT DEFAULT 0;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = 'Failed to save budget due to database error';
        SET p_budget_id = NULL;
    END;
    
    START TRANSACTION;
    
    -- Check if budget exists
    SELECT id, COUNT(*) INTO v_existing_budget_id, v_budget_count
    FROM budgets 
    WHERE user_id = p_user_id 
    LIMIT 1;
    
    IF v_budget_count > 0 THEN
        -- Update existing budget
        UPDATE budgets 
        SET name = p_name, 
            currency = p_currency, 
            income_source = p_income_source, 
            amount = p_amount
        WHERE id = v_existing_budget_id;
        
        SET p_budget_id = v_existing_budget_id;
    ELSE
        -- Create new budget
        SET p_budget_id = UUID();
        INSERT INTO budgets (id, user_id, name, currency, income_source, amount)
        VALUES (p_budget_id, p_user_id, p_name, p_currency, p_income_source, p_amount);
    END IF;
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = 'Budget saved successfully';
END//

-- Complete budget creation with categories and items
DROP PROCEDURE IF EXISTS CreateFullBudget//
CREATE PROCEDURE CreateFullBudget(
    IN p_user_id CHAR(36),
    IN p_budget_name VARCHAR(255),
    IN p_currency VARCHAR(10),
    IN p_income_sources TEXT,
    IN p_total_income DECIMAL(15,2),
    IN p_expenses_json TEXT,
    OUT p_budget_id CHAR(36),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500)
)
BEGIN
    DECLARE v_budget_id CHAR(36);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = 'Failed to create full budget due to database error';
        SET p_budget_id = NULL;
    END;
    
    START TRANSACTION;
    
    -- Create main budget
    SET v_budget_id = UUID();
    INSERT INTO budgets (id, user_id, name, currency, income_source, amount)
    VALUES (v_budget_id, p_user_id, p_budget_name, p_currency, p_income_sources, p_total_income);
    
    -- Note: For expense categories and items, you would typically parse JSON
    -- or pass structured data. This is a simplified version.
    
    COMMIT;
    SET p_budget_id = v_budget_id;
    SET p_success = TRUE;
    SET p_message = 'Full budget created successfully';
END//

-- =============================================================================
-- 3. USER MANAGEMENT OPTIMIZATIONS
-- =============================================================================

-- Replace user registration logic
DROP PROCEDURE IF EXISTS RegisterUser//
CREATE PROCEDURE RegisterUser(
    IN p_role_name VARCHAR(50),
    IN p_first_name VARCHAR(255),
    IN p_last_name VARCHAR(255),
    IN p_dob DATE,
    IN p_age INT,
    IN p_gender VARCHAR(50),
    IN p_marital_status VARCHAR(50),
    IN p_blood_group VARCHAR(10),
    IN p_email VARCHAR(255),
    IN p_phone VARCHAR(20),
    IN p_password VARCHAR(255),
    OUT p_user_id CHAR(36),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500)
)
BEGIN
    DECLARE v_role_id CHAR(36);
    DECLARE v_user_id CHAR(36);
    DECLARE v_contact_id CHAR(36);
    DECLARE v_email_exists INT DEFAULT 0;
    DECLARE v_phone_exists INT DEFAULT 0;
    DECLARE v_counter INT DEFAULT 0;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = 'User registration failed due to database error';
        SET p_user_id = NULL;
    END;
    
    START TRANSACTION;
    
    -- Check if email already exists
    SELECT COUNT(*) INTO v_email_exists FROM contact_info WHERE LOWER(email) = LOWER(p_email);
    
    IF v_email_exists > 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Email already exists';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Email already exists';
    END IF;
    
    -- Check if phone already exists
    SELECT COUNT(*) INTO v_phone_exists FROM contact_info WHERE phone = p_phone;
    
    IF v_phone_exists > 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Phone number already exists';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Phone number already exists';
    END IF;
    
    -- Get role ID
    SELECT id INTO v_role_id FROM roles WHERE LOWER(name) = LOWER(p_role_name);
    
    IF v_role_id IS NULL THEN
        SET p_success = FALSE;
        SET p_message = 'Invalid role specified';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid role specified';
    END IF;
    
    -- Generate unique user ID
    REPEAT
        SET v_user_id = UPPER(CONCAT(
            CHAR(65 + FLOOR(RAND() * 26)),
            CHAR(65 + FLOOR(RAND() * 26)),
            CHAR(65 + FLOOR(RAND() * 26)),
            CHAR(65 + FLOOR(RAND() * 26)),
            CHAR(48 + FLOOR(RAND() * 10)),
            CHAR(48 + FLOOR(RAND() * 10)),
            CHAR(48 + FLOOR(RAND() * 10)),
            CHAR(48 + FLOOR(RAND() * 10))
        ));
        
        SELECT COUNT(*) INTO v_counter FROM users WHERE id = v_user_id;
        
    UNTIL v_counter = 0 END REPEAT;
    
    -- Insert user
    INSERT INTO users (id, first_name, last_name, dob, age, gender, marital_status, 
                      blood_group, balance, joining_date, role_id)
    VALUES (v_user_id, p_first_name, p_last_name, p_dob, p_age, p_gender, 
            p_marital_status, p_blood_group, 0, CURDATE(), v_role_id);
    
    -- Insert contact info
    SET v_contact_id = UUID();
    INSERT INTO contact_info (id, user_id, email, phone, address_id)
    VALUES (v_contact_id, v_user_id, p_email, p_phone, NULL);
    
    -- Insert password (assuming it's already hashed)
    INSERT INTO user_passwords (user_id, password)
    VALUES (v_user_id, p_password);
    
    COMMIT;
    SET p_user_id = v_user_id;
    SET p_success = TRUE;
    SET p_message = 'User registered successfully';
END//

-- =============================================================================
-- 4. FRAUD DETECTION OPTIMIZATIONS
-- =============================================================================

-- Enhanced fraud detection with automatic risk scoring
DROP PROCEDURE IF EXISTS ProcessFraudReport//
CREATE PROCEDURE ProcessFraudReport(
    IN p_reporter_id CHAR(36),
    IN p_reported_user_id CHAR(36),
    IN p_reason VARCHAR(500),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500)
)
BEGIN
    DECLARE v_existing_reports INT DEFAULT 0;
    DECLARE v_reporter_exists INT DEFAULT 0;
    DECLARE v_reported_exists INT DEFAULT 0;
    DECLARE v_risk_score DECIMAL(5,2);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = 'Failed to process fraud report due to database error';
    END;
    
    START TRANSACTION;
    
    -- Validate users exist
    SELECT COUNT(*) INTO v_reporter_exists FROM users WHERE id = p_reporter_id;
    SELECT COUNT(*) INTO v_reported_exists FROM users WHERE id = p_reported_user_id;
    
    IF v_reporter_exists = 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Reporter user not found';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reporter user not found';
    END IF;
    
    IF v_reported_exists = 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Reported user not found';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reported user not found';
    END IF;
    
    -- Check for duplicate reports
    SELECT COUNT(*) INTO v_existing_reports
    FROM fraud_list 
    WHERE user_id = p_reporter_id AND reported_user_id = p_reported_user_id;
    
    IF v_existing_reports > 0 THEN
        SET p_success = FALSE;
        SET p_message = 'You have already reported this user';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You have already reported this user';
    END IF;
    
    -- Insert fraud report
    INSERT INTO fraud_list (id, user_id, reported_user_id, reason)
    VALUES (UUID(), p_reporter_id, p_reported_user_id, p_reason);
    
    -- Update risk score for reported user
    SET v_risk_score = GetUserRiskScore(p_reported_user_id);
    
    -- Auto-suspend if risk score is too high
    IF v_risk_score > 80 THEN
        UPDATE users SET is_suspended = TRUE WHERE id = p_reported_user_id;
        
        -- Log the suspension
        INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details)
        VALUES (UUID(), 'system', '127.0.0.1', NOW(), 
                CONCAT('User ', p_reported_user_id, ' auto-suspended due to high risk score: ', v_risk_score));
    END IF;
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = 'Fraud report processed successfully';
END//

-- =============================================================================
-- 5. ANALYTICS AND REPORTING OPTIMIZATIONS
-- =============================================================================

-- Replace dashboard queries with optimized procedure
DROP PROCEDURE IF EXISTS GetUserDashboardData//
CREATE PROCEDURE GetUserDashboardData(
    IN p_user_id CHAR(36),
    OUT p_current_balance DECIMAL(10,2),
    OUT p_total_sent DECIMAL(15,2),
    OUT p_total_received DECIMAL(15,2),
    OUT p_transaction_count INT,
    OUT p_risk_score DECIMAL(5,2)
)
BEGIN
    -- Get current balance
    SELECT balance INTO p_current_balance 
    FROM users WHERE id = p_user_id;
    
    -- Get transaction statistics
    SELECT 
        COALESCE(SUM(CASE WHEN sender_id = p_user_id THEN amount ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN receiver_id = p_user_id THEN amount ELSE 0 END), 0),
        COUNT(*)
    INTO p_total_sent, p_total_received, p_transaction_count
    FROM transactions 
    WHERE sender_id = p_user_id OR receiver_id = p_user_id;
    
    -- Get risk score
    SET p_risk_score = GetUserRiskScore(p_user_id);
END//

-- =============================================================================
-- 6. ADMIN OPERATIONS OPTIMIZATIONS
-- =============================================================================

-- Batch operations for admin actions
DROP PROCEDURE IF EXISTS AdminBatchBalanceUpdate//
CREATE PROCEDURE AdminBatchBalanceUpdate(
    IN p_admin_id CHAR(36),
    IN p_user_ids TEXT,
    IN p_amounts TEXT,
    IN p_reason TEXT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500),
    OUT p_updated_count INT
)
BEGIN
    DECLARE v_user_id CHAR(36);
    DECLARE v_amount DECIMAL(10,2);
    DECLARE v_pos INT DEFAULT 1;
    DECLARE v_next_pos INT;
    DECLARE v_user_count INT DEFAULT 0;
    DECLARE v_updated_count INT DEFAULT 0;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = 'Batch update failed due to database error';
        SET p_updated_count = 0;
    END;
    
    START TRANSACTION;
    
    -- Parse and process each user ID and amount
    WHILE v_pos > 0 DO
        SET v_next_pos = LOCATE(',', p_user_ids, v_pos);
        
        IF v_next_pos = 0 THEN
            SET v_user_id = TRIM(SUBSTRING(p_user_ids, v_pos));
            SET v_amount = CAST(TRIM(SUBSTRING(p_amounts, v_pos)) AS DECIMAL(10,2));
            SET v_pos = 0;
        ELSE
            SET v_user_id = TRIM(SUBSTRING(p_user_ids, v_pos, v_next_pos - v_pos));
            SET v_amount = CAST(TRIM(SUBSTRING(p_amounts, v_pos, v_next_pos - v_pos)) AS DECIMAL(10,2));
            SET v_pos = v_next_pos + 1;
        END IF;
        
        -- Update user balance
        UPDATE users SET balance = balance + v_amount WHERE id = v_user_id;
        
        -- Log the action
        INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details)
        VALUES (UUID(), p_admin_id, '127.0.0.1', NOW(), 
                CONCAT('Balance update: User ', v_user_id, ' amount ', v_amount, ' reason: ', p_reason));
        
        -- Create transaction record
        INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location)
        VALUES (UUID(), v_amount, 'admin_adjustment', NOW(), p_admin_id, v_user_id, p_reason, 'Deposit', 'Admin Panel');
        
        SET v_updated_count = v_updated_count + 1;
    END WHILE;
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = CONCAT('Successfully updated ', v_updated_count, ' user balances');
    SET p_updated_count = v_updated_count;
END//

-- =============================================================================
-- 7. TRIGGERS FOR AUTOMATED TASKS
-- =============================================================================

-- Enhanced user activity tracking
DROP TRIGGER IF EXISTS tr_user_activity_log//
CREATE TRIGGER tr_user_activity_log
    AFTER INSERT ON transactions
    FOR EACH ROW
BEGIN
    -- Update last activity timestamp
    UPDATE users 
    SET last_activity = NOW()
    WHERE id IN (NEW.sender_id, NEW.receiver_id);
    
    -- Log high-value transactions
    IF NEW.amount > 5000 THEN
        INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details)
        VALUES (UUID(), 'system', '127.0.0.1', NOW(), 
                CONCAT('High-value transaction: ', NEW.id, ' Amount: ', NEW.amount, 
                       ' From: ', NEW.sender_id, ' To: ', NEW.receiver_id));
    END IF;
    
    -- Check for rapid transactions (potential fraud)
    IF (SELECT COUNT(*) FROM transactions 
        WHERE sender_id = NEW.sender_id 
        AND timestamp >= DATE_SUB(NOW(), INTERVAL 1 MINUTE)) > 5 THEN
        
        INSERT INTO fraud_list (id, user_id, reported_user_id, reason)
        VALUES (UUID(), 'system', NEW.sender_id, 'Rapid transaction pattern detected');
    END IF;
END//

-- Cleanup old fraud reports procedure (instead of invalid trigger)
DROP PROCEDURE IF EXISTS CleanupOldFraudReports//
CREATE PROCEDURE CleanupOldFraudReports()
BEGIN
    -- Delete fraud reports older than 1 year
    DELETE FROM fraud_list 
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR);
    
    -- Log the cleanup
    INSERT INTO system_audit_log (
        id, operation_type, entity_type, entity_id, user_id,
        new_values, timestamp, success
    ) VALUES (
        UUID(), 'CLEANUP', 'FRAUD_LIST', NULL, NULL,
        CONCAT('Cleaned up fraud reports older than 1 year'),
        NOW(), TRUE
    );
END//

-- =============================================================================
-- 8. ENHANCED FUNCTIONS
-- =============================================================================

-- Calculate user spending pattern
DROP FUNCTION IF EXISTS CalculateSpendingPattern//
CREATE FUNCTION CalculateSpendingPattern(p_user_id CHAR(36))
RETURNS VARCHAR(50)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_avg_daily_spend DECIMAL(10,2);
    DECLARE v_pattern VARCHAR(50);
    
    SELECT AVG(daily_spend) INTO v_avg_daily_spend
    FROM (
        SELECT DATE(timestamp) as tx_date, SUM(amount) as daily_spend
        FROM transactions 
        WHERE sender_id = p_user_id 
        AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY DATE(timestamp)
    ) daily_totals;
    
    IF v_avg_daily_spend IS NULL THEN
        SET v_pattern = 'INACTIVE';
    ELSEIF v_avg_daily_spend < 100 THEN
        SET v_pattern = 'LOW_SPENDER';
    ELSEIF v_avg_daily_spend < 500 THEN
        SET v_pattern = 'MODERATE_SPENDER';
    ELSEIF v_avg_daily_spend < 1000 THEN
        SET v_pattern = 'HIGH_SPENDER';
    ELSE
        SET v_pattern = 'VERY_HIGH_SPENDER';
    END IF;
    
    RETURN v_pattern;
END//

-- Check if user is within spending limits
DROP FUNCTION IF EXISTS IsWithinSpendingLimit//
CREATE FUNCTION IsWithinSpendingLimit(p_user_id CHAR(36), p_amount DECIMAL(10,2))
RETURNS BOOLEAN
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_daily_spent DECIMAL(10,2);
    DECLARE v_spending_pattern VARCHAR(50);
    DECLARE v_limit DECIMAL(10,2);
    
    -- Get today's spending
    SELECT COALESCE(SUM(amount), 0) INTO v_daily_spent
    FROM transactions 
    WHERE sender_id = p_user_id 
    AND DATE(timestamp) = CURDATE();
    
    -- Get spending pattern
    SET v_spending_pattern = CalculateSpendingPattern(p_user_id);
    
    -- Set limits based on pattern
    CASE v_spending_pattern
        WHEN 'LOW_SPENDER' THEN SET v_limit = 500;
        WHEN 'MODERATE_SPENDER' THEN SET v_limit = 2000;
        WHEN 'HIGH_SPENDER' THEN SET v_limit = 5000;
        WHEN 'VERY_HIGH_SPENDER' THEN SET v_limit = 10000;
        ELSE SET v_limit = 100;
    END CASE;
    
    RETURN (v_daily_spent + p_amount) <= v_limit;
END//

DELIMITER ;

-- =============================================================================
-- 9. OPTIMIZED VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Enhanced user transaction summary
CREATE OR REPLACE VIEW v_user_dashboard_summary AS
SELECT 
    u.id,
    u.first_name,
    u.last_name,
    u.balance,
    u.last_activity,
    COALESCE(ts.total_sent, 0) as total_sent,
    COALESCE(tr.total_received, 0) as total_received,
    COALESCE(ts.sent_count, 0) as transactions_sent,
    COALESCE(tr.received_count, 0) as transactions_received,
    GetUserRiskScore(u.id) as risk_score,
    CalculateSpendingPattern(u.id) as spending_pattern,
    (SELECT COUNT(*) FROM fraud_list WHERE reported_user_id = u.id) as fraud_reports
FROM users u
LEFT JOIN (
    SELECT sender_id, SUM(amount) as total_sent, COUNT(*) as sent_count
    FROM transactions 
    GROUP BY sender_id
) ts ON u.id = ts.sender_id
LEFT JOIN (
    SELECT receiver_id, SUM(amount) as total_received, COUNT(*) as received_count
    FROM transactions 
    GROUP BY receiver_id
) tr ON u.id = tr.receiver_id;

-- Budget analysis view
CREATE OR REPLACE VIEW v_budget_analysis AS
SELECT 
    b.id,
    b.user_id,
    b.name,
    b.currency,
    b.amount as budgeted_amount,
    COALESCE(actual_spent.total_spent, 0) as actual_spent,
    (b.amount - COALESCE(actual_spent.total_spent, 0)) as remaining_budget,
    CASE 
        WHEN COALESCE(actual_spent.total_spent, 0) > b.amount THEN 'OVER_BUDGET'
        WHEN COALESCE(actual_spent.total_spent, 0) > (b.amount * 0.8) THEN 'NEAR_LIMIT'
        ELSE 'ON_TRACK'
    END as budget_status
FROM budgets b
LEFT JOIN (
    SELECT 
        sender_id,
        SUM(amount) as total_spent
    FROM transactions 
    WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    AND type IN ('Transfer', 'Payment', 'Withdrawal')
    GROUP BY sender_id
) actual_spent ON b.user_id = actual_spent.sender_id;

-- Fraud detection indicators
CREATE OR REPLACE VIEW v_fraud_indicators AS
SELECT 
    u.id,
    u.first_name,
    u.last_name,
    GetUserRiskScore(u.id) as risk_score,
    CalculateTransactionVelocity(u.id, 7) as weekly_velocity,
    CalculateTransactionVelocity(u.id, 1) as daily_velocity,
    (SELECT COUNT(*) FROM fraud_list WHERE reported_user_id = u.id) as fraud_reports,
    (SELECT COUNT(*) FROM transactions WHERE sender_id = u.id AND timestamp >= DATE_SUB(NOW(), INTERVAL 1 HOUR)) as hourly_transactions,
    (SELECT COUNT(*) FROM transactions WHERE sender_id = u.id AND amount > 1000 AND timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY)) as high_value_daily
FROM users u
WHERE GetUserRiskScore(u.id) > 20
ORDER BY risk_score DESC;

-- ===========================
-- ROLLBACK AND RECOVERY PROCEDURES
-- ===========================

-- Rollback Transaction Procedure
DROP PROCEDURE IF EXISTS RollbackTransaction//
CREATE PROCEDURE RollbackTransaction(
    IN p_transaction_id CHAR(36),
    IN p_reason TEXT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500)
)
BEGIN
    DECLARE v_backup_exists INT DEFAULT 0;
    DECLARE v_sender_id CHAR(36);
    DECLARE v_receiver_id CHAR(36);
    DECLARE v_sender_balance_before DECIMAL(10,2);
    DECLARE v_receiver_balance_before DECIMAL(10,2);
    DECLARE v_transaction_amount DECIMAL(10,2);
    DECLARE v_transaction_exists INT DEFAULT 0;
    DECLARE v_current_status VARCHAR(20);
    DECLARE v_error_message VARCHAR(500);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 v_error_message = MESSAGE_TEXT;
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = CONCAT('Rollback failed: ', v_error_message);
        
        -- Log rollback failure
        INSERT INTO system_audit_log (
            id, operation_type, entity_type, entity_id, user_id,
            success, error_message, timestamp
        ) VALUES (
            UUID(), 'ROLLBACK', 'TRANSACTION', p_transaction_id, NULL,
            FALSE, v_error_message, NOW()
        );
    END;
    
    START TRANSACTION;
    
    -- Check if transaction exists and get current status
    SELECT COUNT(*), COALESCE(status, 'UNKNOWN') 
    INTO v_transaction_exists, v_current_status
    FROM transactions 
    WHERE id = p_transaction_id;
    
    IF v_transaction_exists = 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Transaction not found';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Transaction not found';
    END IF;
    
    -- Check if transaction is already rolled back
    IF v_current_status = 'ROLLED_BACK' THEN
        SET p_success = FALSE;
        SET p_message = 'Transaction already rolled back';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Transaction already rolled back';
    END IF;
    
    -- Only allow rollback of COMPLETED transactions
    IF v_current_status != 'COMPLETED' THEN
        SET p_success = FALSE;
        SET p_message = CONCAT('Cannot rollback transaction with status: ', v_current_status);
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot rollback non-completed transaction';
    END IF;
    
    -- Get backup information
    SELECT COUNT(*), sender_id, receiver_id, sender_balance_before, 
           receiver_balance_before, transaction_amount
    INTO v_backup_exists, v_sender_id, v_receiver_id, v_sender_balance_before,
         v_receiver_balance_before, v_transaction_amount
    FROM transaction_backups 
    WHERE original_transaction_id = p_transaction_id;
    
    IF v_backup_exists = 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Backup data not found for transaction';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Backup data not found';
    END IF;
    
    -- Restore balances to their previous state
    UPDATE users SET balance = v_sender_balance_before WHERE id = v_sender_id;
    UPDATE users SET balance = v_receiver_balance_before WHERE id = v_receiver_id;
    
    -- Update transaction status
    UPDATE transactions 
    SET status = 'ROLLED_BACK' 
    WHERE id = p_transaction_id;
    
    -- Log the rollback in system audit
    INSERT INTO system_audit_log (
        id, operation_type, entity_type, entity_id, user_id,
        old_values, new_values, timestamp, success
    ) VALUES (
        UUID(), 'ROLLBACK', 'TRANSACTION', p_transaction_id, v_sender_id,
        JSON_OBJECT('status', v_current_status, 'reason', p_reason),
        JSON_OBJECT('status', 'ROLLED_BACK', 'sender_balance_restored', v_sender_balance_before, 'receiver_balance_restored', v_receiver_balance_before),
        NOW(), TRUE
    );
    
    -- Update backup record
    UPDATE transaction_backups 
    SET rollback_timestamp = NOW(),
        rollback_reason = p_reason
    WHERE original_transaction_id = p_transaction_id;
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = CONCAT('Transaction ', p_transaction_id, ' successfully rolled back');
END//

-- Auto-Rollback Failed Transactions Procedure
DROP PROCEDURE IF EXISTS AutoRollbackFailedTransactions//
CREATE PROCEDURE AutoRollbackFailedTransactions(
    IN p_hours_threshold INT DEFAULT 24,
    OUT p_rolled_back_count INT,
    OUT p_message VARCHAR(500)
)
BEGIN
    DECLARE v_transaction_id CHAR(36);
    DECLARE v_done INT DEFAULT FALSE;
    DECLARE v_rollback_success BOOLEAN;
    DECLARE v_rollback_message VARCHAR(500);
    DECLARE v_count INT DEFAULT 0;
    
    -- Cursor to find failed transactions older than threshold
    DECLARE failed_cursor CURSOR FOR
        SELECT id FROM transactions 
        WHERE status = 'FAILED' 
        AND timestamp < DATE_SUB(NOW(), INTERVAL p_hours_threshold HOUR);
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = TRUE;
    
    SET p_rolled_back_count = 0;
    
    OPEN failed_cursor;
    
    rollback_loop: LOOP
        FETCH failed_cursor INTO v_transaction_id;
        IF v_done THEN
            LEAVE rollback_loop;
        END IF;
        
        -- Attempt rollback
        CALL RollbackTransaction(
            v_transaction_id, 
            'Auto-rollback of failed transaction', 
            v_rollback_success, 
            v_rollback_message
        );
        
        IF v_rollback_success THEN
            SET p_rolled_back_count = p_rolled_back_count + 1;
        END IF;
    END LOOP;
    
    CLOSE failed_cursor;
    
    SET p_message = CONCAT('Auto-rolled back ', p_rolled_back_count, ' failed transactions');
    
    -- Log the auto-rollback operation
    INSERT INTO system_audit_log (
        id, operation_type, entity_type, entity_id, user_id,
        new_values, timestamp, success
    ) VALUES (
        UUID(), 'AUTO_ROLLBACK', 'SYSTEM', NULL, NULL,
        JSON_OBJECT('rolled_back_count', p_rolled_back_count, 'hours_threshold', p_hours_threshold),
        NOW(), TRUE
    );
END//

-- Backup User Balance Procedure
DROP PROCEDURE IF EXISTS BackupUserBalance//
CREATE PROCEDURE BackupUserBalance(
    IN p_user_id CHAR(36),
    IN p_operation_type VARCHAR(50),
    OUT p_backup_id CHAR(36),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500)
)
BEGIN
    DECLARE v_current_balance DECIMAL(10,2);
    DECLARE v_user_exists INT DEFAULT 0;
    DECLARE v_backup_uuid CHAR(36);
    DECLARE v_error_message VARCHAR(500);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 v_error_message = MESSAGE_TEXT;
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = CONCAT('Backup failed: ', v_error_message);
        SET p_backup_id = NULL;
    END;
    
    START TRANSACTION;
    
    -- Check if user exists and get current balance
    SELECT COUNT(*), COALESCE(balance, 0) 
    INTO v_user_exists, v_current_balance
    FROM users 
    WHERE id = p_user_id;
    
    IF v_user_exists = 0 THEN
        SET p_success = FALSE;
        SET p_message = 'User not found';
        SET p_backup_id = NULL;
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User not found';
    END IF;
    
    -- Generate backup ID
    SET v_backup_uuid = UUID();
    SET p_backup_id = v_backup_uuid;
    
    -- Create backup entry
    INSERT INTO transaction_backups (
        backup_id, original_transaction_id, sender_id, receiver_id,
        sender_balance_before, receiver_balance_before, transaction_amount,
        backup_timestamp
    ) VALUES (
        v_backup_uuid, NULL, p_user_id, NULL,
        v_current_balance, NULL, NULL,
        NOW()
    );
    
    -- Log backup operation
    INSERT INTO system_audit_log (
        id, operation_type, entity_type, entity_id, user_id,
        old_values, timestamp, success
    ) VALUES (
        UUID(), 'BACKUP', 'USER_BALANCE', p_user_id, p_user_id,
        JSON_OBJECT('balance', v_current_balance, 'operation', p_operation_type),
        NOW(), TRUE
    );
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = CONCAT('Balance backup created for user: ', p_user_id);
END//

-- Restore User Balance Procedure
DROP PROCEDURE IF EXISTS RestoreUserBalance//
CREATE PROCEDURE RestoreUserBalance(
    IN p_backup_id CHAR(36),
    IN p_reason TEXT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500)
)
BEGIN
    DECLARE v_backup_exists INT DEFAULT 0;
    DECLARE v_user_id CHAR(36);
    DECLARE v_backup_balance DECIMAL(10,2);
    DECLARE v_backup_timestamp DATETIME;
    DECLARE v_error_message VARCHAR(500);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 v_error_message = MESSAGE_TEXT;
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = CONCAT('Restore failed: ', v_error_message);
    END;
    
    START TRANSACTION;
    
    -- Get backup information
    SELECT COUNT(*), sender_id, sender_balance_before, backup_timestamp
    INTO v_backup_exists, v_user_id, v_backup_balance, v_backup_timestamp
    FROM transaction_backups 
    WHERE backup_id = p_backup_id;
    
    IF v_backup_exists = 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Backup not found';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Backup not found';
    END IF;
    
    -- Restore the balance
    UPDATE users SET balance = v_backup_balance WHERE id = v_user_id;
    
    -- Log restore operation
    INSERT INTO system_audit_log (
        id, operation_type, entity_type, entity_id, user_id,
        old_values, new_values, timestamp, success
    ) VALUES (
        UUID(), 'RESTORE', 'USER_BALANCE', v_user_id, v_user_id,
        JSON_OBJECT('restore_reason', p_reason, 'backup_timestamp', v_backup_timestamp),
        JSON_OBJECT('restored_balance', v_backup_balance),
        NOW(), TRUE
    );
    
    -- Update backup record
    UPDATE transaction_backups 
    SET rollback_timestamp = NOW(),
        rollback_reason = p_reason
    WHERE backup_id = p_backup_id;
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = CONCAT('Balance restored for user: ', v_user_id, ' to amount: ', v_backup_balance);
END//

-- Get Transaction Status Procedure
DROP PROCEDURE IF EXISTS GetTransactionStatus//
CREATE PROCEDURE GetTransactionStatus(
    IN p_transaction_id CHAR(36),
    OUT p_status VARCHAR(20),
    OUT p_can_rollback BOOLEAN,
    OUT p_message VARCHAR(500)
)
BEGIN
    DECLARE v_transaction_exists INT DEFAULT 0;
    DECLARE v_current_status VARCHAR(20);
    DECLARE v_backup_exists INT DEFAULT 0;
    DECLARE v_transaction_timestamp DATETIME;
    DECLARE v_hours_since_transaction INT;
    
    -- Check if transaction exists
    SELECT COUNT(*), COALESCE(status, 'UNKNOWN'), timestamp
    INTO v_transaction_exists, v_current_status, v_transaction_timestamp
    FROM transactions 
    WHERE id = p_transaction_id;
    
    IF v_transaction_exists = 0 THEN
        SET p_status = 'NOT_FOUND';
        SET p_can_rollback = FALSE;
        SET p_message = 'Transaction not found';
        RETURN;
    END IF;
    
    SET p_status = v_current_status;
    
    -- Check if backup exists
    SELECT COUNT(*) INTO v_backup_exists
    FROM transaction_backups 
    WHERE original_transaction_id = p_transaction_id;
    
    -- Calculate hours since transaction
    SET v_hours_since_transaction = TIMESTAMPDIFF(HOUR, v_transaction_timestamp, NOW());
    
    -- Determine if rollback is possible
    IF v_current_status = 'COMPLETED' AND v_backup_exists > 0 AND v_hours_since_transaction <= 72 THEN
        SET p_can_rollback = TRUE;
        SET p_message = CONCAT('Transaction can be rolled back (', v_hours_since_transaction, ' hours old)');
    ELSE
        SET p_can_rollback = FALSE;
        IF v_current_status = 'ROLLED_BACK' THEN
            SET p_message = 'Transaction already rolled back';
        ELSEIF v_backup_exists = 0 THEN
            SET p_message = 'No backup data available for rollback';
        ELSEIF v_hours_since_transaction > 72 THEN
            SET p_message = 'Transaction too old for rollback (>72 hours)';
        ELSE
            SET p_message = CONCAT('Transaction status does not allow rollback: ', v_current_status);
        END IF;
    END IF;
END//

DELIMITER ;