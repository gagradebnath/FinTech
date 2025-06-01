from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
import uuid
from .user import get_current_user

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/transaction', methods=['GET'])
def get_transaction():
    return {'message': 'Transaction endpoint'}

@transaction_bp.route('/send-money', methods=['GET', 'POST'])
def send_money():
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
        conn = current_app.get_db_connection()
        try:
            # Validate recipient
            recipient = conn.execute('SELECT * FROM users WHERE id = ?', (recipient_id,)).fetchone()
            if not recipient:
                error = 'Recipient not found.'
            elif recipient['id'] == user['id']:
                error = 'Cannot send money to yourself.'
            else:
                # Check balance
                amount_val = float(amount)
                if user['balance'] < amount_val:
                    error = 'Insufficient balance.'
                else:
                    # Update balances
                    conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount_val, user['id']))
                    conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount_val, recipient['id']))
                    # Insert transaction
                    conn.execute('''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)''',
                        (str(uuid.uuid4()), amount_val, payment_method, user['id'], recipient['id'], note, 'transfer', None))
                    conn.commit()
                    success = f'Successfully sent {amount} to {recipient["first_name"]}.'
                    # Refresh user balance
                    user = conn.execute('SELECT * FROM users WHERE id = ?', (user['id'],)).fetchone()
        except Exception as e:
            conn.rollback()
            error = 'Failed to send money: ' + str(e)
        finally:
            conn.close()
    return render_template('send_money.html', error=error, success=success)
