import sqlite3
from flask import current_app

# Authentication and access control utilities will go here

def get_user_by_login_id(login_id):
    """Get user by user_id, email, or phone (case-insensitive)."""
    conn = current_app.get_db_connection()
    user = conn.execute('''
        SELECT u.* FROM users u
        LEFT JOIN contact_info c ON u.id = c.user_id
        WHERE (LOWER(u.id) = ? OR LOWER(c.email) = ? OR c.phone = ?)''',
        (login_id.lower(), login_id.lower(), login_id)).fetchone()
    conn.close()
    return user

def check_password(user_id, password):
    """Check if the password matches for the given user_id."""
    conn = current_app.get_db_connection()
    pw_row = conn.execute('SELECT password FROM user_passwords WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return pw_row and pw_row[0] == password
