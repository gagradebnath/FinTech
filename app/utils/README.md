# FinGuard Utilities (`utils`)

This folder contains all the core utility modules for the FinGuard application. Each module encapsulates database access and business logic for a specific feature. Use these utilities in your route files to keep code clean, maintainable, and testable.

## Utility Modules and Functions

### `admin_utils.py`
Admin dashboard and management helpers.
- `get_role_name_by_id(role_id)` → str | None
  - Get the name of a role given its ID.
  - Usage: `role = get_role_name_by_id(role_id)`
- `get_agents()` → list[Row]
  - Get all users with the 'agent' role.
  - Usage: `agents = get_agents()`
- `get_all_users()` → list[Row]
  - Get all users in the system.
  - Usage: `users = get_all_users()`
- `get_all_transactions(limit=100)` → list[Row]
  - Get all transactions, with sender/receiver names.
  - Usage: `transactions = get_all_transactions()`
- `get_all_frauds(limit=100)` → list[Row]
  - Get all fraud reports, with reporter and reported user info.
  - Usage: `frauds = get_all_frauds()`
- `get_admin_logs(limit=100)` → list[Row]
  - Get all admin log entries.
  - Usage: `logs = get_admin_logs()`
- `update_user_balance(user_id, amount)` → None
  - Add/subtract balance for a user (admin action).
  - Usage: `update_user_balance(user_id, 100)`
- `insert_transaction_admin(tx_id, amount, sender_id, receiver_id, note, tx_type)` → None
  - Insert a transaction performed by an admin.
  - Usage: `insert_transaction_admin(tx_id, 100, sender_id, receiver_id, 'note', 'admin_add_money')`
- `insert_admin_log(log_id, admin_id, ip_address, details)` → None
  - Log an admin operation (for auditing).
  - Usage: `insert_admin_log(log_id, admin_id, ip, 'details')`
- `insert_fraud_list(fraud_id, user_id, reported_user_id, reason)` → None
  - Add a user to the fraud list.
  - Usage: `insert_fraud_list(fraud_id, user_id, reported_user_id, 'reason')`
- `delete_fraud_list(reported_user_id)` → None
  - Remove a user from the fraud list.
  - Usage: `delete_fraud_list(reported_user_id)`
- `update_user_role(user_id, new_role_id)` → None
  - Change a user's role.
  - Usage: `update_user_role(user_id, new_role_id)`
- `get_role_id_by_name(role_name)` → str | None
  - Get a role's ID from its name.
  - Usage: `role_id = get_role_id_by_name('admin')`

### `auth.py`
Authentication helpers.
- `get_user_by_login_id(login_id)` → Row | None
  - Get user by user_id, email, or phone (case-insensitive).
  - Usage: `user = get_user_by_login_id('john@example.com')`
- `check_password(user_id, password)` → bool
  - Check if the password matches for the given user_id.
  - Usage: `ok = check_password(user['id'], 'secret')`

### `budget_utils.py`
Budget CRUD and helpers.
- `get_user_budget(user_id)` → Row | None
  - Get a user's budget.
  - Usage: `budget = get_user_budget(user['id'])`
- `save_or_update_budget(user_id, name, currency, income_source, amount)` → Row
  - Save or update a user's budget.
  - Usage: `budget = save_or_update_budget(user['id'], name, currency, income_source, amount)`
- `insert_full_budget(user_id, budget_name, currency, income, expenses)` → tuple[bool, str | None]
  - Insert a full budget with categories and items.
  - Usage: `success, err = insert_full_budget(user['id'], budget_name, currency, income, expenses)`

### `dashboard.py`
Dashboard queries.
- `get_user_budgets(user_id)` → list[Row]
  - Get all budgets for a user.
  - Usage: `budgets = get_user_budgets(user['id'])`
- `get_recent_expenses(user_id, limit=5)` → list[Row]
  - Get recent expenses for a user.
  - Usage: `expenses = get_recent_expenses(user['id'])`
- `get_recent_transactions(user_id, limit=5)` → list[Row]
  - Get recent transactions for a user.
  - Usage: `transactions = get_recent_transactions(user['id'])`

### `expense_habit.py`
Expense habit fetch and update.
- `get_expense_habit(user_id)` → Row | None
  - Get a user's expense habit record.
  - Usage: `habit = get_expense_habit(user['id'])`
