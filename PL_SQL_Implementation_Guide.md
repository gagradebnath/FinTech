# FinGuard PL/SQL Implementation Guide

## Updated Python Code Examples

This guide shows exactly how to update your Python utility functions to use the new PL/SQL procedures and functions.

## 1. Transaction Utils - Updated Implementation

### Updated `transaction_utils.py`

```python
# Utility functions for transaction operations
from flask import current_app
import uuid

def get_user_by_id(user_id):
    """Get user by ID - can be optimized with a stored procedure later"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
        return user
    finally:
        conn.close()

def send_money(sender_id, recipient_id, amount, payment_method, note, location, tx_type):
    """
    Send money between users using optimized stored procedure
    """
    print(f"send_money called: sender_id={sender_id}, recipient_id={recipient_id}, amount={amount}")
    
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Use the enhanced stored procedure
            cursor.callproc('ProcessMoneyTransferEnhanced', [
                sender_id, recipient_id, float(amount), payment_method, 
                note, tx_type, location, None, None, None
            ])
            
            # Fetch the OUT parameters
            cursor.execute("SELECT @_ProcessMoneyTransferEnhanced_7 as success, @_ProcessMoneyTransferEnhanced_8 as message, @_ProcessMoneyTransferEnhanced_9 as transaction_id")
            result = cursor.fetchone()
            
            if result:
                success = bool(result['success'])
                message = result['message']
                transaction_id = result['transaction_id']
                
                # Get updated sender info if successful
                if success:
                    sender = get_user_by_id(sender_id)
                    print(f"Transaction successful: {message}")
                    return True, message, sender
                else:
                    print(f"Transaction failed: {message}")
                    sender = get_user_by_id(sender_id)
                    return False, message, sender
            else:
                return False, 'Failed to get procedure result', None
                
    except Exception as e:
        print(f"Exception in send_money: {e}")
        return False, f'Failed to send money: {str(e)}', None
    finally:
        conn.close()

def lookup_user_by_identifier(identifier):
    """Lookup user by identifier - can be optimized with a function"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT u.id FROM users u
                LEFT JOIN contact_info c ON u.id = c.user_id
                WHERE LOWER(u.id) = %s OR LOWER(c.email) = %s OR c.phone = %s
            ''', (identifier.lower(), identifier.lower(), identifier))
            user = cursor.fetchone()
        return user
    finally:
        conn.close()

def is_user_flagged_fraud(user_id):
    """Check if user is flagged for fraud"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1 FROM fraud_list WHERE reported_user_id = %s', (user_id,))
            fraud = cursor.fetchone()
        return bool(fraud)
    finally:
        conn.close()

def get_user_risk_score(user_id):
    """Get user risk score using MySQL function"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT GetUserRiskScore(%s) as risk_score", (user_id,))
            result = cursor.fetchone()
            return float(result['risk_score']) if result and result['risk_score'] else 0.0
    except Exception as e:
        print(f"Error getting risk score: {e}")
        return 0.0
    finally:
        conn.close()

def agent_add_money(agent_id, user_id, amount):
    """Agent add money using stored procedure"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Use the enhanced transfer procedure with admin privileges
            cursor.callproc('ProcessMoneyTransferEnhanced', [
                agent_id, user_id, float(amount), 'agent_add', 
                f'Agent {agent_id} added money', 'Deposit', 'Agent Office', 
                None, None, None
            ])
            
            cursor.execute("SELECT @_ProcessMoneyTransferEnhanced_7 as success, @_ProcessMoneyTransferEnhanced_8 as message")
            result = cursor.fetchone()
            
            if result and result['success']:
                return (result['message'], None)
            else:
                return (None, result['message'] if result else 'Unknown error')
                
    except Exception as e:
        return (None, f"Failed to add money: {str(e)}")
    finally:
        conn.close()

def agent_cash_out(agent_id, user_id, amount):
    """Agent cash out using stored procedure"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Use the enhanced transfer procedure
            cursor.callproc('ProcessMoneyTransferEnhanced', [
                user_id, agent_id, float(amount), 'agent_cashout', 
                f'Agent {agent_id} cashed out', 'Withdrawal', 'Agent Office', 
                None, None, None
            ])
            
            cursor.execute("SELECT @_ProcessMoneyTransferEnhanced_7 as success, @_ProcessMoneyTransferEnhanced_8 as message")
            result = cursor.fetchone()
            
            if result and result['success']:
                return (result['message'], None)
            else:
                return (None, result['message'] if result else 'Unknown error')
                
    except Exception as e:
        return (None, f"Failed to cash out: {str(e)}")
    finally:
        conn.close()
```

