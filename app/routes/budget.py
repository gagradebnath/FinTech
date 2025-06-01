from flask import Blueprint, render_template, request, current_app, jsonify, session, redirect, url_for
import uuid
from .user import get_current_user

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budget', methods=['GET'])
def get_budget():
    return {'message': 'Budget endpoint'}

@budget_bp.route('/plan-budget', methods=['GET', 'POST'])
def plan_budget():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    conn = current_app.get_db_connection()
    budget = conn.execute('SELECT * FROM budgets WHERE user_id = ?', (user['id'],)).fetchone()
    error = None
    success = None
    if request.method == 'POST':
        name = request.form.get('name')
        currency = request.form.get('currency')
        income_source = request.form.get('income_source')
        amount = request.form.get('amount')
        try:
            if budget:
                conn.execute('UPDATE budgets SET name=?, currency=?, income_source=?, amount=? WHERE id=?',
                             (name, currency, income_source, amount, budget['id']))
            else:
                conn.execute('INSERT INTO budgets (id, user_id, name, currency, income_source, amount) VALUES (?, ?, ?, ?, ?, ?)',
                             (str(uuid.uuid4()), user['id'], name, currency, income_source, amount))
            conn.commit()
            success = 'Budget saved successfully.'
            budget = conn.execute('SELECT * FROM budgets WHERE user_id = ?', (user['id'],)).fetchone()
        except Exception as e:
            conn.rollback()
            error = 'Failed to save budget: ' + str(e)
    conn.close()
    return render_template('plan_budget.html', budget=budget, error=error, success=success)

@budget_bp.route('/save_budget', methods=['POST'])
def save_budget():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    user_id = session['user_id']
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    budget_name = data.get('budgetName')
    currency = data.get('currency')
    income = data.get('income', [])
    expenses = data.get('expenses', [])
    if not budget_name or not currency or not income or not expenses:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    conn = current_app.get_db_connection()
    try:
        # Insert budget
        budget_id = str(uuid.uuid4())
        total_income = sum(float(i.get('amount', 0)) for i in income)
        conn.execute('INSERT INTO budgets (id, user_id, name, currency, income_source, amount) VALUES (?, ?, ?, ?, ?, ?)',
                     (budget_id, user_id, budget_name, currency, ', '.join(i.get('source', '') for i in income), total_income))
        # Insert expense categories and items
        for cat in expenses:
            cat_id = str(uuid.uuid4())
            cat_name = cat.get('category', 'Other')
            cat_amount = sum(float(item.get('amount', 0)) for item in cat.get('items', []))
            conn.execute('INSERT INTO budget_expense_categories (id, budget_id, category_name, amount) VALUES (?, ?, ?, ?)',
                         (cat_id, budget_id, cat_name, cat_amount))
            for item in cat.get('items', []):
                item_id = str(uuid.uuid4())
                item_name = item.get('name', '')
                item_amount = float(item.get('amount', 0))
                conn.execute('INSERT INTO budget_expense_items (id, category_id, name, amount) VALUES (?, ?, ?, ?)',
                             (item_id, cat_id, item_name, item_amount))
        conn.commit()
        return jsonify({'success': True, 'message': 'Budget saved', 'budget': data})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()