- `upsert_expense_habit(user_id, data)` → Row
  - Insert or update a user's expense habit.
  - Usage: `habit = upsert_expense_habit(user['id'], data)`

### `fraud_utils.py`
Fraud reporting and lookup.
- `lookup_user_by_identifier(identifier)` → Row | None
  - Find user by ID, email, or phone.
  - Usage: `user = lookup_user_by_identifier(identifier)`
- `add_fraud_report(reporter_id, reported_user_id, reason)` → tuple[bool, str | None]
  - Add a user to the fraud list.
  - Usage: `success, err = add_fraud_report(reporter_id, reported_user_id, reason)`

### `notifications.py`
Notification utilities (planned).
- (To be implemented)

### `permissions_utils.py`
Role and permission management.
- `get_all_roles()` → list[Row]
  - Get all roles in the system.
  - Usage: `roles = get_all_roles()`
- `get_all_permissions()` → list[Row]
  - Get all permissions in the system.
  - Usage: `perms = get_all_permissions()`
- `get_permissions_for_role(role_id)` → list[Row]
  - Get all permissions assigned to a role.
  - Usage: `role_perms = get_permissions_for_role(role_id)`
- `add_permission_to_role(role_id, permission_id)` → None
  - Assign a permission to a role.
  - Usage: `add_permission_to_role(role_id, perm_id)`
- `remove_permission_from_role(role_id, permission_id)` → None
  - Remove a permission from a role.
  - Usage: `remove_permission_from_role(role_id, perm_id)`
- `has_permission(user_id, permission_name)` → bool
  - Check if a user has a specific permission.
  - Usage: `if has_permission(user_id, 'send_money'):`

### `profile.py`
User profile fetch and update.
- `get_user_and_contact(user_id)` → tuple[Row, Row]
  - Get user and contact info.
  - Usage: `user, contact = get_user_and_contact(user_id)`
- `update_user_and_contact(user_id, user_data, contact_data)` → tuple[Row, Row]
  - Update user and contact info.
  - Usage: `user, contact = update_user_and_contact(user_id, user_data, contact_data)`

### `register.py`
Registration helpers.
- `is_email_unique(email)` → bool
  - Check if an email is unique.
  - Usage: `ok = is_email_unique('new@example.com')`
- `is_phone_unique(phone)` → bool
  - Check if a phone number is unique.
  - Usage: `ok = is_phone_unique('0123456789')`
- `get_role_id(role)` → str | None
  - Get a role's ID by name.
  - Usage: `role_id = get_role_id('user')`
- `generate_user_id()` → str
  - Generate a unique user ID.
  - Usage: `user_id = generate_user_id()`
- `create_user_and_contact(role_id, first_name, last_name, dob, age, gender, marital_status, blood_group, email, phone, password)` → tuple[str | None, str | None]
  - Create a user and contact info.
  - Usage: `user_id, err = create_user_and_contact(...)`

### `transaction_utils.py`
Transaction logic and helpers.
- `get_user_by_id(user_id)` → Row | None
  - Fetch a user by their ID.
  - Usage: `user = get_user_by_id(user_id)`
- `send_money(sender_id, recipient_id, amount, payment_method, note, location, tx_type)` → tuple[bool, str, Row | None]
  - Transfer money between users (with validation).
  - Usage: `ok, msg, updated_user = send_money(sender_id, recipient_id, amount, payment_method, note, location, tx_type)`
- `lookup_user_by_identifier(identifier)` → Row | None
  - Find user by ID, email, or phone.
  - Usage: `user = lookup_user_by_identifier(identifier)`
- `is_user_flagged_fraud(user_id)` → bool
  - Check if a user is on the fraud list.
  - Usage: `is_fraud = is_user_flagged_fraud(user_id)`
- `agent_add_money(agent_id, user_id, amount)` → tuple[str | None, str | None]
  - Agent adds money to a user (debits agent, credits user).
  - Usage: `msg, err = agent_add_money(agent_id, user_id, amount)`
- `agent_cash_out(agent_id, user_id, amount)` → tuple[str | None, str | None]
  - Agent cashes out from a user (debits user, credits agent).
  - Usage: `msg, err = agent_cash_out(agent_id, user_id, amount)`

### `user_utils.py`
User session and fetch helpers.
- `get_current_user()` → Row | None
  - Get the current user from the session.
  - Usage: `user = get_current_user()`
