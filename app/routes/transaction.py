from flask import Blueprint, render_template, request, current_app, session,  redirect, url_for, jsonify
import uuid
from .user import get_current_user
from app.utils.transaction_utils import get_user_by_id, send_money, lookup_user_by_identifier, is_user_flagged_fraud, get_all_transactions
from app.utils.permissions_utils import has_permission
from datetime import datetime, timedelta
import calendar

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
