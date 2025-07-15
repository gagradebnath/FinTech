-- MySQL 5.7+ Compatible PL/SQL Optimizations for FinGuard
-- This version removes JSON functions and uses TEXT fields instead

DELIMITER //

-- =============================================================================
-- 1. ENHANCED MONEY TRANSFER PROCEDURE
-- =============================================================================

-- Enhanced Money Transfer Procedure with rollback functionality
DROP PROCEDURE IF EXISTS ProcessMoneyTransferEnhanced//
CREATE PROCEDURE ProcessMoneyTransferEnhanced(
    IN p_sender_id CHAR(36),
    IN p_receiver_id CHAR(36),
    IN p_amount DECIMAL(10,2),
    IN p_payment_method VARCHAR(100),
    IN p_note TEXT,
    IN p_tx_type VARCHAR(20),
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
    
    -- Enhanced validation
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
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = CONCAT('Successfully transferred ', p_amount, ' to receiver');
END//

-- =============================================================================
-- 2. ROLLBACK PROCEDURES
-- =============================================================================

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
        CONCAT('status:', v_current_status, ',reason:', p_reason),
        CONCAT('status:ROLLED_BACK,sender_balance_restored:', v_sender_balance_before, ',receiver_balance_restored:', v_receiver_balance_before),
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
        CONCAT('balance:', v_current_balance, ',operation:', p_operation_type),
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
        CONCAT('restore_reason:', p_reason, ',backup_timestamp:', v_backup_timestamp),
        CONCAT('restored_balance:', v_backup_balance),
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
        CONCAT('rolled_back_count:', p_rolled_back_count, ',hours_threshold:', p_hours_threshold),
        NOW(), TRUE
    );
END//

-- =============================================================================
-- 3. BASIC FUNCTIONS
-- =============================================================================

-- Get User Risk Score Function
DROP FUNCTION IF EXISTS GetUserRiskScore//
CREATE FUNCTION GetUserRiskScore(p_user_id CHAR(36))
RETURNS DECIMAL(5,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_risk_score DECIMAL(5,2) DEFAULT 0.0;
    DECLARE v_fraud_reports INT DEFAULT 0;
    DECLARE v_transaction_count INT DEFAULT 0;
    DECLARE v_high_value_transactions INT DEFAULT 0;
    
    -- Check fraud reports
    SELECT COUNT(*) INTO v_fraud_reports
    FROM fraud_list 
    WHERE reported_user_id = p_user_id;
    
    -- Count transactions in last 30 days
    SELECT COUNT(*) INTO v_transaction_count
    FROM transactions 
    WHERE sender_id = p_user_id 
    AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY);
    
    -- Count high-value transactions
    SELECT COUNT(*) INTO v_high_value_transactions
    FROM transactions 
    WHERE sender_id = p_user_id 
    AND amount > 1000 
    AND timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY);
    
    -- Calculate risk score
    SET v_risk_score = 
        (v_fraud_reports * 25.0) +
        (CASE WHEN v_transaction_count > 50 THEN 15.0 ELSE 0.0 END) +
        (v_high_value_transactions * 10.0);
    
    -- Cap at 100
    IF v_risk_score > 100 THEN
        SET v_risk_score = 100.0;
    END IF;
    
    RETURN v_risk_score;
END//

DELIMITER ;

-- Final message
SELECT 'MySQL 5.7+ Compatible PL/SQL Optimizations deployed successfully!' as message;
SELECT 'All rollback procedures and functions are now available.' as status;
