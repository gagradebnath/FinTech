from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
import uuid
from .user import get_current_user
from app.utils.transaction_utils import get_user_by_id, send_money
from app.utils.permissions_utils import has_permission

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/transaction', methods=['GET'])
def get_transaction():
    return {'message': 'Transaction endpoint'}

@transaction_bp.route('/send-money', methods=['GET', 'POST'])
def send_money_route():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    error = None
    success = None
    if not has_permission(user['id'], 'send_money'):
        return render_template('send_money.html', error='Permission denied.', success=None)
    if request.method == 'POST':
        recipient_identifier = request.form.get('recipient_identifier')
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method')
        note = request.form.get('note')
        location = request.form.get('location')
        conn = current_app.get_db_connection()
        recipient = conn.execute('''
            SELECT u.id FROM users u
            LEFT JOIN contact_info c ON u.id = c.user_id
            WHERE LOWER(u.id) = ? OR LOWER(c.email) = ? OR c.phone = ?
        ''', (recipient_identifier.lower(), recipient_identifier.lower(), recipient_identifier)).fetchone()
        if not recipient:
            error = 'Recipient not found.'
        elif recipient['id'] == user['id']:
            error = 'Cannot send money to yourself.'
        else:
            # Check if recipient is in fraud_list
            fraud = conn.execute('SELECT 1 FROM fraud_list WHERE reported_user_id = ?', (recipient['id'],)).fetchone()
            if fraud:
                error = 'Cannot send money: recipient is flagged for fraud.'
            else:
                ok, msg, updated_user = send_money(
                    user['id'], recipient['id'], amount, payment_method, note, location, 'transfer')
                if ok:
                    success = msg
                    user = updated_user
                else:
                    error = msg
        conn.close()
    return render_template('send_money.html', error=error, success=success)
