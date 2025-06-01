# Utility functions for user operations (session, fetch by id)
from flask import current_app, session

def get_current_user():
    user_id = session.get('user_id')
    conn = current_app.get_db_connection()
    user = None
    if user_id:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        user = conn.execute('SELECT * FROM users LIMIT 1').fetchone()
    conn.close()
    return user

def get_role_name_by_id(role_id):
    conn = current_app.get_db_connection()
    row = conn.execute('SELECT name FROM roles WHERE id = ?', (role_id,)).fetchone()
    conn.close()
    return row['name'] if row else None