## 2. Budget Utils - Updated Implementation

### Updated `budget_utils.py`

```python
# Utility functions for budget operations
from flask import current_app
import uuid

def get_user_budget(user_id):
    """Get user budget - kept simple for now"""
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
                return True, None
            else:
                return False, result['message'] if result else 'Unknown error'
                
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_all_user_budgets(user_id):
    """Get all budgets for a user"""
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
    """Get budget by ID with categories and items"""
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
```

## 3. User Registration - Updated Implementation

### Updated `register.py`

```python
import pymysql
import uuid
from datetime import date
from flask import current_app
from .password_utils import hash_password

def is_email_unique(email):
    """Check if email is unique - can be optimized with a function"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1 FROM contact_info WHERE LOWER(email) = %s', (email.lower(),))
            exists = cursor.fetchone()
        return not exists
    finally:
        conn.close()

def is_phone_unique(phone):
    """Check if phone is unique - can be optimized with a function"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1 FROM contact_info WHERE phone = %s', (phone,))
            exists = cursor.fetchone()
        return not exists
    finally:
        conn.close()

def get_role_id(role):
    """Get role ID by name"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id FROM roles WHERE LOWER(name) = %s', (role.lower(),))
            row = cursor.fetchone()
        return row['id'] if row else None
    finally:
        conn.close()

def create_user_and_contact(role_id, first_name, last_name, dob, age, gender, marital_status, blood_group, email, phone, password):
    """Create user and contact using stored procedure"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get role name from role_id
            cursor.execute('SELECT name FROM roles WHERE id = %s', (role_id,))
            role_row = cursor.fetchone()
            
            if not role_row:
                return None, 'Invalid role ID'
                
            role_name = role_row['name']
            
            # Hash the password
            hashed_password = hash_password(password)
            
            # Call the stored procedure
            cursor.callproc('RegisterUser', [
                role_name, first_name, last_name, dob, age, gender, 
                marital_status, blood_group, email, phone, hashed_password,
                None, None, None  # OUT parameters
            ])
            
            # Fetch the OUT parameters
            cursor.execute("SELECT @_RegisterUser_11 as user_id, @_RegisterUser_12 as success, @_RegisterUser_13 as message")
            result = cursor.fetchone()
            
            if result and result['success']:
                return result['user_id'], None
            else:
                return None, result['message'] if result else 'Registration failed'
                
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()
```

## 4. Fraud Utils - Updated Implementation

### Updated `fraud_utils.py`

```python
# Utility functions for fraud operations
from flask import current_app
import uuid

def lookup_user_by_identifier(identifier):
    """Lookup user by identifier"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT u.id FROM users u
                LEFT JOIN contact_info c ON u.id = c.user_id
                WHERE LOWER(u.id) = %s OR LOWER(c.email) = %s OR c.phone = %s
            ''', (identifier.lower(), identifier.lower(), identifier))
            user = cursor.fetchone()
        return user
    finally:
        conn.close()

def add_fraud_report(reporter_id, reported_user_id, reason):
    """Add fraud report using stored procedure"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc('ProcessFraudReport', [
                reporter_id, reported_user_id, reason, None, None  # OUT parameters
            ])
            
            # Fetch the OUT parameters
            cursor.execute("SELECT @_ProcessFraudReport_3 as success, @_ProcessFraudReport_4 as message")
            result = cursor.fetchone()
            
            if result and result['success']:
                return True, None
            else:
                return False, result['message'] if result else 'Unknown error'
                
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
```

