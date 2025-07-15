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

-- Reset delimiter
DELIMITER ;

-- Final status message
SELECT 'FinGuard PL/SQL Deployment Completed Successfully!' as message;
