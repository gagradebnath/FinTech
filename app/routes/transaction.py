from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
import uuid
from .user import get_current_user
from app.utils.transaction_utils import get_user_by_id, send_money

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
    if request.method == 'POST':
        recipient_id = request.form.get('recipient_id')
        amount = request.form.get('amount')
        note = request.form.get('note')
        payment_method = request.form.get('payment_method')
        ok, msg, updated_user = send_money(user['id'], recipient_id, amount, note, payment_method)
        if ok:
            success = msg
            user = updated_user
        else:
            error = msg
    return render_template('send_money.html', error=error, success=success)
