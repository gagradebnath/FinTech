-- MySQL Database Schema for FinGuard
-- Migration from SQLite to MySQL

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS user_passwords;
DROP TABLE IF EXISTS user_expense_habit;
DROP TABLE IF EXISTS budget_expense_items;
DROP TABLE IF EXISTS admin_logs;
DROP TABLE IF EXISTS blockchain_transactions;
DROP TABLE IF EXISTS blockchain;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS contact_info;
DROP TABLE IF EXISTS fraud_list;
DROP TABLE IF EXISTS budget_expense_categories;
DROP TABLE IF EXISTS budgets;
DROP TABLE IF EXISTS addresses;
DROP TABLE IF EXISTS role_permissions;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `roles` (
  `id` CHAR(36) PRIMARY KEY,
  `name` VARCHAR(255),
  `description` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `users` (
  `id` CHAR(36) PRIMARY KEY,
  `first_name` VARCHAR(255),
  `last_name` VARCHAR(255),
  `dob` DATE,
  `age` INT,
  `gender` VARCHAR(50),
  `marital_status` VARCHAR(50),
  `blood_group` VARCHAR(10),
  `balance` DECIMAL(10,2),
  `joining_date` DATE,
  `role_id` CHAR(36),
  INDEX `idx_role_id` (`role_id`),
  FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `permissions` (
  `id` CHAR(36) PRIMARY KEY,
  `name` VARCHAR(255),
  `description` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `role_permissions` (
  `id` CHAR(36) PRIMARY KEY,
  `role_id` CHAR(36),
  `permission_id` CHAR(36),
  INDEX `idx_role_id` (`role_id`),
  INDEX `idx_permission_id` (`permission_id`),
  FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `addresses` (
  `id` CHAR(36) PRIMARY KEY,
  `country` VARCHAR(255),
  `division` VARCHAR(255),
  `district` VARCHAR(255),
  `area` VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `budgets` (
  `id` CHAR(36) PRIMARY KEY,
  `user_id` CHAR(36),
  `name` VARCHAR(255),
  `currency` VARCHAR(10),
  `income_source` VARCHAR(255),
  `amount` DECIMAL(15,2),
  `start_date` DATE,
  `end_date` DATE,
  INDEX `idx_user_id` (`user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `budget_expense_categories` (
  `id` CHAR(36) PRIMARY KEY,
  `budget_id` CHAR(36),
  `category_name` VARCHAR(255),
  `amount` DECIMAL(15,2),
  INDEX `idx_budget_id` (`budget_id`),
  FOREIGN KEY (`budget_id`) REFERENCES `budgets` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `fraud_list` (
  `id` CHAR(36) PRIMARY KEY,
  `user_id` CHAR(36),
  `reported_user_id` CHAR(36),
  `reason` VARCHAR(500),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_reported_user_id` (`reported_user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`reported_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `contact_info` (
  `id` CHAR(36) PRIMARY KEY,
  `user_id` CHAR(36) UNIQUE,
  `email` VARCHAR(255) UNIQUE,
  `phone` VARCHAR(20),
  `address_id` CHAR(36),
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_address_id` (`address_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `transactions` (
  `id` CHAR(36) PRIMARY KEY,
  `amount` DECIMAL(10,2),
  `payment_method` VARCHAR(100),
  `timestamp` DATETIME,
  `sender_id` CHAR(36),
  `receiver_id` CHAR(36),
  `note` TEXT,
  `type` ENUM('Transfer', 'Deposit', 'Withdrawal', 'Payment', 'Refund'),
  `location` VARCHAR(255),
  INDEX `idx_sender_id` (`sender_id`),
  INDEX `idx_receiver_id` (`receiver_id`),
  INDEX `idx_timestamp` (`timestamp`),
  FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `blockchain_transactions` (
  `id` CHAR(36) PRIMARY KEY,
  `user_id` CHAR(36),
  `amount` DECIMAL(15,2),
  `current_balance` DECIMAL(15,2),
  `method` VARCHAR(100),
  `timestamp` DATETIME,
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_timestamp` (`timestamp`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `blockchain` (
  `id` CHAR(36) PRIMARY KEY,
  `index` INT,
  `type` VARCHAR(100),
  `timestamp` DATETIME,
  `previous_hash` VARCHAR(255),
  `hash` VARCHAR(255),
  `transaction_id` CHAR(36),
  INDEX `idx_transaction_id` (`transaction_id`),
  INDEX `idx_index` (`index`),
  FOREIGN KEY (`transaction_id`) REFERENCES `blockchain_transactions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `admin_logs` (
  `id` CHAR(36) PRIMARY KEY,
  `admin_id` CHAR(36),
  `ip_address` VARCHAR(45),
  `timestamp` DATETIME,
  `details` TEXT,
  INDEX `idx_admin_id` (`admin_id`),
  INDEX `idx_timestamp` (`timestamp`),
  FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `budget_expense_items` (
  `id` CHAR(36) PRIMARY KEY,
  `category_id` CHAR(36),
  `name` VARCHAR(255),
  `amount` DECIMAL(10,2),
  `details` TEXT,
  INDEX `idx_category_id` (`category_id`),
  FOREIGN KEY (`category_id`) REFERENCES `budget_expense_categories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `user_expense_habit` (
  `id` CHAR(36) PRIMARY KEY,
  `user_id` CHAR(36),
  `timestamp` DATETIME,
  `monthly_income` VARCHAR(100),
  `earning_member` BOOLEAN,
  `dependents` INT,
  `living_situation` VARCHAR(255),
  `rent` DECIMAL(10,2),
  `transport_mode` VARCHAR(100),
  `transport_cost` DECIMAL(10,2),
  `eating_out_frequency` VARCHAR(100),
  `grocery_cost` DECIMAL(10,2),
  `utilities_cost` DECIMAL(10,2),
  `mobile_internet_cost` DECIMAL(10,2),
  `subscriptions` VARCHAR(500),
  `savings` VARCHAR(255),
  `investments` TEXT,
  `loans` BOOLEAN,
  `loan_payment` DECIMAL(10,2),
  `financial_goal` VARCHAR(255),
  INDEX `idx_user_id` (`user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `user_passwords` (
  `user_id` VARCHAR(255) PRIMARY KEY,
  `password` VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
