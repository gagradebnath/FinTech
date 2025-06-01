# FinGuard Static Assets

This folder contains all static files for the FinGuard web application. These files are served directly to the browser and are not processed by Flask.

## Structure

- `css/`: Custom stylesheets (e.g., `style.css`) for the app's appearance.
- `js/`: JavaScript files for dynamic frontend behavior (e.g., `main.js`, `budget.js`).

## How to Use

- Place any new CSS files in the `css/` subfolder.
- Place any new JavaScript files in the `js/` subfolder.
- Reference these files in your HTML templates using Flask's `url_for('static', filename='...')`.

## Notes
- Do not put sensitive information in static files; they are publicly accessible.
- For images, fonts, or other assets, create additional subfolders as needed (e.g., `img/`, `fonts/`).

For more information, see the main `README.md` in the project root.
