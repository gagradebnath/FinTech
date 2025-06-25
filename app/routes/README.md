# FinGuard App Routes

This folder contains all Flask route blueprints for the FinGuard application. Each file corresponds to a specific feature or module of the app. These routes handle HTTP requests, render templates, and return JSON responses.

## Route Files and Main Functions

### `user.py`
User registration, login, dashboard, profile, and expense habit endpoints.
- `@user_bp.route('/login', methods=['GET', 'POST'])`
  - User login page and logic
  - Handles login via user ID, email, or phone
  - Verifies credentials and sets session
  - Returns: Renders login page or redirects to dashboard
  
- `@user_bp.route('/register', methods=['GET', 'POST'])`
  - User registration page and logic
  - Validates form data and creates new user account
  - Returns: Renders registration page or redirects to login
  
- `@user_bp.route('/dashboard', methods=['GET'])`
  - User dashboard with modern dark-themed UI
  - Displays account balance, budgets, transaction charts, and recent transactions
  - Returns: Renders dashboard template
  
- `@user_bp.route('/profile', methods=['GET', 'POST'])`
  - View and update user profile information
  - Returns: Renders profile page
  
- `@user_bp.route('/expense-habit', methods=['GET', 'POST'])`
  - View and update expense habit information
  - Returns: Renders expense habit page

### `admin.py`
Admin dashboard and management endpoints.
- `@admin_bp.route('/admin/dashboard', methods=['GET', 'POST'])`
  - Admin dashboard: manage agents, users, fraud, roles, permissions, logs
  - Returns: Renders admin dashboard template

### `agent.py`
Agent dashboard and money management endpoints.
- `@agent_bp.route('/agent/dashboard', methods=['GET', 'POST'])`
  - Agent dashboard: add money to users, cash out, view transactions
  - Returns: Renders agent dashboard template

### `budget.py`
Budget planning and saving endpoints.
- `@budget_bp.route('/plan-budget', methods=['GET', 'POST'])`
  - Budget planning page with dynamic form
  - Supports saving and loading previous budgets
  - Returns: Renders plan_budget template
  
- `@budget_bp.route('/save_budget', methods=['POST'])`
  - Save a full budget via AJAX/JSON
  - Handles categories and budget items
  - Returns: JSON response with success/error
  
- `@budget_bp.route('/get_budgets', methods=['GET'])`
  - Retrieve all budgets for the current user
  - Returns: JSON list of budgets
  
- `@budget_bp.route('/get_budget/<budget_id>', methods=['GET'])`
  - Retrieve a specific budget by ID
  - Returns: JSON with complete budget details

### `transaction.py`
Money transfer and transaction endpoints.
- `@transaction_bp.route('/send-money', methods=['GET', 'POST'])`
  - Send money to another user
  - Displays recent transactions in consistent dark-themed style
  - Validates recipient, amount, and processes transfer
  - Returns: Renders send_money template with result

### `fraud.py`
Fraud reporting endpoints.
- `@fraud_bp.route('/report-fraud', methods=['GET', 'POST'])`
  - Report a user for fraud
  - Modern dark-themed UI that fills available height
  - Returns: Renders report_fraud template with result

### `chat.py`
AI chat endpoints (scaffold).
- `@chat_bp.route('/chat', methods=['GET'])`
  - Returns: JSON message for chat endpoint (placeholder)

### `__init__.py`
Blueprint registration.
- `register_blueprints(app)`
  - Registers all blueprints with the Flask app

---

## Modern UI and Page Structures

All pages follow a consistent dark-themed UI structure:
- Modern dark theme with animated gradient backgrounds
- Responsive design using Bootstrap 5
- Cohesive color scheme across all pages
- Sidebar navigation (hidden on login, register, and index pages)
- Consistent card styles and data tables

## Example Usage: Calling Utility Functions in Routes

Most routes use utility functions from `app/utils/` for business logic and database access:

```python
from app.utils.auth import get_user_by_login_id, check_password
from app.utils.dashboard import get_user_budgets, get_recent_expenses
from app.utils.transaction_utils import send_money

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Authentication logic using auth.py utilities
    ...

@user_bp.route('/dashboard')
def dashboard():
    user = get_current_user()
    budgets = get_user_budgets(user['id'])
    expenses = get_recent_expenses(user['id'])
    # Render dashboard with fetched data
    ...

@transaction_bp.route('/send-money', methods=['GET', 'POST'])
def send_money_route():
    # Process money transfer using transaction_utils.py
    ok, msg, updated_user = send_money(user['id'], recipient['id'], amount, payment_method, note, location, 'transfer')
    ...
```

## How to Add a New Route

1. Create a new file in this directory (e.g., `new_feature.py`)
2. Define a Blueprint and routes
3. Register the Blueprint in `__init__.py`
4. Create corresponding templates and utility functions as needed

This documentation lists all route files and their main endpoints, with parameters, return values, and usage examples. Use this as a reference for backend development in FinGuard.
