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

def get_all_user_budgets(user_id):
    """Get all budgets for a given user"""
    conn = current_app.get_db_connection()
    budgets = conn.execute('SELECT id, name, currency, income_source, amount FROM budgets WHERE user_id = ? ORDER BY name', 
                         (user_id,)).fetchall()
    conn.close()
    return budgets

def get_budget_by_id(budget_id, user_id):
    """Get a specific budget by ID, ensuring it belongs to the specified user"""
    conn = current_app.get_db_connection()
    
    # First, verify that the budget belongs to the user
    budget = conn.execute('SELECT * FROM budgets WHERE id = ? AND user_id = ?', 
                         (budget_id, user_id)).fetchone()
    
    if not budget:
        conn.close()
        return None
    
    # Get the complete budget with categories and items
    budget_details = conn.execute('''
        SELECT
            b.id as budget_id,
            b.user_id as user_id,
            b.name as name,
            b.currency as currency,
            b.income_source as income_source,
            b.amount as amount,
            c.id as category_id,
            c.category_name as category_name,
            i.id as item_id,
            i.name as item_name,
            i.amount as item_amount
        FROM
            budgets b
        LEFT JOIN budget_expense_categories c ON b.id = c.budget_id
        LEFT JOIN budget_expense_items i ON c.id = i.category_id
        WHERE
            b.id = ? AND b.user_id = ?
    ''', (budget_id, user_id)).fetchall()
    
    conn.close()
    
    if not budget_details:
        return budget  # Return the basic budget if no details found
    
    # Organize the results into a structured budget object
    result = {
        'id': budget['id'],
        'user_id': budget['user_id'],
        'name': budget['name'],
        'currency': budget['currency'],
        'income_source': budget['income_source'],
        'amount': budget['amount'],
        'categories': {}
    }
    
    # Process the results to create a structured budget with categories and items
    for row in budget_details:
        if row['category_id'] is None:
            continue
            
        category_id = row['category_id']
        if category_id not in result['categories']:
            result['categories'][category_id] = {
                'id': category_id,
                'name': row['category_name'],
                'items': []
            }
        
        if row['item_id'] is not None:
            result['categories'][category_id]['items'].append({
                'id': row['item_id'],
                'name': row['item_name'],
                'amount': row['item_amount']
            })
    
    return result
