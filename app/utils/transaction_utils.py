# Utility functions for transaction operations
from flask import current_app
import uuid
from .blockchain import process_blockchain_transaction
from .overspending_detector import detect_overspending

def get_hybrid_blockchain():
    from .hybrid_blockchain import hybrid_blockchain
    return hybrid_blockchain

def get_user_by_id(user_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
        return user
    finally:
        conn.close()

def send_money(sender_id, recipient_id, amount, payment_method, note, location, tx_type):
    print(f"send_money called: sender_id={sender_id}, recipient_id={recipient_id}, amount={amount}, payment_method={payment_method}, note={note}, location={location}, type={tx_type}")
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (sender_id,))
            sender = cursor.fetchone()
            cursor.execute('SELECT * FROM users WHERE id = %s', (recipient_id,))
            recipient = cursor.fetchone()
            
            print(f"Sender: {sender['id'] if sender else None}, Recipient: {recipient['id'] if recipient else None}")
            
            if not sender:
                print("Sender not found.")
                return False, 'Sender not found.', None
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
            
            # Handle None/NULL balances by setting to 0
            sender_balance = float(sender['balance']) if sender['balance'] is not None else 0.0
            recipient_balance = float(recipient['balance']) if recipient['balance'] is not None else 0.0
            
            print(f"Sender balance: {sender_balance}, Recipient balance: {recipient_balance}")
            
            if sender_balance < amount_val:
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
            
            # Update balances with NULL handling
            cursor.execute('UPDATE users SET balance = COALESCE(balance, 0) - %s WHERE id = %s', (amount_val, sender['id']))
            cursor.execute('UPDATE users SET balance = COALESCE(balance, 0) + %s WHERE id = %s', (amount_val, recipient['id']))
            
            sql = '''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, %s)'''
            params = (tx_id, amount_val, payment_method, sender['id'], recipient['id'], note, tx_type, location)
            print(f"SQL: {sql}\nPARAMS: {params}")
            cursor.execute(sql, params)
            
            # Record transaction in blockchain(s) with better error handling
            hybrid_blockchain = get_hybrid_blockchain()
            blockchain_results = hybrid_blockchain.process_transaction(
                sender_id=sender['id'],
                receiver_id=recipient['id'],
                amount=amount_val,
                transaction_type=tx_type,
                note=note,
                location=location
            )
            
            # Log blockchain results and provide informative messages
            blockchain_messages = []
            if blockchain_results["python_blockchain"]:
                print("✅ Transaction recorded in Python blockchain")
                blockchain_messages.append("recorded in secure blockchain")
            if blockchain_results["solidity_blockchain"]:
                print(f"✅ Transaction recorded in Solidity blockchain")
                blockchain_messages.append("verified on Ethereum network")
            if blockchain_results["errors"]:
                print(f"⚠️ Blockchain errors: {blockchain_results['errors']}")
                # Don't fail the transaction for blockchain errors, just log them
            
            conn.commit()
            
            cursor.execute('SELECT * FROM users WHERE id = %s', (sender['id'],))
            sender = cursor.fetchone()
            
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

