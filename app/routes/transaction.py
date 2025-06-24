from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
import uuid
from .user import get_current_user
from app.utils.transaction_utils import get_user_by_id, send_money, lookup_user_by_identifier, is_user_flagged_fraud
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
    if not has_permission(user['id'], 'perm_send_money'):
        return render_template('send_money.html', error='Permission denied.', success=None)
    if request.method == 'POST':
        recipient_identifier = request.form.get('recipient_identifier')
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method')
        note = request.form.get('note')
        location = request.form.get('location')
        recipient = lookup_user_by_identifier(recipient_identifier)
        if not recipient:
            error = 'Recipient not found.'
        elif recipient['id'] == user['id']:
            error = 'Cannot send money to yourself.'
        elif is_user_flagged_fraud(recipient['id']):
            error = 'Cannot send money: recipient is flagged for fraud.'
        else:
            ok, msg, updated_user = send_money(
                user['id'], recipient['id'], amount, payment_method, note, location, 'transfer')
            if ok:
                success = msg
                user = updated_user
            else:
                error = msg
    return render_template('send_money.html', error=error, success=success)