- `get_role_name_by_id(role_id)` → str | None
  - Get the name of a role given its ID.
  - Usage: `role = get_role_name_by_id(role_id)`

### `blockchain_utils.py`
Blockchain implementation for transaction security and fraud detection.
- `Block` class → Creates immutable blocks with SHA-256 hashing
  - `__init__(index, timestamp, transaction_data, previous_hash, transaction_id=None)`
  - `calculate_hash()` → str: Calculate SHA-256 hash of block data
  - `is_valid()` → bool: Verify block integrity
- `FinGuardBlockchain` class → Manages blockchain operations
  - `__init__()`: Initialize with genesis block
  - `create_genesis_block()` → Block: Create the first block
  - `get_latest_block()` → Block: Get most recent block
  - `add_transaction_block(transaction_data)` → Block: Add new transaction block
  - `is_chain_valid()` → tuple[bool, List[str]]: Validate entire chain
- `get_blockchain_connection()` → Connection: Get database connection
- `create_blockchain_transaction(user_id, amount, current_balance, method, transaction_id=None)` → str: Create blockchain transaction record
- `add_block_to_chain(block_data, transaction_id)` → bool: Add block to database
- `get_blockchain_from_db(limit=None)` → List[Block]: Load blockchain from database
- `process_transaction_with_blockchain(user_id, amount, current_balance, method, transaction_data)` → tuple[bool, str]: Process transaction with blockchain validation
- `validate_transaction_blockchain(transaction_id)` → tuple[bool, str]: Validate transaction using blockchain
- `get_blockchain_analytics()` → dict: Get blockchain statistics
- `detect_fraud_via_blockchain(user_id)` → tuple[bool, str]: Detect fraud using blockchain analysis

### `password_utils.py`
Password hashing and validation utilities.
- `hash_password(password)` → str: Hash password using bcrypt
- `verify_password(password, hashed_password)` → bool: Verify password against hash
- `generate_reset_token()` → str: Generate password reset token
- `verify_reset_token(token)` → bool: Verify password reset token

### `jwt_auth.py`
JWT token management for authentication.
- `generate_token(user_id, role_id)` → str: Generate JWT token
- `verify_token(token)` → dict: Verify and decode JWT token
- `refresh_token(token)` → str: Refresh JWT token
- `revoke_token(token)` → bool: Revoke JWT token

### `advanced_sql_utils.py`
Advanced SQL utilities for complex database operations.
- `execute_stored_procedure(procedure_name, params)` → tuple[bool, any]: Execute stored procedure
- `get_table_statistics(table_name)` → dict: Get table statistics
- `optimize_table(table_name)` → bool: Optimize table performance
- `backup_table(table_name)` → bool: Create table backup
- `restore_table(table_name, backup_date)` → bool: Restore table from backup

---

## 📊 **Database Schema Documentation**

### **Core Tables**

#### `users` Table
**Purpose**: Store user account information
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `first_name` (VARCHAR(255)): User's first name
- `last_name` (VARCHAR(255)): User's last name
- `dob` (DATE): Date of birth
- `age` (INT): User's age
- `gender` (VARCHAR(50)): User's gender
- `marital_status` (VARCHAR(50)): Marital status
- `blood_group` (VARCHAR(10)): Blood group
- `balance` (DECIMAL(10,2)): Current account balance
- `joining_date` (DATE): Account creation date
- `role_id` (CHAR(36)): Foreign key to roles table

**Indexes**:
- `idx_role_id` on `role_id` column for role-based queries

**Relationships**:
- Many-to-One with `roles` table via `role_id`
- One-to-Many with `transactions` table (sender/receiver)
- One-to-Many with `budgets` table
- One-to-Many with `fraud_list` table

#### `roles` Table
**Purpose**: Define user roles and permissions
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `name` (VARCHAR(255)): Role name (e.g., 'USER', 'ADMIN', 'AGENT')
- `description` (TEXT): Role description

**Default Roles**:
- `USER`: Standard user with basic permissions
- `ADMIN`: Administrative user with full permissions
- `AGENT`: Agent user with money transfer permissions

#### `permissions` Table
**Purpose**: Define system permissions
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `name` (VARCHAR(255)): Permission name
- `description` (TEXT): Permission description

**Default Permissions**:
- `send_money`: Allow money transfers
- `view_analytics`: View analytics dashboard
- `manage_users`: Manage user accounts
- `fraud_detection`: Access fraud detection tools