## 5. Admin Utils - Updated Implementation

### Updated `admin_utils.py`

```python
# Utility functions for admin operations
from flask import current_app
import uuid
from datetime import datetime

def get_role_name_by_id(role_id):
    """Get role name by ID"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT name FROM roles WHERE id = %s', (role_id,))
            row = cursor.fetchone()
        return row['name'] if row else None
    finally:
        conn.close()

def get_agents():
    """Get all agents using optimized view"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT u.id, u.first_name, u.last_name, u.balance 
                FROM v_user_dashboard_summary u
                JOIN roles r ON u.role_id = r.id 
                WHERE LOWER(r.name) = "agent"
            ''')
            agents = cursor.fetchall()
        return agents
    finally:
        conn.close()

def get_all_users():
    """Get all users using optimized view"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id, first_name, last_name, balance FROM v_user_dashboard_summary')
            users = cursor.fetchall()
        return users
    finally:
        conn.close()

def get_all_transactions(limit=100):
    """Get all transactions with user details"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT t.*, s.first_name as sender_first, s.last_name as sender_last, 
                       r.first_name as receiver_first, r.last_name as receiver_last 
                FROM transactions t
                LEFT JOIN users s ON t.sender_id = s.id
                LEFT JOIN users r ON t.receiver_id = r.id
                ORDER BY t.timestamp DESC LIMIT %s
            ''', (limit,))
            txs = cursor.fetchall()
        return txs
    finally:
        conn.close()

def get_all_frauds(limit=100):
    """Get all fraud reports"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT f.*, u1.first_name as reporter_first, u1.last_name as reporter_last, 
                       u2.first_name as reported_first, u2.last_name as reported_last 
                FROM fraud_list f
                LEFT JOIN users u1 ON f.user_id = u1.id
                LEFT JOIN users u2 ON f.reported_user_id = u2.id
                ORDER BY f.created_at DESC LIMIT %s
            ''', (limit,))
            frauds = cursor.fetchall()
        return frauds
    finally:
        conn.close()

def get_admin_logs(limit=100):
    """Get admin logs"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT l.*, a.first_name as admin_first, a.last_name as admin_last 
                FROM admin_logs l 
                LEFT JOIN users a ON l.admin_id = a.id 
                ORDER BY l.timestamp DESC LIMIT %s
            ''', (limit,))
            logs = cursor.fetchall()
        return logs
    finally:
        conn.close()

def update_user_balance(user_id, amount):
    """Update single user balance"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE users SET balance = balance + %s WHERE id = %s', (amount, user_id))
        conn.commit()
    finally:
        conn.close()

def batch_update_user_balances(admin_id, user_ids, amounts, reason):
    """Batch update user balances using stored procedure"""
    conn = current_app.get_db_connection()
    try:
        # Convert lists to comma-separated strings
        user_ids_str = ','.join(user_ids)
        amounts_str = ','.join(str(amount) for amount in amounts)
        
        with conn.cursor() as cursor:
            cursor.callproc('AdminBatchBalanceUpdate', [
                admin_id, user_ids_str, amounts_str, reason,
                None, None, None  # OUT parameters
            ])
            
            # Fetch the OUT parameters
            cursor.execute("SELECT @_AdminBatchBalanceUpdate_4 as success, @_AdminBatchBalanceUpdate_5 as message, @_AdminBatchBalanceUpdate_6 as updated_count")
            result = cursor.fetchone()
            
            if result and result['success']:
                return True, result['message'], result['updated_count']
            else:
                return False, result['message'] if result else 'Unknown error', 0
                
    except Exception as e:
        return False, str(e), 0
    finally:
        conn.close()

def insert_transaction_admin(tx_id, amount, sender_id, receiver_id, note, tx_type):
    """Insert admin transaction"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) 
                VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, %s)
            ''', (tx_id, amount, 'admin_add', sender_id, receiver_id, note, tx_type, 'Admin Panel'))
        conn.commit()
    finally:
        conn.close()

def insert_admin_log(log_id, admin_id, ip_address, details):
    """Insert admin log"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details) 
                VALUES (%s, %s, %s, %s, %s)
            ''', (log_id, admin_id, ip_address, datetime.now(), details))
        conn.commit()
    finally:
        conn.close()
```

