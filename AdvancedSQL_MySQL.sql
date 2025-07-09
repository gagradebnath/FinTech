

USE fin_guard;


DELIMITER //


DROP PROCEDURE IF EXISTS ProcessMoneyTransfer//
CREATE PROCEDURE ProcessMoneyTransfer(
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
    DECLARE v_sender_exists INT DEFAULT 0;
    DECLARE v_receiver_exists INT DEFAULT 0;
    DECLARE v_is_fraud_flagged INT DEFAULT 0;
    DECLARE v_tx_id CHAR(36);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = 'Transaction failed due to database error';
        SET p_transaction_id = NULL;
    END;
    
    -- Generate transaction ID
    SET v_tx_id = UUID();
    SET p_transaction_id = v_tx_id;
    
    -- Start transaction
    START TRANSACTION;
    
    -- Validate inputs
    IF p_amount <= 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Amount must be greater than zero';
        ROLLBACK;
        LEAVE ProcessMoneyTransfer;
    END IF;
    
    IF p_sender_id = p_receiver_id THEN
        SET p_success = FALSE;
        SET p_message = 'Cannot transfer money to yourself';
        ROLLBACK;
        LEAVE ProcessMoneyTransfer;
    END IF;
    
    -- Check if sender exists and get balance
    SELECT COUNT(*), COALESCE(balance, 0) 
    INTO v_sender_exists, v_sender_balance
    FROM users 
    WHERE id = p_sender_id;
    
    IF v_sender_exists = 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Sender not found';
        ROLLBACK;
        LEAVE ProcessMoneyTransfer;
    END IF;
    
    -- Check if receiver exists
    SELECT COUNT(*) INTO v_receiver_exists FROM users WHERE id = p_receiver_id;
    
    IF v_receiver_exists = 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Receiver not found';
        ROLLBACK;
        LEAVE ProcessMoneyTransfer;
    END IF;
    
    -- Check if sender has sufficient balance
    IF v_sender_balance < p_amount THEN
        SET p_success = FALSE;
        SET p_message = 'Insufficient balance';
        ROLLBACK;
        LEAVE ProcessMoneyTransfer;
    END IF;
    
    -- Check if receiver is fraud flagged
    SELECT COUNT(*) INTO v_is_fraud_flagged 
    FROM fraud_list 
    WHERE reported_user_id = p_receiver_id;
    
    IF v_is_fraud_flagged > 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Cannot transfer to fraud-flagged user';
        ROLLBACK;
        LEAVE ProcessMoneyTransfer;
    END IF;
    
    -- Perform the transfer
    UPDATE users SET balance = balance - p_amount WHERE id = p_sender_id;
    UPDATE users SET balance = balance + p_amount WHERE id = p_receiver_id;
    
    -- Insert transaction record
    INSERT INTO transactions (
        id, amount, payment_method, timestamp, sender_id, receiver_id, 
        note, type, location
    ) VALUES (
        v_tx_id, p_amount, p_payment_method, NOW(), p_sender_id, p_receiver_id,
        p_note, p_tx_type, p_location
    );
    
    -- Success
    COMMIT;
    SET p_success = TRUE;
    SET p_message = CONCAT('Successfully transferred ', p_amount, ' to receiver');
    
END//

-- Procedure: Get User Transaction History with Analytics
DROP PROCEDURE IF EXISTS GetUserTransactionHistory//
CREATE PROCEDURE GetUserTransactionHistory(
    IN p_user_id CHAR(36),
    IN p_limit INT,
    IN p_offset INT
)
BEGIN
    SELECT 
        t.id,
        t.amount,
        t.payment_method,
        t.timestamp,
        t.type,
        t.location,
        t.note,
        CASE 
            WHEN t.sender_id = p_user_id THEN 'OUTGOING'
            WHEN t.receiver_id = p_user_id THEN 'INCOMING'
            ELSE 'UNKNOWN'
        END as direction,
        CASE 
            WHEN t.sender_id = p_user_id THEN CONCAT(r.first_name, ' ', r.last_name)
            WHEN t.receiver_id = p_user_id THEN CONCAT(s.first_name, ' ', s.last_name)
        END as other_party,
        -- Running balance calculation
        @running_balance := @running_balance + 
            CASE 
                WHEN t.sender_id = p_user_id THEN -t.amount
                WHEN t.receiver_id = p_user_id THEN t.amount
                ELSE 0
            END as running_balance
    FROM transactions t
    LEFT JOIN users s ON t.sender_id = s.id
    LEFT JOIN users r ON t.receiver_id = r.id
    CROSS JOIN (SELECT @running_balance := (SELECT balance FROM users WHERE id = p_user_id)) rb
    WHERE (t.sender_id = p_user_id OR t.receiver_id = p_user_id)
    ORDER BY t.timestamp DESC
    LIMIT p_limit OFFSET p_offset;
END//

-- Procedure: Calculate User Statistics
DROP PROCEDURE IF EXISTS CalculateUserStatistics//
CREATE PROCEDURE CalculateUserStatistics(
    IN p_user_id CHAR(36),
    OUT p_total_sent DECIMAL(15,2),
    OUT p_total_received DECIMAL(15,2),
    OUT p_transaction_count INT,
    OUT p_avg_transaction DECIMAL(10,2),
    OUT p_last_transaction_date DATETIME
)
BEGIN
    -- Calculate total sent
    SELECT COALESCE(SUM(amount), 0) INTO p_total_sent
    FROM transactions 
    WHERE sender_id = p_user_id;
    
    -- Calculate total received  
    SELECT COALESCE(SUM(amount), 0) INTO p_total_received
    FROM transactions 
    WHERE receiver_id = p_user_id;
    
    -- Calculate transaction count
    SELECT COUNT(*) INTO p_transaction_count
    FROM transactions 
    WHERE sender_id = p_user_id OR receiver_id = p_user_id;
    
    -- Calculate average transaction amount
    SELECT COALESCE(AVG(amount), 0) INTO p_avg_transaction
    FROM transactions 
    WHERE sender_id = p_user_id OR receiver_id = p_user_id;
    
    -- Get last transaction date
    SELECT MAX(timestamp) INTO p_last_transaction_date
    FROM transactions 
    WHERE sender_id = p_user_id OR receiver_id = p_user_id;
    
END//

-- Procedure: Bulk Balance Update for Admin
DROP PROCEDURE IF EXISTS BulkBalanceUpdate//
CREATE PROCEDURE BulkBalanceUpdate(
    IN p_admin_id CHAR(36),
    IN p_user_ids TEXT,
    IN p_amounts TEXT,
    IN p_reason TEXT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500)
)
BEGIN
    DECLARE v_user_id CHAR(36);
    DECLARE v_amount DECIMAL(10,2);
    DECLARE v_done INT DEFAULT FALSE;
    DECLARE v_count INT DEFAULT 0;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = 'Bulk update failed due to database error';
    END;
    
    START TRANSACTION;
    
    -- Note: This is a simplified version. In production, you'd want to properly parse the CSV strings
    -- For now, we'll assume single user update
    SET v_user_id = p_user_ids;
    SET v_amount = CAST(p_amounts AS DECIMAL(10,2));
    
    -- Update user balance
    UPDATE users SET balance = balance + v_amount WHERE id = v_user_id;
    
    -- Log admin action
    INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details)
    VALUES (UUID(), p_admin_id, '127.0.0.1', NOW(), 
            CONCAT('Bulk balance update: User ', v_user_id, ' amount ', v_amount, ' reason: ', p_reason));
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = 'Bulk update completed successfully';
    
