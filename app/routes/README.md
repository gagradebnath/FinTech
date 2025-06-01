# FinGuard App Routes

This folder contains all Flask route blueprints for the FinGuard application. Each file corresponds to a specific feature or module of the app.

## Route Files

- `user.py`: User registration, login, dashboard, profile, and expense habit endpoints.
- `admin.py`: (Scaffold) Admin-specific endpoints.
- `agent.py`: (Scaffold) Agent-specific endpoints.
- `budget.py`: Budget planning and saving endpoints.
- `transaction.py`: Money transfer and transaction endpoints.
- `fraud.py`: (Scaffold) Fraud reporting endpoints.
- `chat.py`: (Scaffold) AI chat endpoints.
- `__init__.py`: Registers all blueprints with the Flask app.

## How to Add a New Route

1. Create a new `.py` file in this folder for your feature.
2. Define a Flask `Blueprint` and your routes in that file.
3. Import and register your blueprint in `__init__.py`.

### Example: Adding a Route
```python
# In app/routes/hello.py
from flask import Blueprint
hello_bp = Blueprint('hello', __name__)

@hello_bp.route('/hello')
def hello():
    return 'Hello, world!'

# In app/routes/__init__.py
from .hello import hello_bp

def register_blueprints(app):
    app.register_blueprint(hello_bp)
```

## Notes
- Keep each route file focused on a single feature or module for maintainability.
- Use helper functions from `app/utils/` as needed.
- For more details, see the main `README.md` in the project root or the `app/README.md` file.
