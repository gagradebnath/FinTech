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

## Example: Using Utility Functions in Routes

### User Login (user.py)
```python
from app.utils.auth import get_user_by_login_id, check_password

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form.get('login_id')
        password = request.form.get('password')
        user = get_user_by_login_id(login_id)
        if user and check_password(user['id'], password):
            session['user_id'] = user['id']
            return redirect(url_for('user.dashboard'))
    return render_template('login.html')
```

### Dashboard with Utility Queries (user.py)
```python
from app.utils.dashboard import get_user_budgets, get_recent_expenses

@user_bp.route('/dashboard')
def dashboard():
    user = get_current_user()
    budgets = get_user_budgets(user['id'])
    expenses = get_recent_expenses(user['id'])
    return render_template('dashboard.html', user=user, budgets=budgets, expenses=expenses)
```

### Budget Planning (budget.py)
```python
from app.utils.budget_utils import get_user_budget, save_or_update_budget

@budget_bp.route('/plan-budget', methods=['GET', 'POST'])
def plan_budget():
    user = get_current_user()
    budget = get_user_budget(user['id'])
    if request.method == 'POST':
        name = request.form.get('name')
        currency = request.form.get('currency')
        income_source = request.form.get('income_source')
        amount = request.form.get('amount')
        budget = save_or_update_budget(user['id'], name, currency, income_source, amount)
    return render_template('plan_budget.html', budget=budget)
```

### Sending Money (transaction.py)
```python
from app.utils.transaction_utils import send_money

@transaction_bp.route('/send-money', methods=['GET', 'POST'])
def send_money_route():
    user = get_current_user()
    if request.method == 'POST':
        recipient_id = request.form.get('recipient_id')
        amount = request.form.get('amount')
        note = request.form.get('note')
        payment_method = request.form.get('payment_method')
        ok, msg, updated_user = send_money(user['id'], recipient_id, amount, note, payment_method)
    return render_template('send_money.html')
```

## Notes
- Keep each route file focused on a single feature or module for maintainability.
- Use helper functions from `app/utils/` for all database and business logic.
- For more details, see the main `README.md` in the project root or the `app/README.md` file.
