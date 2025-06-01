# FinGuard Utilities (`utils`)

This folder contains utility modules for the FinGuard application. These modules provide helper functions and logic that support the main features of the app. All database access and business logic is handled here for maintainability and testability.

## Files and Main Functions

- `auth.py`: Authentication helpers (user lookup, password check)
- `register.py`: Registration helpers (unique checks, user creation, role lookup)
- `user_utils.py`: User session and fetch helpers
- `dashboard.py`: Dashboard queries (budgets, recent expenses)
- `expense_habit.py`: Expense habit fetch and update
- `profile.py`: User profile fetch and update
- `budget_utils.py`: Budget CRUD and expense category/item helpers
- `transaction_utils.py`: Transaction logic (send money, user fetch)
- `blockchain.py`: (Planned) Blockchain logic for transaction storage
- `notifications.py`: (Planned) Notification utilities (fraud alerts, etc.)
- `__init__.py`: Marks this folder as a Python package

## Usage Examples

### Authentication (`auth.py`)
```python
from app.utils.auth import get_user_by_login_id, check_password
user = get_user_by_login_id('john@example.com')
if user and check_password(user['id'], 'secret'):
    # Authenticated
    pass
```

### Registration (`register.py`)
```python
from app.utils.register import is_email_unique, create_user_and_contact
if is_email_unique('new@example.com'):
    user_id, err = create_user_and_contact(...)
```

### User Session (`user_utils.py`)
```python
from app.utils.user_utils import get_current_user
user = get_current_user()
```

### Dashboard Queries (`dashboard.py`)
```python
from app.utils.dashboard import get_user_budgets, get_recent_expenses
budgets = get_user_budgets(user['id'])
expenses = get_recent_expenses(user['id'])
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

### Transaction Utilities (`transaction_utils.py`)
```python
from app.utils.transaction_utils import send_money
ok, msg, updated_user = send_money(sender_id, recipient_id, amount, note, payment_method)
```

### Blockchain & Notifications (Planned)
```python
# In app/utils/blockchain.py
# def log_transaction_to_blockchain(transaction): ...

# In app/utils/notifications.py
# def send_fraud_alert(user_id, message): ...
```

## Best Practices
- Place shared helper functions or classes here to keep route files clean and modular.
- Keep utility modules focused on a single responsibility for maintainability.
- Import utilities in your route files as needed, e.g.:
  ```python
  from app.utils.dashboard import get_user_budgets
  ```
