# FinGuard: Personal Finance Management Web App

FinGuard is a comprehensive personal finance management web application built with Flask and SQLite. It features a modern dark-themed UI, supports multiple user roles (admin, agent, user), implements robust access controls, budget planning, fraud reporting, AI chat, blockchain transaction logging, and user dashboards. The frontend uses Bootstrap 5 for a responsive, modern UI.

## Features

- **User Roles:** Admin, Agent, User (with role-based access control)
- **User Registration & Login:**
  - Register/login with user ID, email, or phone
  - 8-character alphanumeric user IDs
  - Unique email and phone enforced
  - Pop-up feedback for registration/login
- **Dashboard:**
  - Modern dark-themed UI with animated gradient backgrounds
  - User-specific info (balance, budgets, recent expenses)
  - Transaction reports with visual charts
  - Navigation to profile, budget, send money, and expense habit pages
- **Profile Management:**
  - View and update personal info (name, email, phone, etc.)
- **Expense Habit Tracking:**
  - Save and edit spending habits
- **Budget Planning:**
  - Dynamic budget planner with income/expense categories
  - Save budgets and view/load previously saved budgets
  - Detailed category and item management
- **Send Money:**
  - Transfer funds to other users with validation
  - View recent transactions
- **Fraud Reporting:**
  - Report suspicious users
- **AI Chat:**
  - AI-powered financial assistant (feature scaffolded)
- **Blockchain Logging:**
  - Transaction logging for transparency (feature scaffolded)
- **Bootstrap Frontend:**
  - Responsive, modern dark UI with animated gradients
  - Consistent styling across all pages
  - Popups and navigational elements

## Project Structure

```text
app/
    __init__.py             # App factory, DB connection, JSON encoder
    config.py               # Flask configuration
    models.py               # (placeholder)
    README.md               # App module documentation
    routes/
        __init__.py         # Blueprint registration
        user.py             # User authentication and dashboard routes
        admin.py            # Admin dashboard and management routes
        agent.py            # Agent dashboard and operations routes
        budget.py           # Budget planning and saving routes
        transaction.py      # Money transfer routes
        fraud.py            # Fraud reporting routes
        chat.py             # AI chat routes (placeholder)
        README.md           # Routes documentation
    static/
        README.md           # Static assets documentation
        assets/             # Images and other assets
        css/
            style.css       # Main stylesheet
            landing.css     # Landing page specific styles
            login.css       # Login page styles
            dashboard.css   # Dashboard styles
            budget.css      # Budget page styles
            transaction.css # Transaction page styles
            fraud.css       # Fraud reporting styles
            and more...     # Other page-specific CSS files
        js/
            main.js         # Main JavaScript
            budget.js       # Budget page functionality
            finance-bg.js   # Background animations
            landing.js      # Landing page scripts
    templates/
        README.md           # Templates documentation
        base.html           # Base layout template
        index.html          # Landing page
        login.html          # Login page
        register.html       # Registration page
        dashboard.html      # User dashboard
        profile.html        # User profile
        expense_habit.html  # Expense habits
        plan_budget.html    # Budget planner
        send_money.html     # Money transfer
        report_fraud.html   # Fraud reporting
        admin_dashboard.html # Admin dashboard
        agent_dashboard.html # Agent dashboard
    utils/
        __init__.py         # Utility initialization
        admin_utils.py      # Admin operations
        auth.py             # Authentication helpers
        blockchain.py       # Blockchain logic (placeholder)
        budget_utils.py     # Budget CRUD operations
        dashboard.py        # Dashboard data retrieval
        expense_habit.py    # Expense habit operations
        fraud_utils.py      # Fraud reporting utilities
        notifications.py    # Notification system (placeholder)
        permissions_utils.py # Role and permission management
        profile.py          # Profile management
        README.md           # Utilities documentation
        register.py         # Registration helpers
        transaction_utils.py # Transaction logic
        user_utils.py       # User data access
DatabaseSchema.sql          # SQLite database schema
fin_guard.db                # SQLite database
requirements.txt            # Project dependencies
run.py                      # App entry point
seed_sqlite.py              # Database seeding script
README.md                   # This file
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

## Demo Accounts (For Quick Testing)

After running the seed script, you can log in with the following demo users:

| Role   | User ID | Password |
|--------|---------|----------|
| Admin  | admin   | admin    |
| Agent  | agent   | agent    |
| User   | user    | user     |

All demo accounts start with a balance of 10,000. You can use these credentials to test all admin, agent, and user flows immediately after setup.

## Database
- SQLite database (`fin_guard.db`)
- Schema defined in `DatabaseSchema.sql`
- Seed script: `seed_sqlite.py`

## Key Features and Functionality

### User Management
- Login/Registration with validation
- Role-based access control (Admin, Agent, User)
- Profile management

### Financial Management
- Dashboard with transaction history and visual charts
- Budget planning with categories and items
- Expense habit tracking
- Money transfers between users

### Admin and Agent Operations
- Admin dashboard for user management, fraud monitoring
- Agent dashboard for adding money, cash out operations
- Transaction monitoring

### UI Features
- Modern dark theme with animated gradient backgrounds
- Responsive design for all screen sizes
- Consistent styling across all pages

## Known Issues and Troubleshooting

### Flask Version Compatibility
- If you encounter a `JSONEncoder` import error, update `app/__init__.py` to use `json.JSONEncoder` instead of `flask.json.JSONEncoder`
- Alternatively, specify Flask version 2.2.x or earlier in requirements.txt

### Database Reset
- If you change the database schema, you'll need to re-run `seed_sqlite.py` to reset the database
- This will erase all existing data and create fresh tables with demo accounts

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
