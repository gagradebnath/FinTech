from flask import Blueprint, render_template, request, current_app, session, redirect, url_for, jsonify
import uuid
from .user import get_current_user
from app.utils.transaction_utils import get_user_by_id, send_money, lookup_user_by_identifier, is_user_flagged_fraud, get_all_transactions
from app.utils.permissions_utils import has_permission
from app.utils.jwt_auth import token_required, get_current_user_from_jwt
from app.utils.overspending_detector import detect_overspending
from datetime import datetime, timedelta
import calendar

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

@transaction_bp.route('/api/check-overspending', methods=['POST'])
def check_overspending():
    """API endpoint to check if a transaction would cause overspending"""
    user = get_current_user_from_jwt()
    if not user:
        user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    expense_description = data.get('description', '')
    expense_amount = data.get('amount', 0)
    
    try:
        expense_amount = float(expense_amount)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount'}), 400
    
    # Check for overspending
    overspending_info = detect_overspending(user['id'], expense_description, expense_amount)
    
    return jsonify({
        'success': True,
        'overspending_info': overspending_info
    }), 200

@transaction_bp.route('/send-money', methods=['GET', 'POST'])
def send_money_route():
    # Support both session-based and JWT-based authentication
    user = get_current_user_from_jwt()
    if not user:
        user = get_current_user()
    if not user:
        # Check if it's an API request
        is_api_request = request.headers.get('Authorization') or request.args.get('token') or request.is_json
        if is_api_request:
            return jsonify({'error': 'Authentication required'}), 401
        return redirect(url_for('user.login'))
    
    error = None
    success = None
    
    if not has_permission(user['id'], 'perm_send_money'):
        return render_template('send_money.html', error='Permission denied.', success=None, transactions=[], user=user)

    # Get filter from query params
    time_filter = request.args.get('filter', 'week')  # default to 'week'

    # Calculate date range based on filter
    now = datetime.now()
    if time_filter == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_filter == 'yesterday':
        start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
    elif time_filter == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # week
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Fetch all transactions
    transactions = get_all_transactions(user['id'])

    # Filter transactions in Python (or you can do it in SQL for efficiency)
    if time_filter == 'today':
        filtered_transactions = [tx for tx in transactions if tx['timestamp'].date() == now.date()]
    elif time_filter == 'yesterday':
        filtered_transactions = [tx for tx in transactions if tx['timestamp'].date() == (now - timedelta(days=1)).date()]
    elif time_filter == 'month':
        filtered_transactions = [tx for tx in transactions if tx['timestamp'].month == now.month and tx['timestamp'].year == now.year]
    elif time_filter == 'all':
        filtered_transactions = transactions
    else:  # week
        filtered_transactions = [tx for tx in transactions if tx['timestamp'] >= start_date]

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
            # Check if this is a force override (user clicked "proceed anyway")
            force_override = request.form.get('force_override') == 'true' or (request.is_json and data.get('force_override') == True)
            
            # Check for overspending only if not forcing override
            if not force_override:
                try:
                    amount_float = float(amount)
                    overspending_info = detect_overspending(user['id'], note or '', amount_float)
                    
                    # If overspending detected, return warning instead of processing
                    if overspending_info['is_overspending']:
                        if request.is_json:
                            return jsonify({
                                'warning': True,
                                'overspending_info': overspending_info
                            }), 200
                        else:
                            # For form submission, render template with warning
                            return render_template(
                                'send_money.html',
                                error=None,
                                success=None,
                                transactions=filtered_transactions,
                                user=user,
                                time_filter=time_filter,
                                overspending_warning=overspending_info,
                                form_data={
                                    'recipient_identifier': recipient_identifier,
                                    'amount': amount,
                                    'payment_method': payment_method,
                                    'note': note,
                                    'location': location
                                }
                            )
                except (ValueError, TypeError):
                    error = 'Invalid amount format.'
                    return render_template(
                        'send_money.html',
                        error=error,
                        success=success,
                        transactions=filtered_transactions,
                        user=user,
                        time_filter=time_filter
                    )
            
            # Process the transaction
            ok, msg, updated_user = send_money(
                user['id'], recipient['id'], amount, payment_method, note, location, 'Transfer')
            if ok:
                success = msg
                user = updated_user
            else:
                error = msg
    transactions = get_all_transactions(user['id'])
    return render_template(
        'send_money.html',
        error=error,
        success=success,
        transactions=filtered_transactions,
        user=user,
        time_filter=time_filter
    )

@transaction_bp.route('/api/transaction-report')
def transaction_report():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    period = request.args.get('period', 'monthly')
    now = datetime.now()
    data = []

    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            if period == 'yearly':
                labels = []
                received = []
                spent = []
                current_year = now.year
                for y in range(current_year - 3, current_year + 1):
                    labels.append(str(y))
                    # Received
                    cursor.execute('''SELECT IFNULL(SUM(amount),0) FROM transactions
                        WHERE receiver_id = %s  AND YEAR(timestamp) = %s''', (user['id'], y))
                    row = cursor.fetchone()
                    if row:
                        received.append(float(list(row.values())[0]))
                    else:
                        received.append(0)
                    # Spent
                    cursor.execute('''SELECT IFNULL(SUM(amount),0) FROM transactions
                        WHERE sender_id = %s AND YEAR(timestamp) = %s''', (user['id'], y))
                    row = cursor.fetchone()
                    spent.append(float(list(row.values())[0]) if row else 0)
                return jsonify({'labels': labels, 'received': received, 'spent': spent})

            elif period == 'weekly':
                year = now.year
                month = now.month
                num_days = calendar.monthrange(year, month)[1]
                num_weeks = (num_days + 6) // 7
                labels = [f'Week {i+1}' for i in range(num_weeks)]
                received = [0] * num_weeks
                spent = [0] * num_weeks
                for week in range(num_weeks):
                    start = datetime(year, month, 1) + timedelta(days=7*week)
                    end = start + timedelta(days=7)
                    cursor.execute('SELECT IFNULL(SUM(amount),0) FROM transactions WHERE receiver_id = %s AND timestamp >= %s AND timestamp < %s', (user['id'], start, end))
                    row = cursor.fetchone()
                    received[week] = float(list(row.values())[0]) if row else 0
                    cursor.execute('SELECT IFNULL(SUM(amount),0) FROM transactions WHERE sender_id = %s AND timestamp >= %s AND timestamp < %s', (user['id'], start, end))
                    row = cursor.fetchone()
                    spent[week] = float(list(row.values())[0]) if row else 0
                return jsonify({'labels': labels, 'received': received, 'spent': spent})

            else:  # monthly (default)
                labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                received = []
                spent = []
                year = now.year
                for m in range(1, 13):
                    # Received
                    cursor.execute('''SELECT IFNULL(SUM(amount),0) FROM transactions
                        WHERE receiver_id = %s  AND YEAR(timestamp) = %s AND MONTH(timestamp) = %s''',
                        (user['id'], year, m))
                    row = cursor.fetchone()
                    received.append(float(list(row.values())[0]) if row else 0)
                    # Spent
                    cursor.execute('''SELECT IFNULL(SUM(amount),0) FROM transactions
                        WHERE sender_id = %s  AND YEAR(timestamp) = %s AND MONTH(timestamp) = %s''',
                        (user['id'], year, m))
                    row = cursor.fetchone()
                    spent.append(float(list(row.values())[0]) if row else 0)
                return jsonify({'labels': labels, 'received': received, 'spent': spent})
    finally:
        conn.close()
