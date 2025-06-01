# FinGuard App Module

This folder contains the main application code for the FinGuard personal finance management system.

## Structure

- `__init__.py`: App factory and database connection setup.
- `config.py`: Flask configuration.
- `models.py`: (Placeholder) For ORM models if needed in the future.
- `routes/`: All Flask route blueprints, organized by feature/module.
- `static/`: Static files (CSS, JS) for the frontend.
- `templates/`: Jinja2 HTML templates for all pages.
- `utils/`: Utility modules for authentication, blockchain, notifications, etc.

## How to Extend

- Add new features by creating a new file in `routes/` and registering its blueprint in `routes/__init__.py`.
- Add new templates to `templates/` and static assets to `static/`.
- Place shared helper functions in `utils/`.

## Notes
- All database access uses direct `sqlite3` queries for simplicity.
- For advanced features (AI, blockchain, notifications), see the `utils/` folder for extension points.

For overall project setup, see the main `README.md` in the project root.
