# FinGuard Static Assets

This folder contains all static files for the FinGuard web application. These files are served directly to the browser and are not processed by Flask.

## Structure

- `css/`: Stylesheets for the app's appearance
  - `style.css`: Main stylesheet with dark theme and common elements
  - `landing.css`: Landing page styles
  - `login.css`: Login page styles
  - `dashboard.css`: Dashboard-specific styles
  - `budget.css`: Budget planning page styles
  - `transaction.css`: Transaction page styles
  - `fraud.css`: Fraud reporting styles
  - Other page-specific CSS files
  
- `js/`: JavaScript files for dynamic frontend behavior
  - `main.js`: Common JavaScript functionality
  - `budget.js`: Budget planning and management
  - `finance-bg.js`: Animated background effects
  - `landing.js`: Landing page scripts
  
- `assets/`: Images, icons, and other visual resources
  - Logo and branding elements
  - Background images

## Modern UI Features

The CSS implements a cohesive dark theme with:
- Animated gradient backgrounds
- Modern card designs with subtle shadows
- Consistent color scheme defined in CSS variables
- Responsive layouts for all device sizes
- Custom styled form elements and tables
- Transition and hover effects

### CSS Variables

The main stylesheet defines a set of custom properties (variables) that maintain a consistent look:

```css
:root {
    --primary-color: #0066ff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #17a2b8;
    
    /* Gradient colors from main content */
    --gradient-color-1: #121212;
    --gradient-color-2: #163e3e;
    --gradient-color-3: #0d1f12;
    --gradient-color-4: #15151f;
    --gradient-color-5: #340434dd;
    
    /* Base theme colors derived from gradient */
    --dark-color: var(--gradient-color-1);
    --dark-secondary: #121b1b;
    --dark-tertiary: #121b15;
    --dark-accent: #1e102c;
    
    --light-color: #f8f9fa;
    --text-primary: #ffffff;
    --text-secondary: #b0b0b0;
    --border-color: rgba(255, 255, 255, 0.05);
}
```

## How to Use

- Place any new CSS files in the `css/` subfolder
- Place any new JavaScript files in the `js/` subfolder
- Place images and other assets in the `assets/` subfolder
- Reference these files in your HTML templates using Flask's `url_for('static', filename='...')`

### Example: Linking Static Files in a Template

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
<script src="{{ url_for('static', filename='js/main.js') }}"></script>
```

## Best Practices

- Use page-specific CSS files to organize styles by feature
- Load only the necessary CSS/JS for each page
- Follow the established dark theme color scheme
- Use the predefined CSS variables for consistency
- Make sure all UI elements are responsive
- Add comments to explain complex JavaScript functionality

## Notes

- Do not put sensitive information in static files; they are publicly accessible
- For more information, see the main `README.md` in the project root
