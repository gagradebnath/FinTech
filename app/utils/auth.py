import pymysql
from flask import current_app

def get_user_by_login_id(login_id):
    """Get user by user_id, email, or phone (case-insensitive)."""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT u.* FROM users u
                LEFT JOIN contact_info c ON u.id = c.user_id
                WHERE (LOWER(u.id) = %s OR LOWER(c.email) = %s OR c.phone = %s)''',
                (login_id.lower(), login_id.lower(), login_id))
            user = cursor.fetchone()
        return user
    finally:
        conn.close()

def check_password(user_id, password):
    """Check if the password matches for the given user_id."""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT password FROM user_passwords WHERE user_id = %s', (user_id,))
            pw_row = cursor.fetchone()
        return pw_row and pw_row['password'] == password
    finally:
        conn.close()
