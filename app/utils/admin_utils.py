# Utility functions for admin operations (moved from admin.py)
from flask import current_app
import uuid
from datetime import datetime

def get_role_name_by_id(role_id):
    conn = current_app.get_db_connection()
    row = conn.execute('SELECT name FROM roles WHERE id = ?', (role_id,)).fetchone()
    conn.close()
    return row['name'] if row else None

def get_agents():
    conn = current_app.get_db_connection()
    agents = conn.execute('SELECT u.id, u.first_name, u.last_name, u.balance FROM users u JOIN roles r ON u.role_id = r.id WHERE LOWER(r.name) = "agent"').fetchall()
    conn.close()
    return agents

def get_all_users():
    conn = current_app.get_db_connection()
    users = conn.execute('SELECT u.id, u.first_name, u.last_name, u.balance FROM users u').fetchall()
    conn.close()
    return users

def get_all_transactions(limit=100):
    conn = current_app.get_db_connection()
    txs = conn.execute('''SELECT t.*, s.first_name as sender_first, s.last_name as sender_last, r.first_name as receiver_first, r.last_name as receiver_last FROM transactions t
        LEFT JOIN users s ON t.sender_id = s.id
        LEFT JOIN users r ON t.receiver_id = r.id
        ORDER BY t.timestamp DESC LIMIT ?''', (limit,)).fetchall()
    conn.close()
    return txs

def get_all_frauds(limit=100):
    conn = current_app.get_db_connection()
    frauds = conn.execute('''SELECT f.*, u1.first_name as reporter_first, u1.last_name as reporter_last, u2.first_name as reported_first, u2.last_name as reported_last FROM fraud_list f
        LEFT JOIN users u1 ON f.user_id = u1.id
        LEFT JOIN users u2 ON f.reported_user_id = u2.id
        ORDER BY f.id DESC LIMIT ?''', (limit,)).fetchall()
    conn.close()
    return frauds

def get_admin_logs(limit=100):
    conn = current_app.get_db_connection()
    logs = conn.execute('''SELECT l.*, a.first_name as admin_first, a.last_name as admin_last FROM admin_logs l LEFT JOIN users a ON l.admin_id = a.id ORDER BY l.timestamp DESC LIMIT ?''', (limit,)).fetchall()
    conn.close()
    return logs

def update_user_balance(user_id, amount):
    conn = current_app.get_db_connection()
    conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))
    conn.commit()
    conn.close()

def insert_transaction_admin(tx_id, amount, sender_id, receiver_id, note, tx_type):
    conn = current_app.get_db_connection()
    conn.execute('''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)''',
        (tx_id, amount, 'admin_add', sender_id, receiver_id, note, tx_type, None))
    conn.commit()
    conn.close()

def insert_admin_log(log_id, admin_id, ip_address, details):
    conn = current_app.get_db_connection()
    conn.execute('INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details) VALUES (?, ?, ?, ?, ?)',
        (log_id, admin_id, ip_address, datetime.now(), details))
    conn.commit()
    conn.close()

def insert_fraud_list(fraud_id, user_id, reported_user_id, reason):
    conn = current_app.get_db_connection()
    conn.execute('INSERT INTO fraud_list (id, user_id, reported_user_id, reason) VALUES (?, ?, ?, ?)',
        (fraud_id, user_id, reported_user_id, reason))
    conn.commit()
    conn.close()

def delete_fraud_list(reported_user_id):
    conn = current_app.get_db_connection()
    conn.execute('DELETE FROM fraud_list WHERE reported_user_id = ?', (reported_user_id,))
    conn.commit()
    conn.close()

def update_user_role(user_id, new_role_id):
    conn = current_app.get_db_connection()
    conn.execute('UPDATE users SET role_id = ? WHERE id = ?', (new_role_id, user_id))
    conn.commit()
    conn.close()

def get_role_id_by_name(role_name):
    conn = current_app.get_db_connection()
    row = conn.execute('SELECT id FROM roles WHERE LOWER(name) = ?', (role_name.lower(),)).fetchone()
    conn.close()
    return row['id'] if row else None
