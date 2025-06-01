# Utility functions for dashboard queries
from flask import current_app

def get_user_budgets(user_id):
    conn = current_app.get_db_connection()
    budgets = conn.execute('SELECT * FROM budgets WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return budgets

def get_recent_expenses(user_id, limit=5):
    conn = current_app.get_db_connection()
    expenses = conn.execute('''
        SELECT t.amount, t.timestamp, t.note, t.location FROM transactions t
        WHERE t.sender_id = ? AND t.type = 'expense'
        ORDER BY t.timestamp DESC LIMIT ?
    ''', (user_id, limit)).fetchall()
    conn.close()
    return expenses