#### `role_permissions` Table
**Purpose**: Map roles to permissions (Many-to-Many)
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `role_id` (CHAR(36)): Foreign key to roles
- `permission_id` (CHAR(36)): Foreign key to permissions

#### `transactions` Table
**Purpose**: Record all financial transactions
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `sender_id` (CHAR(36)): Sender user ID
- `receiver_id` (CHAR(36)): Receiver user ID
- `amount` (DECIMAL(15,2)): Transaction amount
- `payment_method` (VARCHAR(50)): Payment method used
- `description` (TEXT): Transaction description
- `timestamp` (TIMESTAMP): Transaction timestamp
- `status` (VARCHAR(20)): Transaction status
- `transaction_type` (VARCHAR(50)): Type of transaction
- `location` (VARCHAR(255)): Transaction location

**Indexes**:
- `idx_sender_id` on `sender_id` for sender queries
- `idx_receiver_id` on `receiver_id` for receiver queries
- `idx_timestamp` on `timestamp` for time-based queries

#### `blockchain` Table
**Purpose**: Store blockchain blocks for transaction security
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `index` (INT): Block index in chain
- `timestamp` (TIMESTAMP): Block creation time
- `transaction_data` (JSON): Transaction data stored in block
- `previous_hash` (VARCHAR(64)): Hash of previous block
- `hash` (VARCHAR(64)): Current block hash
- `transaction_id` (CHAR(36)): Related transaction ID

**Indexes**:
- `idx_block_index` on `index` for sequential access
- `idx_transaction_id` on `transaction_id` for transaction lookup

#### `blockchain_transactions` Table
**Purpose**: Store blockchain-specific transaction data
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `user_id` (CHAR(36)): User involved in transaction
- `amount` (DECIMAL(15,2)): Transaction amount
- `current_balance` (DECIMAL(15,2)): User balance after transaction
- `method` (VARCHAR(50)): Transaction method
- `timestamp` (TIMESTAMP): Transaction timestamp

**Relationships**:
- Foreign key to `users` table via `user_id`
- Linked to `blockchain` table via `transaction_id`

#### `fraud_list` Table
**Purpose**: Track fraud reports and suspicious users
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `user_id` (CHAR(36)): Reporter user ID
- `reported_user_id` (CHAR(36)): Reported user ID
- `reason` (VARCHAR(500)): Fraud report reason
- `created_at` (TIMESTAMP): Report creation time
- `status` (VARCHAR(20)): Investigation status
- `investigation_notes` (TEXT): Investigation details

**Indexes**:
- `idx_user_id` on `user_id` for reporter queries
- `idx_reported_user_id` on `reported_user_id` for reported user queries

#### `budgets` Table
**Purpose**: Store user budget information
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `user_id` (CHAR(36)): Budget owner user ID
- `name` (VARCHAR(255)): Budget name
- `currency` (VARCHAR(10)): Budget currency
- `income_source` (VARCHAR(255)): Income source
- `amount` (DECIMAL(15,2)): Budget amount
- `start_date` (DATE): Budget start date
- `end_date` (DATE): Budget end date

#### `budget_expense_categories` Table
**Purpose**: Store budget expense categories
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `budget_id` (CHAR(36)): Related budget ID
- `category_name` (VARCHAR(255)): Category name
- `amount` (DECIMAL(15,2)): Category amount

#### `budget_expense_items` Table
**Purpose**: Store individual expense items within categories
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `category_id` (CHAR(36)): Related category ID
- `item_name` (VARCHAR(255)): Item name
- `amount` (DECIMAL(15,2)): Item amount

#### `contact_info` Table
**Purpose**: Store user contact information
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `user_id` (CHAR(36)): Related user ID
- `email` (VARCHAR(255)): Email address
- `phone` (VARCHAR(20)): Phone number
- `address_id` (CHAR(36)): Related address ID

#### `addresses` Table
**Purpose**: Store address information
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `country` (VARCHAR(255)): Country
- `division` (VARCHAR(255)): Division/State
- `district` (VARCHAR(255)): District/City
- `area` (VARCHAR(255)): Area/Locality

#### `user_passwords` Table
**Purpose**: Store user password hashes
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `user_id` (CHAR(36)): Related user ID
- `password_hash` (VARCHAR(255)): Hashed password
- `created_at` (TIMESTAMP): Password creation time
- `updated_at` (TIMESTAMP): Last password update