END//

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Calculate Account Age in Days
DROP FUNCTION IF EXISTS CalculateAccountAge//
CREATE FUNCTION CalculateAccountAge(p_user_id CHAR(36))
RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_joining_date DATE;
    DECLARE v_age_days INT;
    
    SELECT joining_date INTO v_joining_date 
    FROM users 
    WHERE id = p_user_id;
    
    IF v_joining_date IS NULL THEN
        RETURN 0;
    END IF;
    
    SET v_age_days = DATEDIFF(CURDATE(), v_joining_date);
    
    RETURN v_age_days;
END//

-- Function: Calculate Transaction Velocity (transactions per day)
DROP FUNCTION IF EXISTS CalculateTransactionVelocity//
CREATE FUNCTION CalculateTransactionVelocity(p_user_id CHAR(36), p_days INT)
RETURNS DECIMAL(10,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_transaction_count INT;
    DECLARE v_velocity DECIMAL(10,2);
    
    SELECT COUNT(*) INTO v_transaction_count
    FROM transactions 
    WHERE (sender_id = p_user_id OR receiver_id = p_user_id)
    AND timestamp >= DATE_SUB(NOW(), INTERVAL p_days DAY);
    
    SET v_velocity = v_transaction_count / p_days;
    
    RETURN v_velocity;
END//

-- Function: Get User Risk Score
DROP FUNCTION IF EXISTS GetUserRiskScore//
CREATE FUNCTION GetUserRiskScore(p_user_id CHAR(36))
RETURNS DECIMAL(5,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_fraud_reports INT DEFAULT 0;
    DECLARE v_high_amount_txs INT DEFAULT 0;
    DECLARE v_account_age INT DEFAULT 0;
    DECLARE v_risk_score DECIMAL(5,2) DEFAULT 0.0;
    
    -- Count fraud reports against this user
    SELECT COUNT(*) INTO v_fraud_reports
    FROM fraud_list 
    WHERE reported_user_id = p_user_id;
    
    -- Count high amount transactions (>1000) in last 30 days
    SELECT COUNT(*) INTO v_high_amount_txs
    FROM transactions 
    WHERE sender_id = p_user_id 
    AND amount > 1000
    AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY);
    
    -- Get account age
    SET v_account_age = CalculateAccountAge(p_user_id);
    
    -- Calculate risk score (0-100 scale)
    SET v_risk_score = (v_fraud_reports * 30) + (v_high_amount_txs * 10);
    
    -- Reduce risk for older accounts
    IF v_account_age > 365 THEN
        SET v_risk_score = v_risk_score * 0.8;
    ELSEIF v_account_age > 180 THEN
        SET v_risk_score = v_risk_score * 0.9;
    END IF;
    
    -- Cap at 100
    IF v_risk_score > 100 THEN
        SET v_risk_score = 100;
    END IF;
    
    RETURN v_risk_score;
END//

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger: Auto-log admin actions on user table changes
DROP TRIGGER IF EXISTS tr_users_admin_log//
CREATE TRIGGER tr_users_admin_log
    AFTER UPDATE ON users
    FOR EACH ROW
BEGIN
    -- Only log if balance or role changed
    IF OLD.balance != NEW.balance OR OLD.role_id != NEW.role_id THEN
        INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details)
        VALUES (UUID(), 'system', '127.0.0.1', NOW(), 
                CONCAT('User ', NEW.id, ' - Balance changed from ', OLD.balance, ' to ', NEW.balance,
                       ', Role changed from ', COALESCE(OLD.role_id, 'NULL'), ' to ', COALESCE(NEW.role_id, 'NULL')));
    END IF;
