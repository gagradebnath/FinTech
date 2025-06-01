# Utility functions for transaction operations
from flask import current_app
import uuid

def get_user_by_id(user_id):
    conn = current_app.get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def send_money(sender_id, recipient_id, amount, payment_method, note, location, tx_type):
    print(f"send_money called: sender_id={sender_id}, recipient_id={recipient_id}, amount={amount}, payment_method={payment_method}, note={note}, location={location}, type={tx_type}")
    conn = current_app.get_db_connection()
    try:
        sender = conn.execute('SELECT * FROM users WHERE id = ?', (sender_id,)).fetchone()
        recipient = conn.execute('SELECT * FROM users WHERE id = ?', (recipient_id,)).fetchone()
        print(f"Sender: {sender['id'] if sender else None}, Recipient: {recipient['id'] if recipient else None}")
        if not recipient:
            print("Recipient not found.")
            return False, 'Recipient not found.', sender
        if recipient['id'] == sender['id']:
            print("Cannot send money to yourself.")
            return False, 'Cannot send money to yourself.', sender
        try:
            amount_val = float(amount)
        except Exception as e:
            print(f"Invalid amount: {amount}")
            return False, 'Invalid amount.', sender
        if sender['balance'] < amount_val:
            print("Insufficient balance.")
            return False, 'Insufficient balance.', sender
        if not payment_method:
            print("Missing payment_method")
            return False, 'Payment method is required.', sender
        if not tx_type:
            print("Missing transaction type")
            return False, 'Transaction type is required.', sender
        # Print all params before insert
        tx_id = str(uuid.uuid4())
        print(f"INSERT PARAMS: id={tx_id}, amount={amount_val}, payment_method={payment_method}, sender_id={sender['id']}, receiver_id={recipient['id']}, note={note}, type={tx_type}, location={location}")
        conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount_val, sender['id']))
        conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount_val, recipient['id']))
        sql = '''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)'''
        params = (tx_id, amount_val, payment_method, sender['id'], recipient['id'], note, tx_type, location)
        print(f"SQL: {sql}\nPARAMS: {params}")
        conn.execute(sql, params)
        conn.commit()
        sender = conn.execute('SELECT * FROM users WHERE id = ?', (sender['id'],)).fetchone()
        log_message = f"Transaction successful: id={tx_id}, amount={amount_val}, payment_method={payment_method}, sender_id={sender['id']}, receiver_id={recipient['id']}, note={note}, type={tx_type}, location={location}"
        print(log_message)
        # Log to browser console via /log endpoint
        try:
            import requests
            requests.post('http://localhost:5000/log', json={"message": log_message})
        except Exception as e:
            print(f"Failed to log to browser console: {e}")
        return True, f'Successfully sent {amount} to {recipient["first_name"]}.', sender
    except Exception as e:
        conn.rollback()
        print(f"Exception in send_money: {e}")
        return False, 'Failed to send money: ' + str(e), None
    finally:
        conn.close()
