# Utility functions for transaction operations
from flask import current_app
import uuid

def get_user_by_id(user_id):
    conn = current_app.get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def send_money(sender_id, recipient_id, amount, note, payment_method):
    conn = current_app.get_db_connection()
    try:
        sender = conn.execute('SELECT * FROM users WHERE id = ?', (sender_id,)).fetchone()
        recipient = conn.execute('SELECT * FROM users WHERE id = ?', (recipient_id,)).fetchone()
        if not recipient:
            return False, 'Recipient not found.', sender
        if recipient['id'] == sender['id']:
            return False, 'Cannot send money to yourself.', sender
        amount_val = float(amount)
        if sender['balance'] < amount_val:
            return False, 'Insufficient balance.', sender
        conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount_val, sender['id']))
        conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount_val, recipient['id']))
        conn.execute('''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)''',
            (str(uuid.uuid4()), amount_val, payment_method, sender['id'], recipient['id'], note, 'transfer', None))
        conn.commit()
        sender = conn.execute('SELECT * FROM users WHERE id = ?', (sender['id'],)).fetchone()
        return True, f'Successfully sent {amount} to {recipient["first_name"]}.', sender
    except Exception as e:
        conn.rollback()
        return False, 'Failed to send money: ' + str(e), None
    finally:
        conn.close()