#### `admin_logs` Table
**Purpose**: Store administrative action logs
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `admin_id` (CHAR(36)): Admin user ID
- `action` (VARCHAR(100)): Action performed
- `details` (TEXT): Action details
- `timestamp` (TIMESTAMP): Action timestamp

#### `user_expense_habit` Table
**Purpose**: Store user spending habits and patterns
**Columns**:
- `id` (CHAR(36)): Primary key, UUID
- `user_id` (CHAR(36)): Related user ID
- `category` (VARCHAR(100)): Expense category
- `amount` (DECIMAL(15,2)): Expense amount
- `frequency` (VARCHAR(50)): Expense frequency
- `last_updated` (TIMESTAMP): Last update time

---

## 🔧 **Stored Procedures Documentation**

### **ProcessMoneyTransferEnhanced**
**Purpose**: Enhanced money transfer with fraud detection and rollback support
**Parameters**:
- `IN p_sender_id CHAR(36)`: Sender user ID
- `IN p_receiver_id CHAR(36)`: Receiver user ID
- `IN p_amount DECIMAL(15,2)`: Transfer amount
- `IN p_payment_method VARCHAR(50)`: Payment method
- `IN p_description TEXT`: Transaction description
- `OUT p_transaction_id CHAR(36)`: Generated transaction ID
- `OUT p_success BOOLEAN`: Success status
- `OUT p_message VARCHAR(500)`: Result message

**When Used**: Called during money transfer operations from `transaction_utils.py`
**Why Used**: Provides atomic transaction processing with comprehensive error handling
**Usage**: 
```sql
CALL ProcessMoneyTransferEnhanced('sender-id', 'receiver-id', 100.00, 'Bank Transfer', 'Payment', @tx_id, @success, @msg);
```

### **AddColumnIfNotExists**
**Purpose**: Dynamically add database columns if they don't exist
**Parameters**:
- `IN table_name VARCHAR(64)`: Target table name
- `IN column_name VARCHAR(64)`: Column name to add
- `IN column_definition TEXT`: Column definition (type, constraints)

**When Used**: During database migrations and schema updates
**Why Used**: Ensures safe schema modifications without errors
**Usage**:
```sql
CALL AddColumnIfNotExists('users', 'last_login', 'TIMESTAMP NULL');
```

---

## 🔧 **Functions Documentation**

### **GetUserRiskScore**
**Purpose**: Calculate user risk score based on fraud reports
**Parameters**:
- `IN p_user_id CHAR(36)`: User ID to evaluate
**Returns**: `INT` - Risk score (0-100)

**When Used**: Called during fraud detection and transaction validation
**Why Used**: Provides quantitative risk assessment for users
**Usage**:
```sql
SELECT GetUserRiskScore('user-id') as risk_score;
```

**Risk Score Calculation**:
- 0 reports: 0 risk
- 1 report: 25 risk
- 2 reports: 50 risk
- 3 reports: 75 risk
- 4+ reports: 100 risk (maximum)

---

## 🔧 **Triggers Documentation**

### **tr_transaction_audit**
**Purpose**: Automatically log all transactions for audit trail
**Trigger Type**: AFTER INSERT on `transactions`
**When Used**: Fired automatically after every transaction insertion
**Why Used**: Ensures complete audit trail of all financial transactions
**Action**: Inserts audit log entry into `admin_logs` table

### **tr_balance_validation**
**Purpose**: Validate user balance updates and prevent negative balances
**Trigger Type**: BEFORE UPDATE on `users`
**When Used**: Fired before any balance update
**Why Used**: Prevents data integrity issues and logs significant balance changes
**Actions**:
- Prevents negative balance updates
- Logs balance changes > 10,000 for monitoring

### **tr_fraud_detection**
**Purpose**: Automatically detect suspicious transaction patterns
**Trigger Type**: AFTER INSERT on `transactions`
**When Used**: Fired after each transaction insertion
**Why Used**: Real-time fraud detection without manual intervention
**Detection Rules**:
- More than 5 transactions in 1 hour
- Total transaction amount > 50,000 in 1 hour
**Action**: Automatically adds user to fraud_list for investigation

