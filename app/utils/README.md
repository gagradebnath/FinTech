# FinGuard Utilities (`utils`)

This folder contains utility modules for the FinGuard application. These modules provide helper functions and logic that support the main features of the app.

## Files

- `auth.py`: (Planned) Authentication and access control helpers for user sessions, permissions, etc.
- `blockchain.py`: (Planned) Blockchain logic for transaction storage and verification.
- `notifications.py`: (Planned) Notification utilities, such as fraud alerts or user notifications.
- `__init__.py`: Marks this folder as a Python package.

## How to Use

- Place shared helper functions or classes here to keep route files clean and modular.
- Import utilities in your route files as needed, e.g.:
  ```python
  from app.utils.auth import some_auth_function
  ```

## Notes
- These files are currently scaffolds and can be extended as the project grows.
- Keep utility modules focused on a single responsibility for maintainability.

For more information, see the main `README.md` in the project root.
