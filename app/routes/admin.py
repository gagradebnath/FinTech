from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash
from app.utils.user_utils import get_current_user
import uuid
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET'])
def get_admin():
    return {'message': 'Admin endpoint'}

@admin_bp.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    conn = current_app.get_db_connection()
    role_row = conn.execute('SELECT name FROM roles WHERE id = ?', (user['role_id'],)).fetchone()
    if not role_row or role_row['name'].lower() != 'admin':
        conn.close()
        return render_template('login.html', error='Access denied: Admins only.')
    agents = conn.execute('SELECT u.id, u.first_name, u.last_name, u.balance FROM users u JOIN roles r ON u.role_id = r.id WHERE LOWER(r.name) = "agent"').fetchall()
    users = conn.execute('SELECT u.id, u.first_name, u.last_name, u.balance FROM users u').fetchall()
    transactions = conn.execute('''SELECT t.*, s.first_name as sender_first, s.last_name as sender_last, r.first_name as receiver_first, r.last_name as receiver_last FROM transactions t
        LEFT JOIN users s ON t.sender_id = s.id
        LEFT JOIN users r ON t.receiver_id = r.id
        ORDER BY t.timestamp DESC LIMIT 100''').fetchall()
    frauds = conn.execute('''SELECT f.*, u1.first_name as reporter_first, u1.last_name as reporter_last, u2.first_name as reported_first, u2.last_name as reported_last FROM fraud_list f
        LEFT JOIN users u1 ON f.user_id = u1.id
        LEFT JOIN users u2 ON f.reported_user_id = u2.id
        ORDER BY f.id DESC LIMIT 100''').fetchall()
    try:
        admin_logs = conn.execute('''SELECT l.*, a.first_name as admin_first, a.last_name as admin_last FROM admin_logs l LEFT JOIN users a ON l.admin_id = a.id ORDER BY l.timestamp DESC LIMIT 100''').fetchall()
    except Exception:
        admin_logs = []
    add_money_success = None
    add_money_error = None
    fraud_action_success = None
    fraud_action_error = None
    role_action_success = None
    role_action_error = None
    if request.method == 'POST':
        if 'agent_id' in request.form and 'amount' in request.form:
            agent_id = request.form.get('agent_id')
            amount = request.form.get('amount')
            if not agent_id or not amount:
                add_money_error = 'All fields are required.'
            else:
                try:
                    amount_val = float(amount)
                    conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount_val, agent_id))
                    conn.execute('''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)''',
                        (str(uuid.uuid4()), amount_val, 'admin_add', user['id'], agent_id, f'Admin {user["id"]} added money to agent', 'admin_add_money', None))
                    # Log admin action
                    conn.execute('INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details) VALUES (?, ?, ?, ?, ?)',
                        (str(uuid.uuid4()), user['id'], request.remote_addr or 'localhost', datetime.now(), f"Added {amount} to agent (ID: {agent_id})"))
                    conn.commit()
                    add_money_success = f"Added {amount} to agent (ID: {agent_id})"
                except Exception as e:
                    add_money_error = 'Failed to process: ' + str(e)
        elif 'fraud_action' in request.form:
            fraud_action = request.form.get('fraud_action')
            fraud_user_id = request.form.get('fraud_user_id')
            reason = request.form.get('fraud_reason')
            try:
                if fraud_action == 'add' and fraud_user_id and reason:
                    conn.execute('INSERT INTO fraud_list (id, user_id, reported_user_id, reason) VALUES (?, ?, ?, ?)',
                        (str(uuid.uuid4()), user['id'], fraud_user_id, reason))
                    conn.execute('INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details) VALUES (?, ?, ?, ?, ?)',
                        (str(uuid.uuid4()), user['id'], request.remote_addr or 'localhost', datetime.now(), f"Added user {fraud_user_id} to fraud list. Reason: {reason}"))
                    conn.commit()
                    fraud_action_success = f"Added user {fraud_user_id} to fraud list."
                elif fraud_action == 'remove' and fraud_user_id:
                    conn.execute('DELETE FROM fraud_list WHERE reported_user_id = ?', (fraud_user_id,))
                    conn.execute('INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details) VALUES (?, ?, ?, ?, ?)',
                        (str(uuid.uuid4()), user['id'], request.remote_addr or 'localhost', datetime.now(), f"Removed user {fraud_user_id} from fraud list."))
                    conn.commit()
                    fraud_action_success = f"Removed user {fraud_user_id} from fraud list."
                else:
                    fraud_action_error = 'Invalid fraud action or missing fields.'
            except Exception as e:
                fraud_action_error = 'Failed to process fraud action: ' + str(e)
        elif 'role_action' in request.form and request.form.get('role_action') == 'change':
            role_user_id = request.form.get('role_user_id')
            new_role = request.form.get('new_role')
            if not role_user_id or not new_role:
                role_action_error = 'All fields are required.'
            else:
                try:
                    # Get new role_id
                    role_row = conn.execute('SELECT id FROM roles WHERE LOWER(name) = ?', (new_role.lower(),)).fetchone()
                    if not role_row:
                        role_action_error = 'Invalid role selected.'
                    else:
                        new_role_id = role_row['id'] if isinstance(role_row, dict) else role_row[0]
                        conn.execute('UPDATE users SET role_id = ? WHERE id = ?', (new_role_id, role_user_id))
                        conn.execute('INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details) VALUES (?, ?, ?, ?, ?)',
                            (str(uuid.uuid4()), user['id'], request.remote_addr or 'localhost', datetime.now(), f"Changed role of user {role_user_id} to {new_role}"))
                        conn.commit()
                        role_action_success = f"Changed role of user {role_user_id} to {new_role}."
                except Exception as e:
                    role_action_error = 'Failed to change role: ' + str(e)
    conn.close()
    return render_template('admin_dashboard.html', user=user, agents=agents, users=users, transactions=transactions, frauds=frauds, admin_logs=admin_logs, add_money_success=add_money_success, add_money_error=add_money_error, fraud_action_success=fraud_action_success, fraud_action_error=fraud_action_error, role_action_success=role_action_success, role_action_error=role_action_error)
