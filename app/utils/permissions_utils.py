# Utility functions for permissions and role-permissions management
from flask import current_app
import uuid

def get_all_roles():
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM roles')
            roles = cursor.fetchall()
        return roles
    finally:
        conn.close()

def get_all_permissions():
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM permissions')
            permissions = cursor.fetchall()
        return permissions
    finally:
        conn.close()

def get_permissions_for_role(role_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''SELECT p.* FROM permissions p
                JOIN role_permissions rp ON p.id = rp.permission_id
                WHERE rp.role_id = %s''', (role_id,))
            perms = cursor.fetchall()
        return perms
    finally:
        conn.close()

def add_permission_to_role(role_id, permission_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO role_permissions (id, role_id, permission_id) VALUES (%s, %s, %s)',
                         (str(uuid.uuid4()), role_id, permission_id))
        conn.commit()
    finally:
        conn.close()

def remove_permission_from_role(role_id, permission_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM role_permissions WHERE role_id = %s AND permission_id = %s',
                         (role_id, permission_id))
        conn.commit()
    finally:
        conn.close()

def has_permission(user_id, permission_name):
    if not permission_name.startswith('perm_'):
        permission_name = 'perm_' + permission_name
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''SELECT 1 FROM users u
                JOIN roles r ON u.role_id = r.id
                JOIN role_permissions rp ON r.id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE u.id = %s AND p.name = %s''', (user_id, permission_name))
            row = cursor.fetchone()
        return bool(row)
    finally:
        conn.close()
