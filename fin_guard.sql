/*
 Navicat Premium Dump SQL

 Source Server         : fin_guard
 Source Server Type    : MySQL
 Source Server Version : 80042 (8.0.42)
 Source Host           : localhost:3306
 Source Schema         : fin_guard

 Target Server Type    : MySQL
 Target Server Version : 80042 (8.0.42)
 File Encoding         : 65001

 Date: 19/07/2025 19:59:47
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for addresses
-- ----------------------------
DROP TABLE IF EXISTS `addresses`;
CREATE TABLE `addresses`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `country` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `division` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `district` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `area` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for admin_logs
-- ----------------------------
DROP TABLE IF EXISTS `admin_logs`;
CREATE TABLE `admin_logs`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `admin_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `action` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `ip_address` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT NULL,
  `details` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_admin_id`(`admin_id` ASC) USING BTREE,
  INDEX `idx_timestamp`(`timestamp` ASC) USING BTREE,
  CONSTRAINT `admin_logs_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for blockchain
-- ----------------------------
DROP TABLE IF EXISTS `blockchain`;
CREATE TABLE `blockchain`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `index` int NULL DEFAULT NULL,
  `type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT NULL,
  `previous_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `transaction_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_transaction_id`(`transaction_id` ASC) USING BTREE,
  INDEX `idx_index`(`index` ASC) USING BTREE,
  CONSTRAINT `blockchain_ibfk_1` FOREIGN KEY (`transaction_id`) REFERENCES `transactions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for blockchain_transactions
-- ----------------------------
DROP TABLE IF EXISTS `blockchain_transactions`;
CREATE TABLE `blockchain_transactions`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `amount` decimal(15, 2) NULL DEFAULT NULL,
  `current_balance` decimal(15, 2) NULL DEFAULT NULL,
  `method` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_timestamp`(`timestamp` ASC) USING BTREE,
  CONSTRAINT `blockchain_transactions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for budget_expense_categories
-- ----------------------------
DROP TABLE IF EXISTS `budget_expense_categories`;
CREATE TABLE `budget_expense_categories`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `budget_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `category_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `amount` decimal(15, 2) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_budget_id`(`budget_id` ASC) USING BTREE,
  CONSTRAINT `budget_expense_categories_ibfk_1` FOREIGN KEY (`budget_id`) REFERENCES `budgets` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for budget_expense_items
-- ----------------------------
DROP TABLE IF EXISTS `budget_expense_items`;
CREATE TABLE `budget_expense_items`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `amount` decimal(10, 2) NULL DEFAULT NULL,
  `details` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_category_id`(`category_id` ASC) USING BTREE,
  CONSTRAINT `budget_expense_items_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `budget_expense_categories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for budgets
-- ----------------------------
DROP TABLE IF EXISTS `budgets`;
CREATE TABLE `budgets`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `currency` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `income_source` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `amount` decimal(15, 2) NULL DEFAULT NULL,
  `start_date` date NULL DEFAULT NULL,
  `end_date` date NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `budgets_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for contact_info
-- ----------------------------
DROP TABLE IF EXISTS `contact_info`;
CREATE TABLE `contact_info`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `address_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC) USING BTREE,
  UNIQUE INDEX `email`(`email` ASC) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_address_id`(`address_id` ASC) USING BTREE,
  CONSTRAINT `contact_info_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `contact_info_ibfk_2` FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for failed_transactions
-- ----------------------------
DROP TABLE IF EXISTS `failed_transactions`;
CREATE TABLE `failed_transactions`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `attempted_transaction_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `sender_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `receiver_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `amount` decimal(10, 2) NULL DEFAULT NULL,
  `payment_method` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `failure_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `failure_timestamp` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `retry_count` int NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for fraud_list
-- ----------------------------
DROP TABLE IF EXISTS `fraud_list`;
CREATE TABLE `fraud_list`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `reported_user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `reason` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_reported_user_id`(`reported_user_id` ASC) USING BTREE,
  CONSTRAINT `fraud_list_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fraud_list_ibfk_2` FOREIGN KEY (`reported_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for permissions
-- ----------------------------
DROP TABLE IF EXISTS `permissions`;
CREATE TABLE `permissions`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for role_permissions
-- ----------------------------
DROP TABLE IF EXISTS `role_permissions`;
CREATE TABLE `role_permissions`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `role_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `permission_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_role_id`(`role_id` ASC) USING BTREE,
  INDEX `idx_permission_id`(`permission_id` ASC) USING BTREE,
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for system_audit_log
-- ----------------------------
DROP TABLE IF EXISTS `system_audit_log`;
CREATE TABLE `system_audit_log`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `operation_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `entity_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `entity_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `old_values` json NULL,
  `new_values` json NULL,
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `ip_address` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `success` tinyint(1) NULL DEFAULT 1,
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for transaction_backups
-- ----------------------------
DROP TABLE IF EXISTS `transaction_backups`;
CREATE TABLE `transaction_backups`  (
  `backup_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `original_transaction_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `sender_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `receiver_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `sender_balance_before` decimal(10, 2) NULL DEFAULT NULL,
  `receiver_balance_before` decimal(10, 2) NULL DEFAULT NULL,
  `sender_balance_after` decimal(10, 2) NULL DEFAULT NULL,
  `receiver_balance_after` decimal(10, 2) NULL DEFAULT NULL,
  `transaction_amount` decimal(10, 2) NULL DEFAULT NULL,
  `backup_timestamp` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `rollback_executed` tinyint(1) NULL DEFAULT 0,
  `rollback_timestamp` datetime NULL DEFAULT NULL,
  `rollback_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`backup_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for transactions
-- ----------------------------
DROP TABLE IF EXISTS `transactions`;
CREATE TABLE `transactions`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(10, 2) NULL DEFAULT NULL,
  `payment_method` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT NULL,
  `sender_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `receiver_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `note` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `type` enum('Transfer','Deposit','Withdrawal','Payment','Refund') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_sender_id`(`sender_id` ASC) USING BTREE,
  INDEX `idx_receiver_id`(`receiver_id` ASC) USING BTREE,
  INDEX `idx_timestamp`(`timestamp` ASC) USING BTREE,
  CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_expense_habit
-- ----------------------------
DROP TABLE IF EXISTS `user_expense_habit`;
CREATE TABLE `user_expense_habit`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT NULL,
  `monthly_income` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `earning_member` tinyint(1) NULL DEFAULT NULL,
  `dependents` int NULL DEFAULT NULL,
  `living_situation` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `rent` decimal(10, 2) NULL DEFAULT NULL,
  `transport_mode` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `transport_cost` decimal(10, 2) NULL DEFAULT NULL,
  `eating_out_frequency` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `grocery_cost` decimal(10, 2) NULL DEFAULT NULL,
  `utilities_cost` decimal(10, 2) NULL DEFAULT NULL,
  `mobile_internet_cost` decimal(10, 2) NULL DEFAULT NULL,
  `subscriptions` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `savings` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `investments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `loans` tinyint(1) NULL DEFAULT NULL,
  `loan_payment` decimal(10, 2) NULL DEFAULT NULL,
  `financial_goal` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `user_expense_habit_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_passwords
-- ----------------------------
DROP TABLE IF EXISTS `user_passwords`;
CREATE TABLE `user_passwords`  (
  `user_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `last_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `dob` date NULL DEFAULT NULL,
  `age` int NULL DEFAULT NULL,
  `gender` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `marital_status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `blood_group` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `balance` decimal(10, 2) NULL DEFAULT NULL,
  `joining_date` date NULL DEFAULT NULL,
  `role_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_role_id`(`role_id` ASC) USING BTREE,
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- View structure for v_daily_transaction_analytics
-- ----------------------------
DROP VIEW IF EXISTS `v_daily_transaction_analytics`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_daily_transaction_analytics` AS select cast(`transactions`.`timestamp` as date) AS `transaction_date`,count(0) AS `total_transactions`,coalesce(sum(`transactions`.`amount`),0) AS `total_volume`,coalesce(avg(`transactions`.`amount`),0) AS `avg_transaction_amount`,coalesce(min(`transactions`.`amount`),0) AS `min_transaction`,coalesce(max(`transactions`.`amount`),0) AS `max_transaction`,count(distinct `transactions`.`sender_id`) AS `unique_senders`,count(distinct `transactions`.`receiver_id`) AS `unique_receivers`,count((case when (`transactions`.`type` = 'Transfer') then 1 end)) AS `transfers`,count((case when (`transactions`.`type` = 'Deposit') then 1 end)) AS `deposits`,count((case when (`transactions`.`type` = 'Withdrawal') then 1 end)) AS `withdrawals` from `transactions` where (`transactions`.`timestamp` >= (curdate() - interval 30 day)) group by cast(`transactions`.`timestamp` as date) order by `transaction_date` desc;

-- ----------------------------
-- View structure for v_high_risk_users
-- ----------------------------
DROP VIEW IF EXISTS `v_high_risk_users`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_high_risk_users` AS select `u`.`id` AS `id`,`u`.`first_name` AS `first_name`,`u`.`last_name` AS `last_name`,`u`.`balance` AS `balance`,`GetUserRiskScore`(`u`.`id`) AS `risk_score`,count(distinct `f`.`id`) AS `fraud_reports`,`CalculateTransactionVelocity`(`u`.`id`,7) AS `weekly_velocity`,`CalculateAccountAge`(`u`.`id`) AS `account_age_days` from (`users` `u` left join `fraud_list` `f` on((`u`.`id` = `f`.`reported_user_id`))) where (`GetUserRiskScore`(`u`.`id`) > 30) group by `u`.`id`,`u`.`first_name`,`u`.`last_name`,`u`.`balance` order by `risk_score` desc;

-- ----------------------------
-- View structure for v_monthly_transaction_report
-- ----------------------------
DROP VIEW IF EXISTS `v_monthly_transaction_report`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_monthly_transaction_report` AS select `monthly_data`.`year` AS `year`,`monthly_data`.`month` AS `month`,`monthly_data`.`transaction_count` AS `transaction_count`,`monthly_data`.`total_volume` AS `total_volume`,`monthly_data`.`avg_amount` AS `avg_amount`,sum(`monthly_data`.`transaction_count`) OVER (ORDER BY `monthly_data`.`year`,`monthly_data`.`month` )  AS `cumulative_transactions`,sum(`monthly_data`.`total_volume`) OVER (ORDER BY `monthly_data`.`year`,`monthly_data`.`month` )  AS `cumulative_volume` from (select year(`transactions`.`timestamp`) AS `year`,month(`transactions`.`timestamp`) AS `month`,count(0) AS `transaction_count`,coalesce(sum(`transactions`.`amount`),0) AS `total_volume`,coalesce(avg(`transactions`.`amount`),0) AS `avg_amount` from `transactions` group by year(`transactions`.`timestamp`),month(`transactions`.`timestamp`)) `monthly_data` order by `monthly_data`.`year` desc,`monthly_data`.`month` desc;

-- ----------------------------
-- View structure for v_user_transaction_summary
-- ----------------------------
DROP VIEW IF EXISTS `v_user_transaction_summary`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_user_transaction_summary` AS select `u`.`id` AS `id`,`u`.`first_name` AS `first_name`,`u`.`last_name` AS `last_name`,`u`.`balance` AS `balance`,count(distinct `t_sent`.`id`) AS `transactions_sent`,count(distinct `t_received`.`id`) AS `transactions_received`,coalesce(sum(`t_sent`.`amount`),0) AS `total_sent`,coalesce(sum(`t_received`.`amount`),0) AS `total_received`,coalesce(max(greatest(coalesce(`t_sent`.`timestamp`,'1970-01-01'),coalesce(`t_received`.`timestamp`,'1970-01-01'))),'1970-01-01') AS `last_transaction_date`,`GetUserRiskScore`(`u`.`id`) AS `risk_score` from ((`users` `u` left join `transactions` `t_sent` on((`u`.`id` = `t_sent`.`sender_id`))) left join `transactions` `t_received` on((`u`.`id` = `t_received`.`receiver_id`))) group by `u`.`id`,`u`.`first_name`,`u`.`last_name`,`u`.`balance`;

-- ----------------------------
-- Procedure structure for AddColumnIfNotExists
-- ----------------------------
DROP PROCEDURE IF EXISTS `AddColumnIfNotExists`;
delimiter ;;
CREATE PROCEDURE `AddColumnIfNotExists`(IN p_table_name VARCHAR(64),
    IN p_column_name VARCHAR(64),
    IN p_column_definition TEXT)
BEGIN
    DECLARE v_col_exists INT DEFAULT 0;
    
    -- Check if column exists
    SELECT COUNT(*) INTO v_col_exists
    FROM information_schema.columns 
    WHERE table_schema = DATABASE() 
    AND table_name = p_table_name 
    AND column_name = p_column_name;
    
    IF v_col_exists = 0 THEN
        SET @sql = CONCAT('ALTER TABLE `', p_table_name, '` ADD COLUMN `', p_column_name, '` ', p_column_definition);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for AdminBatchBalanceUpdate
-- ----------------------------
DROP PROCEDURE IF EXISTS `AdminBatchBalanceUpdate`;
delimiter ;;
CREATE PROCEDURE `AdminBatchBalanceUpdate`(IN p_admin_id CHAR(36),
    IN p_user_ids TEXT,
    IN p_amounts TEXT,
    IN p_reason TEXT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500),
    OUT p_updated_count INT)
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
    
    WHILE v_pos <= LENGTH(p_user_ids) DO
        SET v_next_pos = LOCATE(',', p_user_ids, v_pos);
        IF v_next_pos = 0 THEN
            SET v_next_pos = LENGTH(p_user_ids) + 1;
        END IF;
        
        SET v_user_id = TRIM(SUBSTRING(p_user_ids, v_pos, v_next_pos - v_pos));
        SET v_pos = LOCATE(',', p_amounts, v_pos);
        IF v_pos = 0 THEN
            SET v_pos = LENGTH(p_amounts) + 1;
        ELSE
            SET v_pos = v_pos + 1;
        END IF;
        
        SET v_next_pos = LOCATE(',', p_amounts, v_pos);
        IF v_next_pos = 0 THEN
            SET v_next_pos = LENGTH(p_amounts) + 1;
        END IF;
        
        SET v_amount = CAST(TRIM(SUBSTRING(p_amounts, v_pos, v_next_pos - v_pos)) AS DECIMAL(10,2));
        
        -- Update user balance
        UPDATE users SET balance = balance + v_amount WHERE id = v_user_id;
        
        -- Create transaction record
        INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, transaction_type, description)
        VALUES (UUID(), v_amount, 'admin_adjustment', NOW(), p_admin_id, v_user_id, 'Deposit', 'Admin Panel');
        
        -- Note: Removed admin_logs insert to prevent foreign key constraint issues
        
        SET v_updated_count = v_updated_count + 1;
        SET v_pos = v_next_pos + 1;
    END WHILE;
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = CONCAT('Successfully updated ', v_updated_count, ' user balances');
    SET p_updated_count = v_updated_count;
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for BulkBalanceUpdate
-- ----------------------------
DROP PROCEDURE IF EXISTS `BulkBalanceUpdate`;
delimiter ;;
CREATE PROCEDURE `BulkBalanceUpdate`(IN p_admin_id CHAR(36),
    IN p_user_ids TEXT,
    IN p_amounts TEXT,
    IN p_reason TEXT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500))
BEGIN
    DECLARE v_user_id CHAR(36);
    DECLARE v_amount DECIMAL(10,2);
    DECLARE v_index INT DEFAULT 1;
    DECLARE v_user_count INT;
    DECLARE v_amount_count INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_success = FALSE;
        SET p_message = 'Bulk update failed due to database error';
    END;
    
    -- Count number of users and amounts
    SET v_user_count = (SELECT LENGTH(p_user_ids) - LENGTH(REPLACE(p_user_ids, ',', '')) + 1);
    SET v_amount_count = (SELECT LENGTH(p_amounts) - LENGTH(REPLACE(p_amounts, ',', '')) + 1);
    
    IF v_user_count != v_amount_count THEN
        SET p_success = FALSE;
        SET p_message = 'Number of users and amounts must match';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Number of users and amounts must match';
    END IF;
    
    START TRANSACTION;
    
    WHILE v_index <= v_user_count DO
        SET v_user_id = SUBSTRING_INDEX(SUBSTRING_INDEX(p_user_ids, ',', v_index), ',', -1);
        SET v_amount = CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(p_amounts, ',', v_index), ',', -1) AS DECIMAL(10,2));
        
        -- Update user balance
        UPDATE users SET balance = balance + v_amount WHERE id = v_user_id;
        
        -- Log admin action
        INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details)
        VALUES (UUID(), p_admin_id, '127.0.0.1', NOW(), 
                CONCAT('Bulk balance update: User ', v_user_id, ' amount ', v_amount, ' reason: ', p_reason));
        
        SET v_index = v_index + 1;
    END WHILE;
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = CONCAT('Successfully updated ', v_user_count, ' user balances');
END
;;
delimiter ;

-- ----------------------------
-- Function structure for CalculateAccountAge
-- ----------------------------
DROP FUNCTION IF EXISTS `CalculateAccountAge`;
delimiter ;;
CREATE FUNCTION `CalculateAccountAge`(p_user_id CHAR(36))
 RETURNS int
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
END
;;
delimiter ;

-- ----------------------------
-- Function structure for CalculateTransactionVelocity
-- ----------------------------
DROP FUNCTION IF EXISTS `CalculateTransactionVelocity`;
delimiter ;;
CREATE FUNCTION `CalculateTransactionVelocity`(p_user_id CHAR(36), p_days INT)
 RETURNS decimal(10,2)
  READS SQL DATA 
  DETERMINISTIC
BEGIN
    DECLARE v_transaction_count INT;
    DECLARE v_velocity DECIMAL(10,2);
    
    SELECT COUNT(*) INTO v_transaction_count
    FROM transactions 
    WHERE (sender_id = p_user_id OR receiver_id = p_user_id)
    AND timestamp >= DATE_SUB(NOW(), INTERVAL p_days DAY);
    
    SET v_velocity = v_transaction_count / GREATEST(p_days, 1);
    
    RETURN v_velocity;
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for CalculateUserStatistics
-- ----------------------------
DROP PROCEDURE IF EXISTS `CalculateUserStatistics`;
delimiter ;;
CREATE PROCEDURE `CalculateUserStatistics`(IN p_user_id CHAR(36),
    OUT p_total_sent DECIMAL(15,2),
    OUT p_total_received DECIMAL(15,2),
    OUT p_transaction_count INT,
    OUT p_avg_transaction DECIMAL(10,2),
    OUT p_last_transaction_date DATETIME)
BEGIN
    SELECT COALESCE(SUM(amount), 0) INTO p_total_sent
    FROM transactions 
    WHERE sender_id = p_user_id;
    
    SELECT COALESCE(SUM(amount), 0) INTO p_total_received
    FROM transactions 
    WHERE receiver_id = p_user_id;
    
    SELECT COUNT(*) INTO p_transaction_count
    FROM transactions 
    WHERE sender_id = p_user_id OR receiver_id = p_user_id;
    
    SELECT COALESCE(AVG(amount), 0) INTO p_avg_transaction
    FROM transactions 
    WHERE sender_id = p_user_id OR receiver_id = p_user_id;
    
    SELECT MAX(timestamp) INTO p_last_transaction_date
    FROM transactions 
    WHERE sender_id = p_user_id OR receiver_id = p_user_id;
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for CreateFullBudget
-- ----------------------------
DROP PROCEDURE IF EXISTS `CreateFullBudget`;
delimiter ;;
CREATE PROCEDURE `CreateFullBudget`(IN p_user_id CHAR(36),
    IN p_budget_name VARCHAR(255),
    IN p_currency VARCHAR(10),
    IN p_income_sources TEXT,
    IN p_total_income DECIMAL(15,2),
    IN p_expenses_json TEXT,
    OUT p_budget_id CHAR(36),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500))
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
    
    
    SET v_budget_id = UUID();
    INSERT INTO budgets (id, user_id, name, currency, income_source, amount)
    VALUES (v_budget_id, p_user_id, p_budget_name, p_currency, p_income_sources, p_total_income);
    
    
    
    
    COMMIT;
    SET p_budget_id = v_budget_id;
    SET p_success = TRUE;
    SET p_message = 'Full budget created successfully';
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for GetUserDashboardData
-- ----------------------------
DROP PROCEDURE IF EXISTS `GetUserDashboardData`;
delimiter ;;
CREATE PROCEDURE `GetUserDashboardData`(IN p_user_id CHAR(36),
    OUT p_current_balance DECIMAL(10,2),
    OUT p_total_sent DECIMAL(15,2),
    OUT p_total_received DECIMAL(15,2),
    OUT p_transaction_count INT,
    OUT p_risk_score DECIMAL(5,2))
BEGIN
    
    SELECT balance INTO p_current_balance 
    FROM users WHERE id = p_user_id;
    
    
    SELECT 
        COALESCE(SUM(CASE WHEN sender_id = p_user_id THEN amount ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN receiver_id = p_user_id THEN amount ELSE 0 END), 0),
        COUNT(*)
    INTO p_total_sent, p_total_received, p_transaction_count
    FROM transactions 
    WHERE sender_id = p_user_id OR receiver_id = p_user_id;
    
    
    SET p_risk_score = GetUserRiskScore(p_user_id);
END
;;
delimiter ;

-- ----------------------------
-- Function structure for GetUserRiskScore
-- ----------------------------
DROP FUNCTION IF EXISTS `GetUserRiskScore`;
delimiter ;;
CREATE FUNCTION `GetUserRiskScore`(p_user_id CHAR(36))
 RETURNS decimal(5,2)
  READS SQL DATA 
  DETERMINISTIC
BEGIN
    DECLARE v_fraud_reports INT DEFAULT 0;
    DECLARE v_high_amount_txs INT DEFAULT 0;
    DECLARE v_account_age INT DEFAULT 0;
    DECLARE v_risk_score DECIMAL(5,2) DEFAULT 0.0;
    
    SELECT COUNT(*) INTO v_fraud_reports
    FROM fraud_list 
    WHERE reported_user_id = p_user_id;
    
    SELECT COUNT(*) INTO v_high_amount_txs
    FROM transactions 
    WHERE sender_id = p_user_id 
    AND amount > 1000
    AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY);
    
    SET v_account_age = CalculateAccountAge(p_user_id);
    
    SET v_risk_score = (v_fraud_reports * 30) + (v_high_amount_txs * 10);
    
    IF v_account_age > 365 THEN
        SET v_risk_score = v_risk_score * 0.8;
    ELSEIF v_account_age > 180 THEN
        SET v_risk_score = v_risk_score * 0.9;
    END IF;
    
    SET v_risk_score = LEAST(v_risk_score, 100);
    
    RETURN v_risk_score;
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for GetUserTransactionHistory
-- ----------------------------
DROP PROCEDURE IF EXISTS `GetUserTransactionHistory`;
delimiter ;;
CREATE PROCEDURE `GetUserTransactionHistory`(IN p_user_id CHAR(36),
    IN p_limit INT,
    IN p_offset INT)
BEGIN
    SET @running_balance = (SELECT balance FROM users WHERE id = p_user_id);
    
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
        COALESCE(
            CASE 
                WHEN t.sender_id = p_user_id THEN CONCAT(r.first_name, ' ', r.last_name)
                WHEN t.receiver_id = p_user_id THEN CONCAT(s.first_name, ' ', s.last_name)
            END,
            'Unknown'
        ) as other_party,
        @running_balance := @running_balance + 
            CASE 
                WHEN t.sender_id = p_user_id THEN -t.amount
                WHEN t.receiver_id = p_user_id THEN t.amount
                ELSE 0
            END as running_balance
    FROM transactions t
    LEFT JOIN users s ON t.sender_id = s.id
    LEFT JOIN users r ON t.receiver_id = r.id
    WHERE t.sender_id = p_user_id OR t.receiver_id = p_user_id
    ORDER BY t.timestamp DESC
    LIMIT p_limit OFFSET p_offset;
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for ProcessFraudReport
-- ----------------------------
DROP PROCEDURE IF EXISTS `ProcessFraudReport`;
delimiter ;;
CREATE PROCEDURE `ProcessFraudReport`(IN p_reporter_id CHAR(36),
    IN p_reported_user_id CHAR(36),
    IN p_reason VARCHAR(500),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500))
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
    
    -- Check if reporter exists
    SELECT COUNT(*) INTO v_reporter_exists FROM users WHERE id = p_reporter_id;
    
    -- Check if reported user exists
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
    
    -- Check for existing reports
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
    
    -- Get risk score and check for auto-suspension
    SET v_risk_score = GetUserRiskScore(p_reported_user_id);
    
    IF v_risk_score > 80 THEN
        UPDATE users SET is_suspended = TRUE WHERE id = p_reported_user_id;
        -- Note: Removed admin_logs insert to prevent foreign key constraint issues
    END IF;
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = 'Fraud report processed successfully';
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for ProcessMoneyTransfer
-- ----------------------------
DROP PROCEDURE IF EXISTS `ProcessMoneyTransfer`;
delimiter ;;
CREATE PROCEDURE `ProcessMoneyTransfer`(IN p_sender_id CHAR(36),
    IN p_receiver_id CHAR(36),
    IN p_amount DECIMAL(10,2),
    IN p_payment_method VARCHAR(100),
    IN p_note TEXT,
    IN p_tx_type ENUM('Transfer', 'Deposit', 'Withdrawal', 'Payment', 'Refund'),
    IN p_location VARCHAR(255),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500),
    OUT p_transaction_id CHAR(36))
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
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Amount must be greater than zero';
    END IF;
    
    IF p_sender_id = p_receiver_id THEN
        SET p_success = FALSE;
        SET p_message = 'Cannot transfer money to yourself';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot transfer money to yourself';
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
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Sender not found';
    END IF;
    
    -- Check if receiver exists
    SELECT COUNT(*) INTO v_receiver_exists FROM users WHERE id = p_receiver_id;
    
    IF v_receiver_exists = 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Receiver not found';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Receiver not found';
    END IF;
    
    -- Check if sender has sufficient balance
    IF v_sender_balance < p_amount THEN
        SET p_success = FALSE;
        SET p_message = 'Insufficient balance';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient balance';
    END IF;
    
    -- Check if receiver is fraud flagged
    SELECT COUNT(*) INTO v_is_fraud_flagged 
    FROM fraud_list 
    WHERE reported_user_id = p_receiver_id;
    
    IF v_is_fraud_flagged > 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Cannot transfer to fraud-flagged user';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot transfer to fraud-flagged user';
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
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = CONCAT('Successfully transferred ', p_amount, ' to receiver');
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for RegisterUser
-- ----------------------------
DROP PROCEDURE IF EXISTS `RegisterUser`;
delimiter ;;
CREATE PROCEDURE `RegisterUser`(IN p_role_name VARCHAR(50),
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
    OUT p_message VARCHAR(500))
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
    
    
    SELECT COUNT(*) INTO v_email_exists FROM contact_info WHERE LOWER(email) = LOWER(p_email);
    
    IF v_email_exists > 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Email already exists';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Email already exists';
    END IF;
    
    
    SELECT COUNT(*) INTO v_phone_exists FROM contact_info WHERE phone = p_phone;
    
    IF v_phone_exists > 0 THEN
        SET p_success = FALSE;
        SET p_message = 'Phone number already exists';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Phone number already exists';
    END IF;
    
    
    SELECT id INTO v_role_id FROM roles WHERE LOWER(name) = LOWER(p_role_name);
    
    IF v_role_id IS NULL THEN
        SET p_success = FALSE;
        SET p_message = 'Invalid role specified';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid role specified';
    END IF;
    
    
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
    
    
    INSERT INTO users (id, first_name, last_name, dob, age, gender, marital_status, 
                      blood_group, balance, joining_date, role_id)
    VALUES (v_user_id, p_first_name, p_last_name, p_dob, p_age, p_gender, 
            p_marital_status, p_blood_group, 0, CURDATE(), v_role_id);
    
    
    SET v_contact_id = UUID();
    INSERT INTO contact_info (id, user_id, email, phone, address_id)
    VALUES (v_contact_id, v_user_id, p_email, p_phone, NULL);
    
    
    INSERT INTO user_passwords (user_id, password)
    VALUES (v_user_id, p_password);
    
    COMMIT;
    SET p_user_id = v_user_id;
    SET p_success = TRUE;
    SET p_message = 'User registered successfully';
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for RollbackTransaction
-- ----------------------------
DROP PROCEDURE IF EXISTS `RollbackTransaction`;
delimiter ;;
CREATE PROCEDURE `RollbackTransaction`(IN p_transaction_id CHAR(36),
    IN p_reason TEXT,
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500))
  COMMENT 'Rollback a completed transaction by restoring original balances from backup data'
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
        
        
        INSERT INTO system_audit_log (
            id, operation_type, entity_type, entity_id, user_id,
            success, error_message, timestamp
        ) VALUES (
            UUID(), 'ROLLBACK', 'TRANSACTION', p_transaction_id, NULL,
            FALSE, v_error_message, NOW()
        );
    END;
    
    START TRANSACTION;
    
    
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
    
    
    IF v_current_status = 'ROLLED_BACK' THEN
        SET p_success = FALSE;
        SET p_message = 'Transaction already rolled back';
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Transaction already rolled back';
    END IF;
    
    
    IF v_current_status != 'COMPLETED' THEN
        SET p_success = FALSE;
        SET p_message = CONCAT('Cannot rollback transaction with status: ', v_current_status);
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot rollback non-completed transaction';
    END IF;
    
    
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
    
    
    UPDATE users SET balance = v_sender_balance_before WHERE id = v_sender_id;
    UPDATE users SET balance = v_receiver_balance_before WHERE id = v_receiver_id;
    
    
    UPDATE transactions 
    SET status = 'ROLLED_BACK' 
    WHERE id = p_transaction_id;
    
    
    INSERT INTO system_audit_log (
        id, operation_type, entity_type, entity_id, user_id,
        old_values, new_values, timestamp, success
    ) VALUES (
        UUID(), 'ROLLBACK', 'TRANSACTION', p_transaction_id, v_sender_id,
        CONCAT('status:', v_current_status, ',reason:', p_reason),
        CONCAT('status:ROLLED_BACK,sender_balance_restored:', v_sender_balance_before, ',receiver_balance_restored:', v_receiver_balance_before),
        NOW(), TRUE
    );
    
    
    UPDATE transaction_backups 
    SET rollback_timestamp = NOW(),
        rollback_reason = p_reason
    WHERE original_transaction_id = p_transaction_id;
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = CONCAT('Transaction ', p_transaction_id, ' successfully rolled back');
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for SafeAddColumn
-- ----------------------------
DROP PROCEDURE IF EXISTS `SafeAddColumn`;
delimiter ;;
CREATE PROCEDURE `SafeAddColumn`(IN table_name VARCHAR(128),
    IN column_name VARCHAR(128),
    IN column_definition TEXT)
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
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for SafeAddIndex
-- ----------------------------
DROP PROCEDURE IF EXISTS `SafeAddIndex`;
delimiter ;;
CREATE PROCEDURE `SafeAddIndex`(IN table_name VARCHAR(128),
    IN index_name VARCHAR(128),
    IN index_definition TEXT)
BEGIN
    DECLARE idx_exists INT DEFAULT 0;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
    
    SELECT COUNT(*) INTO idx_exists
    FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = table_name 
    AND INDEX_NAME = index_name;
    
    IF idx_exists = 0 THEN
        SET @sql = CONCAT('ALTER TABLE ', table_name, ' ADD INDEX ', index_name, ' ', index_definition);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        SELECT CONCAT('Added index ', index_name, ' to ', table_name) as message;
    ELSE
        SELECT CONCAT('Index ', index_name, ' already exists in ', table_name) as message;
    END IF;
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for SaveOrUpdateBudget
-- ----------------------------
DROP PROCEDURE IF EXISTS `SaveOrUpdateBudget`;
delimiter ;;
CREATE PROCEDURE `SaveOrUpdateBudget`(IN p_user_id CHAR(36),
    IN p_name VARCHAR(255),
    IN p_currency VARCHAR(10),
    IN p_income_source VARCHAR(255),
    IN p_amount DECIMAL(15,2),
    OUT p_budget_id CHAR(36),
    OUT p_success BOOLEAN,
    OUT p_message VARCHAR(500))
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
    
    
    SELECT id, COUNT(*) INTO v_existing_budget_id, v_budget_count
    FROM budgets 
    WHERE user_id = p_user_id 
    LIMIT 1;
    
    IF v_budget_count > 0 THEN
        
        UPDATE budgets 
        SET name = p_name, 
            currency = p_currency, 
            income_source = p_income_source, 
            amount = p_amount
        WHERE id = v_existing_budget_id;
        
        SET p_budget_id = v_existing_budget_id;
    ELSE
        
        SET p_budget_id = UUID();
        INSERT INTO budgets (id, user_id, name, currency, income_source, amount)
        VALUES (p_budget_id, p_user_id, p_name, p_currency, p_income_source, p_amount);
    END IF;
    
    COMMIT;
    SET p_success = TRUE;
    SET p_message = 'Budget saved successfully';
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table transactions
-- ----------------------------
DROP TRIGGER IF EXISTS `tr_transactions_blockchain`;
delimiter ;;
CREATE TRIGGER `tr_transactions_blockchain` AFTER INSERT ON `transactions` FOR EACH ROW BEGIN
    DECLARE v_prev_hash VARCHAR(255) DEFAULT '';
    DECLARE v_block_index INT DEFAULT 0;
    DECLARE v_new_hash VARCHAR(255);
    
    -- Get the highest index from blockchain table
    SELECT COALESCE(MAX(`index`), -1) + 1 INTO v_block_index FROM blockchain;
    
    -- Get the previous hash if exists
    SELECT COALESCE(hash, '') INTO v_prev_hash FROM blockchain WHERE `index` = v_block_index - 1;
    
    -- Generate new hash
    SET v_new_hash = SHA2(CONCAT(v_block_index, NEW.id, NEW.amount, NEW.timestamp, v_prev_hash), 256);
    
    -- Insert into blockchain
    INSERT INTO blockchain (id, `index`, type, timestamp, previous_hash, hash, transaction_id)
    VALUES (UUID(), v_block_index, 'TRANSACTION', NEW.timestamp, v_prev_hash, v_new_hash, NEW.id);
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table users
-- ----------------------------
DROP TRIGGER IF EXISTS `tr_balance_validation`;
delimiter ;;
CREATE TRIGGER `tr_balance_validation` BEFORE UPDATE ON `users` FOR EACH ROW BEGIN
            -- Prevent negative balance
            IF NEW.balance < 0 THEN
                SIGNAL SQLSTATE '45000' 
                SET MESSAGE_TEXT = 'Balance cannot be negative';
            END IF;
            
            -- Skip admin_logs for balance changes to avoid foreign key issues
        END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
