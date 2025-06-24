# Utility functions for permissions and role-permissions management
from flask import current_app
import uuid

def get_all_roles():
    conn = current_app.get_db_connection()
    roles = conn.execute('SELECT * FROM roles').fetchall()
    conn.close()
    return roles

def get_all_permissions():
    conn = current_app.get_db_connection()
    permissions = conn.execute('SELECT * FROM permissions').fetchall()
    conn.close()
    return permissions

def get_permissions_for_role(role_id):
    conn = current_app.get_db_connection()
    perms = conn.execute('''SELECT p.* FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        WHERE rp.role_id = ?''', (role_id,)).fetchall()
    conn.close()
    return perms

def add_permission_to_role(role_id, permission_id):
    conn = current_app.get_db_connection()
    conn.execute('INSERT INTO role_permissions (id, role_id, permission_id) VALUES (?, ?, ?)',
                 (str(uuid.uuid4()), role_id, permission_id))
    conn.commit()
    conn.close()

def remove_permission_from_role(role_id, permission_id):
    conn = current_app.get_db_connection()
    conn.execute('DELETE FROM role_permissions WHERE role_id = ? AND permission_id = ?',
                 (role_id, permission_id))
    conn.commit()
    conn.close()

def has_permission(user_id, permission_name):
    if not permission_name.startswith('perm_'):
        permission_name = 'perm_' + permission_name
    conn = current_app.get_db_connection()
    row = conn.execute('''SELECT 1 FROM users u
        JOIN roles r ON u.role_id = r.id
        JOIN role_permissions rp ON r.id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE u.id = ? AND p.name = ?''', (user_id, permission_name)).fetchone()
    conn.close()
    return bool(row)
