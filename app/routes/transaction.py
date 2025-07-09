from flask import Blueprint, render_template, request, current_app, session, redirect, url_for, jsonify
import uuid
from .user import get_current_user
from app.utils.transaction_utils import get_user_by_id, send_money, lookup_user_by_identifier, is_user_flagged_fraud
from app.utils.permissions_utils import has_permission
from app.utils.jwt_auth import token_required, get_current_user_from_jwt

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/transaction', methods=['GET'])
def get_transaction():
    return {'message': 'Transaction endpoint'}

@transaction_bp.route('/api/transactions', methods=['GET'])
@token_required
def get_transactions_api():
    """Protected API endpoint to get user transactions."""
    user = get_current_user_from_jwt()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get recent transactions for the user
    from app.utils.dashboard import get_recent_transactions
    transactions = get_recent_transactions(user['id'])
    
    return jsonify({
        'transactions': transactions,
        'count': len(transactions)
    }), 200

@transaction_bp.route('/send-money', methods=['GET', 'POST'])
def send_money_route():
    # Support both session-based and JWT-based authentication
    user = get_current_user_from_jwt()
    if not user:
        # Check if it's an API request
        is_api_request = request.headers.get('Authorization') or request.args.get('token') or request.is_json
        if is_api_request:
            return jsonify({'error': 'Authentication required'}), 401
        return redirect(url_for('user.login'))
    
    error = None
    success = None
    
    if not has_permission(user['id'], 'perm_send_money'):
        error_msg = 'Permission denied.'
        is_api_request = request.headers.get('Authorization') or request.args.get('token') or request.is_json
        if is_api_request:
            return jsonify({'error': error_msg}), 403
        return render_template('send_money.html', error=error_msg, success=None)
    
    if request.method == 'POST':
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            recipient_identifier = data.get('recipient_identifier')
            amount = data.get('amount')
            payment_method = data.get('payment_method')
            note = data.get('note')
            location = data.get('location')
        else:
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
                user['id'], recipient['id'], amount, payment_method, note, location, 'Transfer')
            if ok:
                success = msg
                user = updated_user
            else:
                error = msg
        
        # Return JSON response for API requests
        if request.is_json:
            if error:
                return jsonify({'error': error}), 400
            else:
                return jsonify({
                    'success': True,
                    'message': success,
                    'updated_balance': user.get('balance') if user else None
                }), 200
    
    # Return JSON response for API GET requests
    is_api_request = request.headers.get('Authorization') or request.args.get('token')
    if is_api_request and request.method == 'GET':
        return jsonify({
            'user_balance': user.get('balance', 0),
            'message': 'Send money endpoint ready'
        }), 200
    
    return render_template('send_money.html', error=error, success=success)
