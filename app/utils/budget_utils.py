# Utility functions for budget operations
from flask import current_app
import uuid

def get_user_budget(user_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM budgets WHERE user_id = %s', (user_id,))
            budget = cursor.fetchone()
        return budget
    finally:
        conn.close()

def save_or_update_budget(user_id, name, currency, income_source, amount):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM budgets WHERE user_id = %s', (user_id,))
            budget = cursor.fetchone()
            
            if budget:
                cursor.execute('UPDATE budgets SET name=%s, currency=%s, income_source=%s, amount=%s WHERE id=%s',
                             (name, currency, income_source, amount, budget['id']))
            else:
                cursor.execute('INSERT INTO budgets (id, user_id, name, currency, income_source, amount) VALUES (%s, %s, %s, %s, %s, %s)',
                             (str(uuid.uuid4()), user_id, name, currency, income_source, amount))
            
            conn.commit()
            cursor.execute('SELECT * FROM budgets WHERE user_id = %s', (user_id,))
            budget = cursor.fetchone()
        return budget
    finally:
        conn.close()

def insert_full_budget(user_id, budget_name, currency, income, expenses):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            budget_id = str(uuid.uuid4())
            total_income = sum(float(i.get('amount', 0)) for i in income)
            cursor.execute('INSERT INTO budgets (id, user_id, name, currency, income_source, amount) VALUES (%s, %s, %s, %s, %s, %s)',
                         (budget_id, user_id, budget_name, currency, ', '.join(i.get('source', '') for i in income), total_income))
            
            for cat in expenses:
                cat_id = str(uuid.uuid4())
                cat_name = cat.get('category', 'Other')
                cat_amount = sum(float(item.get('amount', 0)) for item in cat.get('items', []))
                cursor.execute('INSERT INTO budget_expense_categories (id, budget_id, category_name, amount) VALUES (%s, %s, %s, %s)',
                             (cat_id, budget_id, cat_name, cat_amount))
                
                for item in cat.get('items', []):
                    item_id = str(uuid.uuid4())
                    item_name = item.get('name', '')
                    item_amount = float(item.get('amount', 0))
                    cursor.execute('INSERT INTO budget_expense_items (id, category_id, name, amount) VALUES (%s, %s, %s, %s)',
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
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id, name, currency, income_source, amount FROM budgets WHERE user_id = %s ORDER BY name', 
                         (user_id,))
            budgets = cursor.fetchall()
        return budgets
    finally:
        conn.close()

def get_budget_by_id(budget_id, user_id):
    """Get a specific budget by ID, ensuring it belongs to the specified user"""
    conn = current_app.get_db_connection()
    
    try:
        with conn.cursor() as cursor:
            # First, verify that the budget belongs to the user
            cursor.execute('SELECT * FROM budgets WHERE id = %s AND user_id = %s', 
                         (budget_id, user_id))
            budget = cursor.fetchone()
            
            if not budget:
                return None
            
            # Get the complete budget with categories and items
            cursor.execute('''
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
                    b.id = %s AND b.user_id = %s
            ''', (budget_id, user_id))
            budget_details = cursor.fetchall()
    finally:
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
                'name': row['category_name'],  # This is the category name from the database
                'items': []
            }
        
        if row['item_id'] is not None:
            result['categories'][category_id]['items'].append({
                'id': row['item_id'],
                'name': row['item_name'],  # This is the item name from the database
                'amount': row['item_amount']
            })
    
    return result
