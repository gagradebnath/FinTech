# FinGuard Templates

This folder contains all Jinja2 HTML templates for the FinGuard web application. Templates define the structure and layout of the web pages rendered by Flask.

## Structure

- `base.html`: The main layout template. Other templates extend this for consistent navigation and styling.
- `index.html`: Landing page for the app.
- `login.html`, `register.html`: User authentication pages.
- `dashboard.html`: User dashboard with summary info.
- `profile.html`: User profile view/edit page.
- `expense_habit.html`: Form for tracking user expense habits.
- `plan_budget.html`: Dynamic budget planner page.
- `send_money.html`: Page for sending money to other users.

## How to Use

- To create a new page, add a new `.html` file here and extend `base.html` for consistent layout.
- Use Jinja2 templating syntax (`{{ ... }}` and `{% ... %}`) to insert dynamic content from Flask.
- Reference static assets (CSS/JS) using `{{ url_for('static', filename='...') }}`.

### Example: Extending the Base Template
```html
{% extends 'base.html' %}
{% block content %}
<h1>My New Page</h1>
{% endblock %}
```

## Notes
- Keep templates modular and reusable by using blocks and includes.
- For UI changes, edit the relevant template and reload the page in your browser.
- For more information, see the main `README.md` in the project root.
