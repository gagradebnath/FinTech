# FinGuard Utilities (`utils`)

This folder contains all the core utility modules for the FinGuard application. These modules encapsulate database access, business logic, and helper functions for each major feature of the app. By centralizing logic here, the project ensures that route files remain clean, maintainable, and easy to test.

## Why Use Utilities?
- **Separation of Concerns:** Keeps route/view code focused on HTTP and UI logic, not database details.
- **Reusability:** Utility functions can be reused across different routes and features.
- **Maintainability:** Changes to business logic or database queries are made in one place.
- **Testability:** Utilities can be tested independently from Flask routes.

## Utility Modules Overview

- **`auth.py`**: User authentication helpers (login lookup, password check).
- **`register.py`**: Registration helpers (unique email/phone checks, user creation, role lookup).
- **`user_utils.py`**: User session management and user fetch by ID or session.
- **`dashboard.py`**: Dashboard queries (fetch budgets, recent expenses, recent transactions for a user).
- **`expense_habit.py`**: Fetch and update user expense/spending habits.
- **`profile.py`**: Fetch and update user profile and contact info.
- **`budget_utils.py`**: Budget CRUD (create, read, update) and helpers for budget categories/items.
- **`transaction_utils.py`**: All transaction logic (send money, agent add/cash out, user lookup, fraud check).
- **`admin_utils.py`**: Admin dashboard logic (user/agent/transaction/fraud queries, admin logs, role changes, etc.).
- **`permissions_utils.py`**: Role and permission management (assign/revoke/check permissions, fetch roles/permissions).
- **`fraud_utils.py`**: Fraud reporting and lookup helpers.
- **`blockchain.py`**: (Planned) Blockchain logic for transaction storage and verification.
- **`notifications.py`**: (Planned) Notification utilities (fraud alerts, user notifications, etc.).
- **`__init__.py`**: Marks this folder as a Python package.

## How to Use Utilities

Import the relevant function(s) in your route or business logic file. Each utility is designed to be self-contained and safe for use in Flask request contexts.

### Authentication (`auth.py`)
```python
from app.utils.auth import get_user_by_login_id, check_password
user = get_user_by_login_id('john@example.com')
if user and check_password(user['id'], 'secret'):
    # Authenticated
    ...
```

### Registration (`register.py`)
```python
from app.utils.register import is_email_unique, create_user_and_contact
if is_email_unique('new@example.com'):
    user_id, err = create_user_and_contact(...)
```

### User Session (`user_utils.py`)
```python
from app.utils.user_utils import get_current_user, get_role_name_by_id
user = get_current_user()
role = get_role_name_by_id(user['role_id'])
```

### Dashboard Queries (`dashboard.py`)
```python
from app.utils.dashboard import get_user_budgets, get_recent_expenses, get_recent_transactions
budgets = get_user_budgets(user['id'])
expenses = get_recent_expenses(user['id'])
transactions = get_recent_transactions(user['id'])
```

### Expense Habit (`expense_habit.py`)
```python
from app.utils.expense_habit import get_expense_habit, upsert_expense_habit
habit = get_expense_habit(user['id'])
habit = upsert_expense_habit(user['id'], data)
```

### Profile (`profile.py`)
```python
from app.utils.profile import get_user_and_contact, update_user_and_contact
user, contact = get_user_and_contact(user_id)
user, contact = update_user_and_contact(user_id, user_data, contact_data)
```

### Budget Utilities (`budget_utils.py`)
```python
from app.utils.budget_utils import get_user_budget, save_or_update_budget, insert_full_budget
budget = get_user_budget(user['id'])
budget = save_or_update_budget(user['id'], name, currency, income_source, amount)
success, err = insert_full_budget(user['id'], budget_name, currency, income, expenses)
```

### Admin Utilities (`admin_utils.py`)
```python
from app.utils.admin_utils import (
    get_role_name_by_id,  # (role_id: str) -> str | None: Get the name of a role given its ID
    get_agents,           # () -> list[Row]: Get all users with the 'agent' role
    get_all_users,        # () -> list[Row]: Get all users in the system
    get_all_transactions, # (limit: int = 100) -> list[Row]: Get all transactions, with sender/receiver names
    get_all_frauds,       # (limit: int = 100) -> list[Row]: Get all fraud reports, with reporter and reported user info
    get_admin_logs,       # (limit: int = 100) -> list[Row]: Get all admin log entries
    update_user_balance,  # (user_id: str, amount: float) -> None: Add/subtract balance for a user (admin action)
    insert_transaction_admin, # (tx_id: str, amount: float, sender_id: str, receiver_id: str, note: str, tx_type: str) -> None: Insert a transaction performed by an admin
    insert_admin_log,     # (log_id: str, admin_id: str, ip_address: str, details: str) -> None: Log an admin operation (for auditing)
    insert_fraud_list,    # (fraud_id: str, user_id: str, reported_user_id: str, reason: str) -> None: Add a user to the fraud list
    delete_fraud_list,    # (reported_user_id: str) -> None: Remove a user from the fraud list
    update_user_role,     # (user_id: str, new_role_id: str) -> None: Change a user's role
    get_role_id_by_name   # (role_name: str) -> str | None: Get a role's ID from its name
)
role = get_role_name_by_id(role_id)  # Returns role name as string or None
agents = get_agents()  # Returns list of agent users (sqlite3.Row)
users = get_all_users()  # Returns list of all users (sqlite3.Row)
transactions = get_all_transactions()  # Returns list of all transactions (sqlite3.Row)
frauds = get_all_frauds()  # Returns list of all fraud reports (sqlite3.Row)
logs = get_admin_logs()  # Returns list of admin log entries (sqlite3.Row)
update_user_balance(user_id, 100)  # No return value
insert_transaction_admin(tx_id, 100, sender_id, receiver_id, 'note', 'admin_add_money')  # No return value
insert_admin_log(log_id, admin_id, ip, 'details')  # No return value
insert_fraud_list(fraud_id, user_id, reported_user_id, 'reason')  # No return value
delete_fraud_list(reported_user_id)  # No return value
update_user_role(user_id, new_role_id)  # No return value
role_id = get_role_id_by_name('admin')  # Returns role ID as string or None
```

