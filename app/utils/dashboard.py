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
    except Exception as e:
        print(f"Error getting budgets: {e}")
        # Fallback to original query
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM budgets WHERE user_id = %s', (user_id,))
                budgets = cursor.fetchall()
            return budgets
        except Exception as fallback_error:
            print(f"Fallback query also failed: {fallback_error}")
            return []
    finally:
        conn.close()

def get_recent_expenses(user_id, limit=5):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT t.amount, t.timestamp, t.note, t.location FROM transactions t
                WHERE t.sender_id = %s AND t.type = 'expense'
                ORDER BY t.timestamp DESC LIMIT %s
            ''', (user_id, limit))
            expenses = cursor.fetchall()
        return expenses
    finally:
        conn.close()

def get_recent_transactions(user_id, limit=5):
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
            
            # Debug: Check timestamp data types
            for tx in txs:
                if 'timestamp' in tx:
                    print(f"DEBUG dashboard.py: Transaction timestamp type: {type(tx['timestamp'])}, value: {tx['timestamp']}")
            
        return txs
    finally:
        conn.close()
