import pymysql
from flask import current_app, session, redirect, url_for, request, jsonify
from functools import wraps
from .password_utils import verify_password, is_password_hashed


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Login required'}), 401
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function


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
        
        if not pw_row:
            return False
        
        stored_password = pw_row['password']
        
        # Check if the stored password is hashed
        if is_password_hashed(stored_password):
            # Use bcrypt verification for hashed passwords
            return verify_password(password, stored_password)
        else:
            # Fallback to plain text comparison for backwards compatibility
            # This allows existing plain text passwords to still work during transition
            return stored_password == password
    finally:
        conn.close()
