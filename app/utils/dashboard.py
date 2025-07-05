
from flask import current_app

def get_user_budgets(user_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM budgets WHERE user_id = %s', (user_id,))
            budgets = cursor.fetchall()
        return budgets
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