### Transaction Utilities (`transaction_utils.py`)
```python
from app.utils.transaction_utils import (
    send_money,                # (sender_id: str, recipient_id: str, amount: float, payment_method: str, note: str, location: str, tx_type: str) -> tuple[bool, str, Row | None]: Transfer money between users (with validation)
    get_user_by_id,            # (user_id: str) -> Row | None: Fetch a user by their ID
    agent_add_money,           # (agent_id: str, user_id: str, amount: float) -> tuple[str | None, str | None]: Agent adds money to a user (debits agent, credits user)
    agent_cash_out,            # (agent_id: str, user_id: str, amount: float) -> tuple[str | None, str | None]: Agent cashes out from a user (debits user, credits agent)
    lookup_user_by_identifier, # (identifier: str) -> Row | None: Find user by ID, email, or phone
    is_user_flagged_fraud      # (user_id: str) -> bool: Check if a user is on the fraud list
)
user = get_user_by_id(user_id)  # Returns user record (sqlite3.Row) or None
ok, msg, updated_user = send_money(sender_id, recipient_id, amount, payment_method, note, location, tx_type)  # ok: bool, msg: str, updated_user: Row or None
msg, err = agent_add_money(agent_id, user_id, amount)  # msg: str or None, err: str or None
msg, err = agent_cash_out(agent_id, user_id, amount)   # msg: str or None, err: str or None
user = lookup_user_by_identifier(identifier)  # Returns user (sqlite3.Row) or None
is_fraud = is_user_flagged_fraud(user_id)     # Returns True if user is flagged for fraud
```

### Permissions Utilities (`permissions_utils.py`)
```python
from app.utils.permissions_utils import (
    get_all_roles,            # () -> list[Row]: Get all roles in the system
    get_all_permissions,      # () -> list[Row]: Get all permissions in the system
    get_permissions_for_role, # (role_id: str) -> list[Row]: Get all permissions assigned to a role
    add_permission_to_role,   # (role_id: str, permission_id: str) -> None: Assign a permission to a role
    remove_permission_from_role, # (role_id: str, permission_id: str) -> None: Remove a permission from a role
    has_permission            # (user_id: str, permission_name: str) -> bool: Check if a user has a specific permission
)
roles = get_all_roles()  # Returns list of all roles (sqlite3.Row)
perms = get_all_permissions()  # Returns list of all permissions (sqlite3.Row)
role_perms = get_permissions_for_role(role_id)  # Returns list of permissions for a role (sqlite3.Row)
add_permission_to_role(role_id, perm_id)  # No return value
remove_permission_from_role(role_id, perm_id)  # No return value
if has_permission(user_id, 'send_money'):
    # Returns True if user has permission
    ...
```

### Fraud Utilities (`fraud_utils.py`)
```python
from app.utils.fraud_utils import lookup_user_by_identifier, add_fraud_report
user = lookup_user_by_identifier(identifier)  # (identifier: str) -> Row | None: Find user by ID/email/phone
success, err = add_fraud_report(reporter_id, reported_user_id, reason)  # (reporter_id: str, reported_user_id: str, reason: str) -> tuple[bool, str | None]: Report a user for fraud
```

### Dashboard Utilities (`dashboard.py`)
```python
from app.utils.dashboard import get_user_budgets, get_recent_expenses, get_recent_transactions
budgets = get_user_budgets(user['id'])  # (user_id: str) -> list[Row]: List of user's budgets
expenses = get_recent_expenses(user['id'])  # (user_id: str, limit: int = 5) -> list[Row]: List of user's recent expenses
transactions = get_recent_transactions(user['id'])  # (user_id: str, limit: int = 5) -> list[Row]: List of user's recent transactions
```

## Best Practices
- Place all database and business logic in these utility modules, not in route files.
- Keep each utility focused on a single responsibility (e.g., only transaction logic in `transaction_utils.py`).
- Import only what you need in each route file for clarity and performance.
- If you add a new feature, create a new utility module or extend an existing one as appropriate.

## Planned/Advanced Utilities
- **blockchain.py:** For blockchain-based transaction logging and verification.
- **notifications.py:** For sending fraud alerts, user notifications, etc.

---

This structure ensures that anyone new to the project can quickly find, understand, and use the business logic for any feature in FinGuard. If you have questions or want to contribute, see the main project README or contact the maintainers.