def lookup_user_by_identifier(identifier):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT u.* FROM users u
                LEFT JOIN contact_info c ON u.id = c.user_id
                WHERE LOWER(u.id) = %s OR LOWER(c.email) = %s OR c.phone = %s
            ''', (identifier.lower(), identifier.lower(), identifier))
            user = cursor.fetchone()
        return user
    finally:
        conn.close()

def is_user_flagged_fraud(user_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1 FROM fraud_list WHERE reported_user_id = %s', (user_id,))
            fraud = cursor.fetchone()
        return bool(fraud)
    finally:
        conn.close()

def agent_add_money(agent_id, user_id, amount):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE users SET balance = COALESCE(balance, 0) - %s WHERE id = %s', (amount, agent_id))
            cursor.execute('UPDATE users SET balance = COALESCE(balance, 0) + %s WHERE id = %s', (amount, user_id))
            cursor.execute('''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, %s)''',
                (str(uuid.uuid4()), amount, 'agent_add', agent_id, user_id, f'Agent {agent_id} added money', 'Deposit', None))
        conn.commit()
        return (f"Added {amount} to user (ID: {user_id})", None)
    except Exception as e:
        conn.rollback()
        return (None, f"Failed to add money: {str(e)}")
    finally:
        conn.close()

def agent_cash_out(agent_id, user_id, amount):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE users SET balance = COALESCE(balance, 0) - %s WHERE id = %s', (amount, user_id))
            cursor.execute('UPDATE users SET balance = COALESCE(balance, 0) + %s WHERE id = %s', (amount, agent_id))
            cursor.execute('''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, %s)''',
                (str(uuid.uuid4()), amount, 'agent_cashout', user_id, agent_id, f'Agent {agent_id} cashed out', 'Withdrawal', None))
        conn.commit()
        return (f"Cashed out {amount} from user (ID: {user_id})", None)
    except Exception as e:
        conn.rollback()
        return (None, f"Failed to cash out: {str(e)}")
    finally:
        conn.close()

def check_transaction_overspending(user_id, note, amount):
    """
    Check if a transaction would result in overspending
    Returns a dictionary with overspending information and whether to proceed
    """
    try:
        amount_float = float(amount)
        overspending = detect_overspending(user_id, note or 'Money transfer', amount_float)
        
        return {
            'success': True,
            'overspending_data': overspending,
            'should_warn': overspending['is_overspending'],
            'error': None
        }
    except ValueError:
        return {
            'success': False,
            'overspending_data': None,
            'should_warn': False,
            'error': 'Invalid amount specified.'
        }
    except Exception as e:
        return {
            'success': False,
            'overspending_data': None,
            'should_warn': False,
            'error': f'Error checking overspending: {str(e)}'
        }

def process_send_money_with_overspending(user_id, recipient_identifier, amount, payment_method, note, location, confirm_overspending=False):
    """
    Process send money transaction with overspending checks
    Returns a comprehensive result dictionary
    """
    # Import here to avoid circular imports
    from .permissions_utils import has_permission
    
    result = {
        'success': False,
        'error': None,
        'warning': None,
        'overspending_warning': None,
        'updated_user': None,
        'message': None
    }
    
    # Check permissions
    if not has_permission(user_id, 'perm_send_money'):
        result['error'] = 'Permission denied.'
        return result
    
    # Look up recipient
    recipient = lookup_user_by_identifier(recipient_identifier)
    
    # Basic validation
    if not recipient:
        result['error'] = 'Recipient not found.'
        return result
    elif recipient['id'] == user_id:
        result['error'] = 'Cannot send money to yourself.'
        return result
    elif is_user_flagged_fraud(recipient['id']):
        result['error'] = 'Cannot send money: recipient is flagged for fraud.'
        return result
    
    # Check overspending
    overspending_check = check_transaction_overspending(user_id, note, amount)
    
    if not overspending_check['success']:
        result['error'] = overspending_check['error']
        return result
    
    overspending = overspending_check['overspending_data']
    
    # If overspending detected and user hasn't confirmed yet
    if overspending['is_overspending'] and not confirm_overspending:
        result['overspending_warning'] = {
            'category': overspending['category'],
            'budget': overspending['budget'],
            'expense_amount': overspending['expense_amount'],
            'overspending_amount': overspending['overspending_amount'],
            'percentage_over': overspending['percentage_over'],
            'message': overspending['message'],
            'recipient_identifier': recipient_identifier,
            'amount': amount,
            'payment_method': payment_method,
            'note': note,
            'location': location
        }
        result['warning'] = 'Transaction requires overspending confirmation'
        return result
    
    # Proceed with transaction
    category_note = f"{overspending.get('category', 'Other')} : {note}" if note else overspending.get('category', 'Money transfer')
    ok, msg, updated_user = send_money(
        user_id, recipient['id'], amount, payment_method, category_note, location, 'Transfer')
    
    if ok:
        result['success'] = True
        result['message'] = msg
        result['updated_user'] = updated_user
        
        # Add overspending acknowledgment to success message if applicable
        if overspending['is_overspending'] and confirm_overspending:
            result['message'] += f" (Note: This transaction exceeded your {overspending['category']} budget by ${overspending['overspending_amount']:.2f})"
    else:
        result['error'] = msg
    
    return result

def get_user_balance_info(user_id):
    """Get comprehensive user balance information"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get user with balance
            cursor.execute('SELECT id, first_name, last_name, COALESCE(balance, 0) as balance FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return None
                
            # Get recent transactions for context
            cursor.execute('''
                SELECT amount, type, timestamp, 
                       CASE 
                           WHEN sender_id = %s THEN 'debit'
                           WHEN receiver_id = %s THEN 'credit'
                           ELSE 'unknown'
                       END as direction
                FROM transactions 
                WHERE sender_id = %s OR receiver_id = %s 
                ORDER BY timestamp DESC 
                LIMIT 5
            ''', (user_id, user_id, user_id, user_id))
            
            recent_transactions = cursor.fetchall()
            
            return {
                'user_id': user['id'],
                'name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                'balance': float(user['balance']),
                'recent_transactions': recent_transactions
            }
    finally:
        conn.close()