END//

-- Trigger: Validate transaction amounts
DROP TRIGGER IF EXISTS tr_transactions_validate//
CREATE TRIGGER tr_transactions_validate
    BEFORE INSERT ON transactions
    FOR EACH ROW
BEGIN
    -- Ensure amount is positive
    IF NEW.amount <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Transaction amount must be positive';
    END IF;
    
    -- Ensure sender and receiver are different
    IF NEW.sender_id = NEW.receiver_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Sender and receiver cannot be the same';
    END IF;
    
    -- Set timestamp if not provided
    IF NEW.timestamp IS NULL THEN
        SET NEW.timestamp = NOW();
    END IF;
END//

-- Trigger: Auto-create blockchain record for transactions
DROP TRIGGER IF EXISTS tr_transactions_blockchain//
CREATE TRIGGER tr_transactions_blockchain
    AFTER INSERT ON transactions
    FOR EACH ROW
BEGIN
    DECLARE v_prev_hash VARCHAR(255) DEFAULT '';
    DECLARE v_block_index INT DEFAULT 0;
    DECLARE v_new_hash VARCHAR(255);
    
    -- Get previous block info
    SELECT COALESCE(MAX(`index`), -1), COALESCE(hash, '') 
    INTO v_block_index, v_prev_hash
    FROM blockchain 
    ORDER BY `index` DESC 
    LIMIT 1;
    
    SET v_block_index = v_block_index + 1;
    
    -- Create simple hash (in production, use proper cryptographic hash)
    SET v_new_hash = SHA2(CONCAT(v_block_index, NEW.id, NEW.amount, NEW.timestamp, v_prev_hash), 256);
    
    -- Insert blockchain transaction record
    INSERT INTO blockchain_transactions (id, user_id, amount, current_balance, method, timestamp)
    VALUES (UUID(), NEW.sender_id, NEW.amount, 
            (SELECT balance FROM users WHERE id = NEW.sender_id), 
            NEW.payment_method, NEW.timestamp);
    
    -- Insert blockchain record
    INSERT INTO blockchain (id, `index`, type, timestamp, previous_hash, hash, transaction_id)
    VALUES (UUID(), v_block_index, 'TRANSACTION', NEW.timestamp, v_prev_hash, v_new_hash, 
            (SELECT id FROM blockchain_transactions ORDER BY timestamp DESC LIMIT 1));