### **tr_user_registration**
**Purpose**: Handle new user registration tasks
**Trigger Type**: AFTER INSERT on `users`
**When Used**: Fired after new user creation
**Why Used**: Ensures proper user setup and logging
**Actions**:
- Sets default USER role if not specified
- Logs user registration in admin_logs

---

## 📊 **Common Database Queries Used in Application**

### **Authentication Queries** (from `auth.py`)
```sql
-- Get user by login identifier
SELECT * FROM users u 
JOIN contact_info c ON u.id = c.user_id 
WHERE LOWER(c.email) = LOWER(%s) OR c.phone = %s OR u.id = %s;

-- Verify password
SELECT password_hash FROM user_passwords WHERE user_id = %s;
```

### **Transaction Queries** (from `transaction_utils.py`)
```sql
-- Get user balance
SELECT balance FROM users WHERE id = %s;

-- Update user balance
UPDATE users SET balance = balance + %s WHERE id = %s;

-- Insert transaction
INSERT INTO transactions (id, sender_id, receiver_id, amount, payment_method, description, timestamp) 
VALUES (%s, %s, %s, %s, %s, %s, %s);
```

### **Fraud Detection Queries** (from `fraud_utils.py`)
```sql
-- Check if user is flagged for fraud
SELECT COUNT(*) FROM fraud_list WHERE reported_user_id = %s;

-- Add fraud report
INSERT INTO fraud_list (id, user_id, reported_user_id, reason, created_at) 
VALUES (%s, %s, %s, %s, %s);

-- Get fraud reports
SELECT f.*, u1.first_name as reporter_name, u2.first_name as reported_name 
FROM fraud_list f 
JOIN users u1 ON f.user_id = u1.id 
JOIN users u2 ON f.reported_user_id = u2.id 
ORDER BY f.created_at DESC;
```

### **Blockchain Queries** (from `blockchain_utils.py`)
```sql
-- Get latest blockchain block
SELECT `index`, hash FROM blockchain ORDER BY `index` DESC LIMIT 1;

-- Insert blockchain block
INSERT INTO blockchain (id, `index`, timestamp, transaction_data, previous_hash, hash, transaction_id) 
VALUES (%s, %s, %s, %s, %s, %s, %s);

-- Insert blockchain transaction
INSERT INTO blockchain_transactions (id, user_id, amount, current_balance, method, timestamp) 
VALUES (%s, %s, %s, %s, %s, %s);

-- Validate blockchain integrity
SELECT id, `index`, hash, previous_hash FROM blockchain ORDER BY `index`;
```

### **Budget Queries** (from `budget_utils.py`)
```sql
-- Get user budget
SELECT * FROM budgets WHERE user_id = %s;

-- Insert/Update budget
INSERT INTO budgets (id, user_id, name, currency, income_source, amount, start_date, end_date) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
ON DUPLICATE KEY UPDATE name=%s, currency=%s, income_source=%s, amount=%s;

-- Get budget categories
SELECT * FROM budget_expense_categories WHERE budget_id = %s;
```

### **Admin Queries** (from `admin_utils.py`)
```sql
-- Get all users with roles
SELECT u.*, r.name as role_name FROM users u 
JOIN roles r ON u.role_id = r.id 
ORDER BY u.joining_date DESC;

-- Get transaction analytics
SELECT DATE(timestamp) as date, COUNT(*) as count, SUM(amount) as total 
FROM transactions 
WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY) 
GROUP BY DATE(timestamp) 
ORDER BY date DESC;

-- Get system statistics
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM transactions) as total_transactions,
    (SELECT SUM(amount) FROM transactions) as total_volume,
    (SELECT COUNT(*) FROM fraud_list) as fraud_reports;
```

### **Permission Queries** (from `permissions_utils.py`)
```sql
-- Check user permissions
SELECT p.name FROM permissions p 
JOIN role_permissions rp ON p.id = rp.permission_id 
JOIN users u ON rp.role_id = u.role_id 
WHERE u.id = %s AND p.name = %s;

-- Get all roles
SELECT * FROM roles ORDER BY name;

-- Get role permissions
SELECT p.* FROM permissions p 
JOIN role_permissions rp ON p.id = rp.permission_id 
WHERE rp.role_id = %s;
```

---

This comprehensive documentation covers all database components, queries, stored procedures, functions, triggers, and their usage throughout the FinGuard application. Use this as a complete reference for database operations and troubleshooting.
