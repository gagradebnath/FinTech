from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash
from app.utils.user_utils import get_current_user
from app.utils.dashboard import get_user_budgets, get_recent_expenses
from app.utils.permissions_utils import has_permission
import uuid

agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/agent', methods=['GET'])
def get_agent():
    return {'message': 'Agent endpoint'}

@agent_bp.route('/agent/dashboard', methods=['GET', 'POST'])
def agent_dashboard():
    user = get_current_user()
    if not has_permission(user['id'], 'view_dashboard'):
        return render_template('agent_dashboard.html', user=user, budgets=[], expenses=[], add_money_success=None, add_money_error='Permission denied.')
    budgets = get_user_budgets(user['id'])
    expenses = get_recent_expenses(user['id'])
    add_money_success = None
    add_money_error = None
    if request.method == 'POST':
        target_identifier = request.form.get('target_identifier')
        amount = request.form.get('amount')
        operation = request.form.get('operation')  # 'add' or 'cashout'
        if not target_identifier or not amount or not operation:
            add_money_error = 'All fields are required.'
        else:
            try:
                conn = current_app.get_db_connection()
                target = conn.execute('''
                    SELECT u.id, u.first_name, u.last_name, u.balance FROM users u
                    LEFT JOIN contact_info c ON u.id = c.user_id
                    WHERE LOWER(u.id) = ? OR LOWER(c.email) = ? OR c.phone = ?
                ''', (target_identifier.lower(), target_identifier.lower(), target_identifier)).fetchone()
                if not target:
                    add_money_error = 'User not found.'
                elif target['id'] == user['id']:
                    add_money_error = 'You cannot add or cash out money to your own account.'
                else:
                    amount_val = float(amount)
                    agent_bal = conn.execute('SELECT balance FROM users WHERE id = ?', (user['id'],)).fetchone()['balance']
                    if operation == 'add':
                        if not has_permission(user['id'], 'add_money'):
                            add_money_error = 'Permission denied.'
                        elif agent_bal < amount_val:
                            add_money_error = 'Insufficient agent balance.'
                        else:
                            # Debit agent, credit user
                            conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount_val, user['id']))
                            conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount_val, target['id']))
                            conn.execute('''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)''',
                                (str(uuid.uuid4()), amount_val, 'agent_add', user['id'], target['id'], f'Agent {user["id"]} added money', 'add_money', None))
                            conn.commit()
                            add_money_success = f"Added {amount} to {target['first_name']} {target['last_name']} (ID: {target['id']})"
                    elif operation == 'cashout':
                        if not has_permission(user['id'], 'cash_out'):
                            add_money_error = 'Permission denied.'
                        elif target['balance'] < amount_val:
                            add_money_error = 'Insufficient user balance for cash out.'
                        else:
                            # Debit user, credit agent
                            conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount_val, target['id']))
                            conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount_val, user['id']))
                            conn.execute('''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)''',
                                (str(uuid.uuid4()), amount_val, 'agent_cashout', target['id'], user['id'], f'Agent {user["id"]} cashed out', 'cash_out', None))
                            conn.commit()
                            add_money_success = f"Cashed out {amount} from {target['first_name']} {target['last_name']} (ID: {target['id']})"
                conn.close()
            except Exception as e:
                add_money_error = 'Failed to process: ' + str(e)
    return render_template('agent_dashboard.html', user=user, budgets=budgets, expenses=expenses, add_money_success=add_money_success, add_money_error=add_money_error)