END//

-- Trigger: Update user last activity on transaction
DROP TRIGGER IF EXISTS tr_update_user_activity//
CREATE TRIGGER tr_update_user_activity
    AFTER INSERT ON transactions
    FOR EACH ROW
BEGIN

    INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details)
    VALUES (UUID(), 'system', '127.0.0.1', NOW(), 
            CONCAT('Transaction activity - Sender: ', NEW.sender_id, ', Receiver: ', NEW.receiver_id, ', Amount: ', NEW.amount));
END//

-- Reset delimiter
DELIMITER ;


-- View: User Transaction Summary
CREATE OR REPLACE VIEW v_user_transaction_summary AS
SELECT 
    u.id,
    u.first_name,
    u.last_name,
    u.balance,
    COUNT(DISTINCT t_sent.id) as transactions_sent,
    COUNT(DISTINCT t_received.id) as transactions_received,
    COALESCE(SUM(DISTINCT t_sent.amount), 0) as total_sent,
    COALESCE(SUM(DISTINCT t_received.amount), 0) as total_received,
    COALESCE(MAX(GREATEST(t_sent.timestamp, t_received.timestamp)), '1970-01-01') as last_transaction_date,
    GetUserRiskScore(u.id) as risk_score
FROM users u
LEFT JOIN transactions t_sent ON u.id = t_sent.sender_id
LEFT JOIN transactions t_received ON u.id = t_received.receiver_id
GROUP BY u.id, u.first_name, u.last_name, u.balance;

-- View: Daily Transaction Analytics
CREATE OR REPLACE VIEW v_daily_transaction_analytics AS
SELECT 
    DATE(timestamp) as transaction_date,
    COUNT(*) as total_transactions,
    SUM(amount) as total_volume,
    AVG(amount) as avg_transaction_amount,
    MIN(amount) as min_transaction,
    MAX(amount) as max_transaction,
    COUNT(DISTINCT sender_id) as unique_senders,
    COUNT(DISTINCT receiver_id) as unique_receivers,
    COUNT(CASE WHEN type = 'Transfer' THEN 1 END) as transfers,
    COUNT(CASE WHEN type = 'Deposit' THEN 1 END) as deposits,
    COUNT(CASE WHEN type = 'Withdrawal' THEN 1 END) as withdrawals
FROM transactions
WHERE timestamp >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY DATE(timestamp)
ORDER BY transaction_date DESC;

-- View: High Risk Users
CREATE OR REPLACE VIEW v_high_risk_users AS
SELECT 
    u.id,
    u.first_name,
    u.last_name,
    u.balance,
    GetUserRiskScore(u.id) as risk_score,
    COUNT(DISTINCT f.id) as fraud_reports,
    CalculateTransactionVelocity(u.id, 7) as weekly_velocity,
    CalculateAccountAge(u.id) as account_age_days
FROM users u
LEFT JOIN fraud_list f ON u.id = f.reported_user_id
WHERE GetUserRiskScore(u.id) > 30
GROUP BY u.id, u.first_name, u.last_name, u.balance
ORDER BY risk_score DESC;

-- Complex Query: Monthly Transaction Report with Running Totals
-- This would be called from Python code
/*
WITH monthly_data AS (
    SELECT 
        YEAR(timestamp) as year,
        MONTH(timestamp) as month,
        COUNT(*) as transaction_count,
        SUM(amount) as total_volume,
        AVG(amount) as avg_amount
    FROM transactions
    GROUP BY YEAR(timestamp), MONTH(timestamp)
),
running_totals AS (
    SELECT 
        year,
        month,
        transaction_count,
        total_volume,
        avg_amount,
        SUM(transaction_count) OVER (ORDER BY year, month) as cumulative_transactions,
        SUM(total_volume) OVER (ORDER BY year, month) as cumulative_volume
    FROM monthly_data
)
SELECT * FROM running_totals
ORDER BY year DESC, month DESC;
*/