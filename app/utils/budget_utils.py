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
    """Get budget by ID with enhanced analysis"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get budget data
            cursor.execute('''
                SELECT id, user_id, name, currency, income_source, amount, start_date, end_date
                FROM budgets
                WHERE id = %s AND user_id = %s
            ''', (budget_id, user_id))
            budget = cursor.fetchone()
            
            if not budget:
                return None
            
            # Calculate actual spent and remaining budget
            cursor.execute('''
                SELECT COALESCE(SUM(i.amount), 0) as total_budget_items
                FROM budget_expense_categories c
                JOIN budget_expense_items i ON c.id = i.category_id
                WHERE c.budget_id = %s
            ''', (budget_id,))
            budget_items_result = cursor.fetchone()
            total_budget_items = budget_items_result['total_budget_items'] if budget_items_result else 0
            
            # Calculate actual spent from transactions (you may need to implement this based on your transaction tracking)
            actual_spent = 0  # Placeholder - implement based on your transaction tracking logic
            remaining_budget = float(budget['amount']) - actual_spent  # budget['amount'] - actual_spent
            
            budget_status = 'WITHIN_BUDGET' if remaining_budget >= 0 else 'OVER_BUDGET'
            
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
                'actual_spent': actual_spent,
                'remaining_budget': remaining_budget,
                'budget_status': budget_status,
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
                    # Only append item if item_id is not None
                    if row['item_id'] is not None:
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
def get_all_user_budgets_with_categories(user_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get all budgets for the user
            cursor.execute("SELECT id, name, amount, currency FROM budgets WHERE user_id = %s", (user_id,))
            budgets = cursor.fetchall()
            result = []
            for b in budgets:
                budget_id = b['id']
                # Get all categories and their amounts for this budget
                cursor.execute(
                    "SELECT category_name, amount FROM budget_expense_categories WHERE budget_id = %s",
                    (budget_id,)
                )
                categories = {row['category_name']: float(row['amount']) for row in cursor.fetchall()}
                result.append({
                    'id': budget_id,
                    'name': b['name'],
                    'amount': float(b['amount']) if b['amount'] else 0,
                    'currency': b['currency'],
                    'categories': categories
                })
            return result
    except Exception as e:
        print(f"Error getting user budgets with categories: {e}")
        return []
    finally:
        conn.close()      

def delete_budget(budget_id, user_id, deletion_reason="User initiated deletion"):
    """Delete a budget and all its associated data"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # First verify the budget belongs to the user
            cursor.execute('SELECT id, name FROM budgets WHERE id = %s AND user_id = %s', (budget_id, user_id))
            budget = cursor.fetchone()
            
            if not budget:
                return False, "Budget not found or you don't have permission to delete it"
            
            budget_name = budget['name']
            
            # Update the deletion reason in the trigger by setting a session variable
            cursor.execute('SET @deletion_reason = %s', (deletion_reason,))
            
            # Delete the budget (CASCADE will handle related records and trigger will log)
            cursor.execute('DELETE FROM budgets WHERE id = %s AND user_id = %s', (budget_id, user_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, f"Budget '{budget_name}' deleted successfully"
            else:
                return False, "Failed to delete budget"
                
    except Exception as e:
        print(f"Error deleting budget: {e}")
        conn.rollback()
        return False, f"Error deleting budget: {str(e)}"
    finally:
        conn.close()

def get_budget_deletion_history(user_id, limit=10):
    """Get the deletion history for a user's budgets"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    deleted_budget_name,
                    budget_amount,
                    currency,
                    deletion_timestamp,
                    categories_count,
                    items_count,
                    deletion_reason
                FROM budget_deletion_log 
                WHERE deleted_by_user_id = %s 
                ORDER BY deletion_timestamp DESC 
                LIMIT %s
            ''', (user_id, limit))
            return cursor.fetchall()
    except Exception as e:
        print(f"Error getting deletion history: {e}")
        return []
    finally:
        conn.close()

def restore_budget_from_log(deletion_log_id, user_id):
    """Attempt to restore a budget from deletion log (if data is available)"""
    # This is a placeholder function - actual implementation would depend on
    # how much data you want to store in the deletion log
    # For now, it just returns information about what was deleted
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT * FROM budget_deletion_log 
                WHERE id = %s AND deleted_by_user_id = %s
            ''', (deletion_log_id, user_id))
            log_entry = cursor.fetchone()
            
            if log_entry:
                return {
                    'status': 'info_available',
                    'message': 'Budget information found in deletion log',
                    'data': dict(log_entry)
                }
            else:
                return {
                    'status': 'not_found',
                    'message': 'No deletion record found'
                }
    except Exception as e:
        print(f"Error checking deletion log: {e}")
        return {
            'status': 'error',
            'message': f"Error accessing deletion log: {str(e)}"
        }
    finally:
        conn.close()
