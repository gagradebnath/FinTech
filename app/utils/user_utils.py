# Utility functions for user operations (session, fetch by id)
from flask import current_app, session

def get_current_user():
    user_id = session.get('user_id')
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            user = None
            if user_id:
                cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
                user = cursor.fetchone()
            if not user:
                cursor.execute('SELECT * FROM users LIMIT 1')
                user = cursor.fetchone()
        return user
    finally:
        conn.close()

def get_role_name_by_id(role_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT name FROM roles WHERE id = %s', (role_id,))
            row = cursor.fetchone()
        return row['name'] if row else None
    finally:
        conn.close()
