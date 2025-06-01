# FinGuard App Module

This folder contains the main application code for the FinGuard personal finance management system.

## Structure

- `__init__.py`: App factory and database connection setup.
- `config.py`: Flask configuration.
- `models.py`: (Placeholder) For ORM models if needed in the future.
- `routes/`: All Flask route blueprints, organized by feature/module.
- `static/`: Static files (CSS, JS) for the frontend.
- `templates/`: Jinja2 HTML templates for all pages.
- `utils/`: Utility modules for authentication, blockchain, notifications, registration, etc.

## How to Extend

- Add new features by creating a new file in `routes/` and registering its blueprint in `routes/__init__.py`.
- Add new templates to `templates/` and static assets to `static/`.
- Place shared helper functions in `utils/`.

## Example: Registering a New Blueprint
```python
# In app/routes/myfeature.py
from flask import Blueprint
myfeature_bp = Blueprint('myfeature', __name__)

@myfeature_bp.route('/myfeature')
def myfeature():
    return 'Hello from my feature!'

# In app/routes/__init__.py
from .myfeature import myfeature_bp

def register_blueprints(app):
    app.register_blueprint(myfeature_bp)
```

## Notes
- All database access uses direct `sqlite3` queries for simplicity.
- For advanced features (AI, blockchain, notifications), see the `utils/` folder for extension points.
- For overall project setup and debugging, see the main `README.md` in the project root.
