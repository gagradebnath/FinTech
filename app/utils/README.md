# FinGuard Utilities (`utils`)

This folder contains utility modules for the FinGuard application. These modules provide helper functions and logic that support the main features of the app.

## Files

- `auth.py`: (Planned) Authentication and access control helpers for user sessions, permissions, etc.
- `blockchain.py`: (Planned) Blockchain logic for transaction storage and verification.
- `notifications.py`: (Planned) Notification utilities, such as fraud alerts or user notifications.
- `__init__.py`: Marks this folder as a Python package.

## How to Use Utilities

### Example: Adding a Helper Function
Suppose you want to add a function to check if a user is an admin:

```python
# In app/utils/auth.py

def is_admin(user):
    return user and user.get('role') == 'admin'
```

You can then use this function in your route files:

```python
# In app/routes/user.py
from app.utils.auth import is_admin

@user_bp.route('/admin-only')
def admin_only():
    user = get_current_user()
    if not is_admin(user):
        return 'Access denied', 403
    return 'Welcome, admin!'
```

### Example: Blockchain Utility (Scaffold)
```python
# In app/utils/blockchain.py

def log_transaction_to_blockchain(transaction):
    # Add transaction to blockchain (to be implemented)
    pass
```

### Example: Notification Utility (Scaffold)
```python
# In app/utils/notifications.py

def send_fraud_alert(user_id, message):
    # Send a notification to the user (to be implemented)
    pass
```

## Best Practices
- Place shared helper functions or classes here to keep route files clean and modular.
- Keep utility modules focused on a single responsibility for maintainability.
- Import utilities in your route files as needed, e.g.:
  ```python
  from app.utils.auth import is_admin
  ```

## Notes
- These files are currently scaffolds and can be extended as the project grows.
- For more information, see the main `README.md` in the project root.
