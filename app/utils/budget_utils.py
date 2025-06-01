# Utility functions for budget operations
from flask import current_app
import uuid

def get_user_budget(user_id):
    conn = current_app.get_db_connection()
    budget = conn.execute('SELECT * FROM budgets WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return budget

def save_or_update_budget(user_id, name, currency, income_source, amount):
    conn = current_app.get_db_connection()
    budget = conn.execute('SELECT * FROM budgets WHERE user_id = ?', (user_id,)).fetchone()
    if budget:
        conn.execute('UPDATE budgets SET name=?, currency=?, income_source=?, amount=? WHERE id=?',
                     (name, currency, income_source, amount, budget['id']))
    else:
        conn.execute('INSERT INTO budgets (id, user_id, name, currency, income_source, amount) VALUES (?, ?, ?, ?, ?, ?)',
                     (str(uuid.uuid4()), user_id, name, currency, income_source, amount))
    conn.commit()
    budget = conn.execute('SELECT * FROM budgets WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return budget

def insert_full_budget(user_id, budget_name, currency, income, expenses):
    conn = current_app.get_db_connection()
    try:
        budget_id = str(uuid.uuid4())
        total_income = sum(float(i.get('amount', 0)) for i in income)
        conn.execute('INSERT INTO budgets (id, user_id, name, currency, income_source, amount) VALUES (?, ?, ?, ?, ?, ?)',
                     (budget_id, user_id, budget_name, currency, ', '.join(i.get('source', '') for i in income), total_income))
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
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()
