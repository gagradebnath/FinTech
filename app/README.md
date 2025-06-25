# FinGuard App Module

This folder contains the main application code for the FinGuard personal finance management system.

## Structure

- `__init__.py`: App factory, database connection setup, and custom JSON encoder.
- `config.py`: Flask configuration settings.
- `models.py`: (Placeholder) For ORM models if needed in the future.
- `routes/`: All Flask route blueprints, organized by feature/module.
- `static/`: Static files (CSS, JS, assets) for the frontend.
- `templates/`: Jinja2 HTML templates for all pages.
- `utils/`: Utility modules for business logic, authentication, database operations, etc.

## Key Components

### App Factory
The `create_app()` function in `__init__.py` initializes the Flask application with:
- Custom JSON encoder for SQLite Row objects
- Database connection function
- Template filters for JSON serialization
- Blueprint registration

### Database Connection
The application uses SQLite with the Row factory for dictionary-like access to query results:
```python
def get_db_connection():
    conn = sqlite3.connect('fin_guard.db')
    conn.row_factory = sqlite3.Row
    return conn
```

### JSON Serialization
A custom JSON encoder and template filter handle SQLite Row objects:
```python
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'keys') and hasattr(obj, 'values'):
            return dict(obj)
        return super(CustomJSONEncoder, self).default(obj)

@app.template_filter('tojson_safe')
def tojson_safe(obj):
    if hasattr(obj, 'keys') and hasattr(obj, 'values'):
        obj = dict(obj)
    return json.dumps(obj)
```

## How to Extend

- Add new features by creating a new file in `routes/` and registering its blueprint in `routes/__init__.py`.
- Add new templates to `templates/` and static assets to `static/`.
- Place shared helper functions in `utils/`.
- Keep database queries in utility functions for better organization.

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
    # Add your new blueprint to this list
    app.register_blueprint(myfeature_bp)
```

## Notes
- All database access uses direct `sqlite3` queries for simplicity.
- For advanced features (AI, blockchain, notifications), see the `utils/` folder for extension points.
- For overall project setup and debugging, see the main `README.md` in the project root.
- If you encounter JSON serialization issues with Flask 2.3+, see the main README's troubleshooting section.
