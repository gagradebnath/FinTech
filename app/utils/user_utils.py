# Utility functions for user operations (session, fetch by id)
from flask import current_app, session, url_for
import pymysql

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

def get_dashboard_url_for_user(user):
    """Get the appropriate dashboard URL based on user role"""
    if not user or 'role_id' not in user:
        return url_for('user.dashboard')
    
    role_name = get_role_name_by_id(user['role_id'])
    if not role_name:
        return url_for('user.dashboard')
    
    role_name = role_name.lower()
    if role_name == 'agent':
        return url_for('agent.agent_dashboard')
    elif role_name == 'admin':
        return url_for('admin.admin_dashboard')
    else:
        return url_for('user.dashboard')
def get_all_users():
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT u.id, u.first_name, u.last_name, c.email, c.phone
                FROM users u
                LEFT JOIN contact_info c ON u.id = c.user_id
            ''')
            users = cursor.fetchall()
        return users
    finally:
        conn.close()
def get_all_admins():
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE role_id = (SELECT id FROM roles WHERE name = 'admin')"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()
def get_all_agents():
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE role_id = (SELECT id FROM roles WHERE name = 'agent')")
            return cursor.fetchall()
    finally:
        conn.close()
