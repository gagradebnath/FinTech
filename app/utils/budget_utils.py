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
    """Save or update budget using stored procedure"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc('SaveOrUpdateBudget', [
                user_id, name, currency, income_source, amount,
                None, None, None  # OUT parameters
            ])
            
            # Fetch the OUT parameters
            cursor.execute("SELECT @_SaveOrUpdateBudget_5 as budget_id, @_SaveOrUpdateBudget_6 as success, @_SaveOrUpdateBudget_7 as message")
            result = cursor.fetchone()
            
            if result and result['success']:
                # Get the updated budget
                cursor.execute('SELECT * FROM budgets WHERE id = %s', (result['budget_id'],))
                budget = cursor.fetchone()
                return budget
            else:
                print(f"Budget save failed: {result['message'] if result else 'Unknown error'}")
                return None
                
    except Exception as e:
        print(f"Exception in save_or_update_budget: {e}")
        return None
    finally:
        conn.close()

def insert_full_budget(user_id, budget_name, currency, income, expenses):
    """Insert full budget using stored procedure"""
    conn = current_app.get_db_connection()
    try:
        # Prepare income sources
        income_sources = ', '.join(i.get('source', '') for i in income)
        total_income = sum(float(i.get('amount', 0)) for i in income)
        
        # For now, we'll use a simplified approach
        # In production, you'd want to enhance the procedure to handle complex expenses
        expenses_json = str(expenses)  # Simplified JSON representation
        
        with conn.cursor() as cursor:
            cursor.callproc('CreateFullBudget', [
                user_id, budget_name, currency, income_sources, 
                total_income, expenses_json, None, None, None  # OUT parameters
            ])
            
            cursor.execute("SELECT @_CreateFullBudget_6 as budget_id, @_CreateFullBudget_7 as success, @_CreateFullBudget_8 as message")
            result = cursor.fetchone()
            
            if result and result['success']:
                # Now handle the categories and items manually for this version
                budget_id = result['budget_id']
                
                # Process expense categories and items
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
            else:
                return False, result['message'] if result else 'Unknown error'
                
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
    """Get budget by ID with enhanced analysis using optimized view"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Use the optimized view for budget analysis
            cursor.execute('''
                SELECT b.*, ba.actual_spent, ba.remaining_budget, ba.budget_status
                FROM budgets b
                LEFT JOIN v_budget_analysis ba ON b.id = ba.id
                WHERE b.id = %s AND b.user_id = %s
            ''', (budget_id, user_id))
            budget = cursor.fetchone()
            
            if not budget:
                return None
            
            # Get categories and items
            cursor.execute('''
                SELECT
                    c.id as category_id,
                    c.category_name as category_name,
                    i.id as item_id,
                    i.name as item_name,
                    i.amount as item_amount
                FROM
                    budget_expense_categories c
                LEFT JOIN budget_expense_items i ON c.id = i.category_id
                WHERE
                    c.budget_id = %s
            ''', (budget_id,))
            budget_details = cursor.fetchall()
            
            # Structure the response
            result = {
                'id': budget['id'],
                'user_id': budget['user_id'],
                'name': budget['name'],
                'currency': budget['currency'],
                'income_source': budget['income_source'],
                'amount': budget['amount'],
                'actual_spent': budget.get('actual_spent', 0),
                'remaining_budget': budget.get('remaining_budget', 0),
                'budget_status': budget.get('budget_status', 'UNKNOWN'),
                'categories': {}
            }
            
            # Process categories and items
            for row in budget_details:
                if row['category_id']:
                    category_id = row['category_id']
                    if category_id not in result['categories']:
                        result['categories'][category_id] = {
                            'id': category_id,
                            'name': row['category_name'],
                            'items': []
                        }
                    
                    if row['item_id']:
                        result['categories'][category_id]['items'].append({
                            'id': row['item_id'],
                            'name': row['item_name'],
                            'amount': row['item_amount']
                        })
            
            return result
            
    except Exception as e:
        print(f"Error getting budget: {e}")
        return None
    finally:
        conn.close()
