# FinGuard App Routes

This folder contains all Flask route blueprints for the FinGuard application. Each file corresponds to a specific feature or module of the app. Use these routes to handle HTTP requests and render templates or return JSON responses.

## Route Files and Main Functions

### `user.py`
User registration, login, dashboard, profile, and expense habit endpoints.
- `@user_bp.route('/login', methods=['GET', 'POST'])`
  - User login page and logic.
  - Params: login_id, password, role (form fields)
  - Returns: Renders login page or redirects to dashboard.
  - Example:
    ```python
    @user_bp.route('/login', methods=['GET', 'POST'])
    def login():
        ...
    ```
- `@user_bp.route('/register', methods=['GET', 'POST'])`
  - User registration page and logic.
  - Params: first_name, last_name, dob, etc. (form fields)
  - Returns: Renders registration page or redirects to login.
- `@user_bp.route('/dashboard', methods=['GET'])`
  - User dashboard with budgets and recent transactions.
  - Returns: Renders dashboard template.
- `@user_bp.route('/profile', methods=['GET', 'POST'])`
  - View and update user profile.
  - Returns: Renders profile page.
- `@user_bp.route('/expense-habit', methods=['GET', 'POST'])`
  - View and update expense habit info.
  - Returns: Renders expense habit page.

### `admin.py`
Admin dashboard and management endpoints.
- `@admin_bp.route('/admin/dashboard', methods=['GET', 'POST'])`
  - Admin dashboard: manage agents, users, fraud, roles, permissions, logs.
  - Returns: Renders admin dashboard template.
  - Example:
    ```python
    @admin_bp.route('/admin/dashboard', methods=['GET', 'POST'])
    def admin_dashboard():
        ...
    ```

### `agent.py`
Agent dashboard and money management endpoints.
- `@agent_bp.route('/agent/dashboard', methods=['GET', 'POST'])`
  - Agent dashboard: add money to users, cash out, view transactions.
  - Returns: Renders agent dashboard template.
  - Example:
    ```python
    @agent_bp.route('/agent/dashboard', methods=['GET', 'POST'])
    def agent_dashboard():
        ...
    ```

### `budget.py`
Budget planning and saving endpoints.
- `@budget_bp.route('/plan-budget', methods=['GET', 'POST'])`
  - Budget planning page and logic.
  - Returns: Renders plan_budget template.
- `@budget_bp.route('/save_budget', methods=['POST'])`
  - Save a full budget via AJAX/JSON.
  - Params: budgetName, currency, income, expenses (JSON)
  - Returns: JSON response with success/error.

### `transaction.py`
Money transfer and transaction endpoints.
- `@transaction_bp.route('/send-money', methods=['GET', 'POST'])`
  - Send money to another user.
  - Params: recipient_identifier, amount, payment_method, note, location (form fields)
  - Returns: Renders send_money template with result.
  - Example:
    ```python
    @transaction_bp.route('/send-money', methods=['GET', 'POST'])
    def send_money_route():
        ...
    ```

### `fraud.py`
Fraud reporting endpoints.
- `@fraud_bp.route('/report-fraud', methods=['GET', 'POST'])`
  - Report a user for fraud.
  - Params: reported_user_identifier, reason (form fields)
  - Returns: Renders report_fraud template with result.

### `chat.py`
AI chat endpoints (scaffold).
- `@chat_bp.route('/chat', methods=['GET'])`
  - Returns: JSON message for chat endpoint.

### `__init__.py`
Blueprint registration.
- `register_blueprints(app)`
  - Registers all blueprints with the Flask app.
  - Usage:
    ```python
    from .user import user_bp
    from .admin import admin_bp
    ...
    def register_blueprints(app):
        app.register_blueprint(user_bp)
        app.register_blueprint(admin_bp)
        ...
    ```

---

## Example Usage: Calling Utility Functions in Routes

Most routes use utility functions from `app/utils/` for business logic and database access. For example:

```python
from app.utils.auth import get_user_by_login_id, check_password
from app.utils.dashboard import get_user_budgets, get_recent_expenses
from app.utils.transaction_utils import send_money

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    ...

@user_bp.route('/dashboard')
def dashboard():
    user = get_current_user()
    budgets = get_user_budgets(user['id'])
    expenses = get_recent_expenses(user['id'])
    ...

@transaction_bp.route('/send-money', methods=['GET', 'POST'])
def send_money_route():
    ...
    ok, msg, updated_user = send_money(user['id'], recipient['id'], amount, payment_method, note, location, 'transfer')
    ...
```

This README lists all route files and their main endpoints, with parameters, return values, and usage. Use this as a reference for backend development in FinGuard.
