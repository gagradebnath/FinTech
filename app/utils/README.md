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

### `blockchain.py`
Blockchain logic (planned).
- (To be implemented)

---

This README lists all utility modules and their functions, with parameters, return values, and usage. Use this as a reference for backend development in FinGuard.
