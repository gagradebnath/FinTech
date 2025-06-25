# FinGuard Templates

This folder contains all Jinja2 HTML templates for the FinGuard web application. Templates define the structure and layout of the web pages rendered by Flask.

## Structure

- `base.html`: The main layout template with dark theme, sidebar, and navigation elements
- `index.html`: Landing page for the app with modern animated backgrounds
- `login.html`: User login page with dark theme styling
- `register.html`: User registration page with validation
- `dashboard.html`: User dashboard with transaction charts, stats cards, and recent transactions
- `profile.html`: User profile view/edit page
- `expense_habit.html`: Form for tracking user expense habits
- `plan_budget.html`: Dynamic budget planner with category management and saved budget loading
- `send_money.html`: Page for sending money to other users with transaction history
- `report_fraud.html`: Form for reporting suspicious users
- `admin_dashboard.html`: Admin dashboard for user/transaction management
- `agent_dashboard.html`: Agent dashboard for financial operations

## UI Implementation

All templates share a consistent modern dark theme with:

- Animated gradient backgrounds
- Responsive card layouts
- Modern table designs for data display
- Consistent navigation and user interface elements
- Dark-themed forms and inputs
- Bootstrap 5 integration with custom styling

### Base Template Structure

The `base.html` template provides the foundation for all pages with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Meta tags, title, and common CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block page_css %}{% endblock %}
</head>
<body>
    <div class="wrapper">
        <!-- Sidebar (conditionally shown) -->
        {% if current_page not in ['index', 'login', 'register'] %}
        <nav class="sidebar">
            <!-- Sidebar content -->
        </nav>
        {% endif %}
        
        <div class="main-content">
            <!-- Top navbar (conditionally shown) -->
            {% if current_page not in ['index', 'login', 'register'] %}
            <header class="top-navbar">
                <!-- Navbar content -->
            </header>
            {% endif %}
            
            <!-- Main content block for page-specific content -->
            {% block content %}{% endblock %}
        </div>
    </div>
    
    <!-- Common scripts and page-specific scripts -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block page_scripts %}{% endblock %}
</body>
</html>
```

## How to Use

- To create a new page, add a new `.html` file here and extend `base.html` for consistent layout.
- Use Jinja2 templating syntax (`{{ ... }}` and `{% ... %}`) to insert dynamic content from Flask.
- Reference static assets (CSS/JS) using `{{ url_for('static', filename='...') }}`.
- Add page-specific CSS in the `page_css` block and scripts in the `page_scripts` block.

### Example: Creating a New Page

```html
{% extends 'base.html' %}

{% block page_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/my_feature.css') }}">
{% endblock %}

{% block content %}
<div class="container py-4">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5 class="m-0">My New Feature</h5>
                </div>
                <div class="card-body">
                    <!-- Feature content -->
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_scripts %}
<script src="{{ url_for('static', filename='js/my_feature.js') }}"></script>
{% endblock %}
```

## Best Practices

- Keep templates modular by using blocks and includes
- Follow the established dark theme UI patterns
- Use consistent card and table structures
- Maintain responsive layouts
- Include proper form validation
- Use the same icon set (Bootstrap icons) throughout

## Notes

- All templates follow a cohesive dark theme with consistent styling
- The sidebar and navbar are conditionally shown (hidden on index, login, and register pages)
- For UI changes, edit the relevant template and reload the page in your browser
- For more information, see the main `README.md` in the project root