## 6. Dashboard Utils - Updated Implementation

### Updated `dashboard.py`

```python
from flask import current_app

def get_user_dashboard_data(user_id):
    """Get complete dashboard data using stored procedure"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc('GetUserDashboardData', [
                user_id, None, None, None, None, None  # OUT parameters
            ])
            
            # Fetch the OUT parameters
            cursor.execute("""
                SELECT @_GetUserDashboardData_1 as current_balance,
                       @_GetUserDashboardData_2 as total_sent,
                       @_GetUserDashboardData_3 as total_received,
                       @_GetUserDashboardData_4 as transaction_count,
                       @_GetUserDashboardData_5 as risk_score
            """)
            result = cursor.fetchone()
            
            if result:
                return {
                    'current_balance': float(result['current_balance'] or 0),
                    'total_sent': float(result['total_sent'] or 0),
                    'total_received': float(result['total_received'] or 0),
                    'transaction_count': int(result['transaction_count'] or 0),
                    'risk_score': float(result['risk_score'] or 0)
                }
            else:
                return {
                    'current_balance': 0.0,
                    'total_sent': 0.0,
                    'total_received': 0.0,
                    'transaction_count': 0,
                    'risk_score': 0.0
                }
    except Exception as e:
        print(f"Error getting dashboard data: {e}")
        return {
            'current_balance': 0.0,
            'total_sent': 0.0,
            'total_received': 0.0,
            'transaction_count': 0,
            'risk_score': 0.0
        }
    finally:
        conn.close()

def get_user_budgets(user_id):
    """Get user budgets using optimized view"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM v_budget_analysis WHERE user_id = %s', (user_id,))
            budgets = cursor.fetchall()
        return budgets
    finally:
        conn.close()

def get_recent_expenses(user_id, limit=5):
    """Get recent expenses"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT t.amount, t.timestamp, t.note, t.location 
                FROM transactions t
                WHERE t.sender_id = %s AND t.type IN ('Transfer', 'Payment', 'Withdrawal')
                ORDER BY t.timestamp DESC LIMIT %s
            ''', (user_id, limit))
            expenses = cursor.fetchall()
        return expenses
    finally:
        conn.close()

def get_recent_transactions(user_id, limit=5):
    """Get recent transactions"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT t.amount, t.timestamp, t.note, t.location, t.type, t.receiver_id, t.sender_id, t.payment_method
                FROM transactions t
                WHERE t.sender_id = %s OR t.receiver_id = %s
                ORDER BY t.timestamp DESC LIMIT %s
            ''', (user_id, user_id, limit))
            txs = cursor.fetchall()
        return txs
    finally:
        conn.close()
```

## Implementation Steps

1. **Deploy the PL/SQL file first:**
   ```sql
   SOURCE b:\L2T1\Project\FinGuard\PL_SQL_Optimizations.sql;
   ```

2. **Update Python files gradually:**
   - Start with `transaction_utils.py`
   - Test thoroughly
   - Move to `register.py`
   - Continue with other files

3. **Test each component:**
   - Unit tests for each function
   - Integration tests for complete workflows
   - Performance benchmarks

4. **Monitor and optimize:**
   - Check procedure execution times
   - Monitor database performance
   - Adjust as needed

This implementation provides significant performance improvements while maintaining all existing functionality.
