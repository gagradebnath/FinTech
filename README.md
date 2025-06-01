# FinGuard: Personal Finance Management Web App

FinGuard is a personal finance management web application built with Flask and SQLite. It supports multiple user roles (admin, agent, user), robust access controls, budget planning, fraud reporting, AI chat, blockchain transaction logging, and user dashboards. The frontend uses Bootstrap for a modern, responsive UI.

## Features

- **User Roles:** Admin, Agent, User (with role-based access control)
- **User Registration & Login:**
  - Register/login with user ID, email, or phone
  - 8-character alphanumeric user IDs
  - Unique email and phone enforced
  - Pop-up feedback for registration/login
- **Dashboard:**
  - User-specific info (balance, budgets, recent expenses)
  - Navigation to profile, budget, send money, and expense habit pages
- **Profile Management:**
  - View and update personal info (name, email, phone, etc.)
- **Expense Habit Tracking:**
  - Save and edit spending habits
- **Budget Planning:**
  - Dynamic budget planner with income/expense categories
  - Save budgets and view previous ones
- **Send Money:**
  - Transfer funds to other users with validation
- **Fraud Reporting:**
  - Report suspicious users (feature scaffolded)
- **AI Chat:**
  - AI-powered financial assistant (feature scaffolded)
- **Blockchain Logging:**
  - Transaction logging for transparency (feature scaffolded)
- **Bootstrap Frontend:**
  - Responsive, modern UI with popups and navigation

## Project Structure

```text
app/
  __init__.py
  config.py
  models.py (placeholder)
  README.md
  routes/
    __init__.py
    user.py
    admin.py
    agent.py
    budget.py
    transaction.py
    fraud.py
    chat.py
    README.md
    __pycache__/
  static/
    README.md
    css/
      style.css
    js/
      main.js
      budget.js
  templates/
    README.md
    base.html
    index.html
    login.html
    register.html
    dashboard.html
    profile.html
    expense_habit.html
    plan_budget.html
    send_money.html
  utils/
    __init__.py
    auth.py
    blockchain.py
    budget_utils.py
    dashboard.py
    expense_habit.py
    notifications.py
    profile.py
    README.md
    register.py
    transaction_utils.py
    user_utils.py
    __pycache__/
DatabaseSchema.sql
fin_guard.db
requirements.txt
run.py
seed_sqlite.py
README.md
```

## Setup & Usage

1. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```
2. **Initialize the database:**
   ```cmd
   python seed_sqlite.py
   ```
3. **Run the app:**
   ```cmd
   python run.py
   ```
4. **Access the app:**
   Open your browser to [http://localhost:5000](http://localhost:5000)

## Database
- SQLite database (`fin_guard.db`)
- Schema defined in `DatabaseSchema.sql`
- Seed script: `seed_sqlite.py`

## Main Functions and Endpoints

### User Management (`user.py`)
- **login**: Handles user login via user ID, email, or phone. Sets session for logged-in user.
- **register**: Handles user registration, enforces unique email/phone, and creates user/contact records.
- **get_current_user**: Utility to fetch the current user from session.
- **dashboard**: Displays user dashboard with balance, budgets, and recent expenses.
- **expense_habit**: Allows users to save and edit their expense/spending habits.
- **profile**: View and update user profile information.
- **log_js_message**: Receives and logs messages from frontend JS to the server terminal.

### Budget Management (`budget.py`)
- **plan_budget**: Renders the budget planning page and handles form submissions for simple budget info.
- **save_budget**: Receives and saves detailed budget data (income, categories, items) from the dynamic planner (AJAX/JS).

### Transactions (`transaction.py`)
- **send_money**: Handles sending money between users, including validation and balance updates.

### Admin, Agent, Fraud, Chat Endpoints
- **admin.get_admin**: Placeholder for admin-specific endpoints.
- **agent.get_agent**: Placeholder for agent-specific endpoints.
- **fraud.get_fraud**: Placeholder for fraud reporting endpoints.
- **chat.get_chat**: Placeholder for AI chat endpoints.

### Utilities (in `app/utils/`)
- **auth.py**: Authentication and access control helpers (e.g., user lookup, password check).
- **register.py**: Registration helpers (unique checks, user creation, role lookup).
- **user_utils.py**: User session and fetch helpers.
- **dashboard.py**: Dashboard queries (budgets, recent expenses).
- **expense_habit.py**: Expense habit fetch and update.
- **profile.py**: User profile fetch and update.
- **budget_utils.py**: Budget CRUD and expense category/item helpers.
- **transaction_utils.py**: Transaction logic (send money, user fetch).
- **blockchain.py**: (Planned) Blockchain logic for transaction storage.
- **notifications.py**: (Planned) Notification utilities (fraud alerts, etc.).

## How to Change and Debug

### Making Changes
- **Edit Python code:**
  - All backend logic is in the `app/routes/` directory. For example, to change budget logic, edit `budget.py`.
  - Templates (HTML) are in `app/templates/`. For UI changes, edit the relevant HTML file.
  - Static files (JS, CSS) are in `app/static/`.
- **Database schema:**
  - To change the database structure, edit `DatabaseSchema.sql` and re-run `seed_sqlite.py` (note: this will reset your data).
- **Add new features:**
  - Create a new route file in `app/routes/` and register its blueprint in `app/routes/__init__.py`.
  - Add new templates or static files as needed.

### Debugging
- **Enable debug mode:**
  - The app runs in debug mode by default (`app.run(debug=True)` in `run.py`). This provides detailed error messages in the browser.
- **View logs:**
  - Print statements in Python will appear in your terminal.
  - JS logs can be sent to the server using the `/log` endpoint, or viewed in the browser console (F12).
- **Common issues:**
  - If you see a `BuildError` for a route, check that you are using the correct blueprint name in `url_for` (e.g., `budget.plan_budget` not `user.plan_budget`).
  - If the database schema changes, re-run `seed_sqlite.py` to reset tables.
- **Hot reload:**
  - Flask will auto-reload on code changes when in debug mode. If not, restart the server manually.
- **Windows users:**
  - Use `python run.py` in `cmd.exe` to start the server.

## License

© 2025 Ghagra Salem Debnath. All rights reserved.
