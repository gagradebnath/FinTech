# Utility functions for transaction operations
from flask import current_app
import uuid
from decimal import Decimal
from .blockchain_utils import process_transaction_with_blockchain, get_user_blockchain_summary

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
            
            if not recipient:
                print("Recipient not found.")
                return False, 'Recipient not found.', sender
            if recipient['id'] == sender['id']:
                print("Cannot send money to yourself.")
                return False, 'Cannot send money to yourself.', sender
                
            try:
                # Convert amount to Decimal for consistent calculations
                amount_val = Decimal(str(amount))
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
            
            # Calculate new balances using Decimal arithmetic
            new_sender_balance = sender['balance'] - amount_val
            new_recipient_balance = recipient['balance'] + amount_val
            
            # Validate sender transaction with blockchain
            sender_blockchain_valid, sender_message = process_transaction_with_blockchain(
                sender['id'], 
                -amount_val,  # Negative amount for sender
                new_sender_balance,
                f"send_money_{payment_method}",
                {
                    'transaction_id': tx_id,
                    'recipient_id': recipient['id'],
                    'note': note,
                    'location': location,
                    'type': tx_type
                }
            )
            
            if not sender_blockchain_valid:
                print(f"Sender blockchain validation failed: {sender_message}")
                return False, f'Transaction blocked: {sender_message}', sender
            
            # Validate recipient transaction with blockchain
            recipient_blockchain_valid, recipient_message = process_transaction_with_blockchain(
                recipient['id'],
                amount_val,   # Positive amount for recipient
                new_recipient_balance,
                f"receive_money_{payment_method}",
                {
                    'transaction_id': tx_id,
                    'sender_id': sender['id'],
                    'note': note,
                    'location': location,
                    'type': tx_type
                }
            )
            
            if not recipient_blockchain_valid:
                print(f"Recipient blockchain validation failed: {recipient_message}")
                return False, f'Transaction blocked: {recipient_message}', sender
            
            # Update user balances using Decimal values
            cursor.execute('UPDATE users SET balance = balance - %s WHERE id = %s', (amount_val, sender['id']))
            cursor.execute('UPDATE users SET balance = balance + %s WHERE id = %s', (amount_val, recipient['id']))
            
            # Record transaction in main transactions table
            sql = '''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, %s)'''
            params = (tx_id, amount_val, payment_method, sender['id'], recipient['id'], note, tx_type, location)
            print(f"SQL: {sql}\nPARAMS: {params}")
            cursor.execute(sql, params)
            
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
                SELECT u.id FROM users u
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
            # Convert amount to Decimal for consistent calculations
            amount_val = Decimal(str(amount))
            
            # Get current balances
            cursor.execute('SELECT balance FROM users WHERE id = %s', (agent_id,))
            agent = cursor.fetchone()
            cursor.execute('SELECT balance FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            
            if not agent or not user:
                return (None, "Agent or user not found")
            
            # Calculate new balances
            new_agent_balance = agent['balance'] - amount_val
            new_user_balance = user['balance'] + amount_val
            
            # Validate agent transaction with blockchain
            agent_blockchain_valid, agent_message = process_transaction_with_blockchain(
                agent_id,
                -amount_val,  # Negative amount for agent
                new_agent_balance,
                "agent_add_money",
                {
                    'recipient_id': user_id,
                    'note': f'Agent {agent_id} added money',
                    'type': 'agent_service'
                }
            )
            
            if not agent_blockchain_valid:
                return (None, f'Agent transaction blocked: {agent_message}')
            
            # Validate user transaction with blockchain
            user_blockchain_valid, user_message = process_transaction_with_blockchain(
                user_id,
                amount_val,   # Positive amount for user
                new_user_balance,
                "agent_receive_money",
                {
                    'agent_id': agent_id,
                    'note': f'Received money from agent {agent_id}',
                    'type': 'agent_service'
                }
            )
            
            if not user_blockchain_valid:
                return (None, f'User transaction blocked: {user_message}')
            
            # Update balances
            cursor.execute('UPDATE users SET balance = balance - %s WHERE id = %s', (amount_val, agent_id))
            cursor.execute('UPDATE users SET balance = balance + %s WHERE id = %s', (amount_val, user_id))
            
            # Record transaction
            cursor.execute('''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, %s)''',
                (str(uuid.uuid4()), amount_val, 'agent_add', agent_id, user_id, f'Agent {agent_id} added money', 'Deposit', None))
        conn.commit()
        return (f"Added {amount_val} to user (ID: {user_id})", None)
    except Exception as e:
        conn.rollback()
        return (None, f"Failed to add money: {str(e)}")
    finally:
        conn.close()

def agent_cash_out(agent_id, user_id, amount):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Convert amount to Decimal for consistent calculations
            amount_val = Decimal(str(amount))
            
            # Get current balances
            cursor.execute('SELECT balance FROM users WHERE id = %s', (agent_id,))
            agent = cursor.fetchone()
            cursor.execute('SELECT balance FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            
            if not agent or not user:
                return (None, "Agent or user not found")
            
            # Calculate new balances
            new_agent_balance = agent['balance'] + amount_val
            new_user_balance = user['balance'] - amount_val
            
            # Validate user transaction with blockchain
            user_blockchain_valid, user_message = process_transaction_with_blockchain(
                user_id,
                -amount_val,  # Negative amount for user
                new_user_balance,
                "agent_cash_out",
                {
                    'agent_id': agent_id,
                    'note': f'Cashed out to agent {agent_id}',
                    'type': 'agent_service'
                }
            )
            
            if not user_blockchain_valid:
                return (None, f'User transaction blocked: {user_message}')
            
            # Validate agent transaction with blockchain
            agent_blockchain_valid, agent_message = process_transaction_with_blockchain(
                agent_id,
                amount_val,   # Positive amount for agent
                new_agent_balance,
                "agent_receive_cashout",
                {
                    'user_id': user_id,
                    'note': f'Received cashout from user {user_id}',
                    'type': 'agent_service'
                }
            )
            
            if not agent_blockchain_valid:
                return (None, f'Agent transaction blocked: {agent_message}')
            
            # Update balances
            cursor.execute('UPDATE users SET balance = balance - %s WHERE id = %s', (amount_val, user_id))
            cursor.execute('UPDATE users SET balance = balance + %s WHERE id = %s', (amount_val, agent_id))
            
            # Record transaction
            cursor.execute('''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, %s)''',
                (str(uuid.uuid4()), amount_val, 'agent_cashout', user_id, agent_id, f'Agent {agent_id} cashed out', 'Withdrawal', None))
        conn.commit()
        return (f"Cashed out {amount_val} from user (ID: {user_id})", None)
    except Exception as e:
        conn.rollback()
        return (None, f"Failed to cash out: {str(e)}")
    finally:
        conn.close()
def get_all_transactions(user_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT t.amount, t.timestamp, t.note, t.location, t.type, t.receiver_id, t.sender_id, t.payment_method
                FROM transactions t
                WHERE t.sender_id = %s OR t.receiver_id = %s
                ORDER BY t.timestamp DESC
            ''', (user_id, user_id))
            txs = cursor.fetchall()
        return txs
    finally:
        conn.close()

def rollback_transaction(transaction_id, reason, admin_user_id=None):
    """Rollback a transaction by reversing the balance changes"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get the original transaction
            cursor.execute('''
                SELECT id, sender_id, receiver_id, amount, timestamp
                FROM transactions 
                WHERE id = %s
            ''', (transaction_id,))
            transaction = cursor.fetchone()
            
            if not transaction:
                return False, "Transaction not found"
            
            # Check if transaction is within rollback window (72 hours)
            from datetime import datetime, timedelta
            if transaction['timestamp'] < datetime.now() - timedelta(hours=72):
                return False, "Transaction is too old to rollback (72 hour limit)"
            
            # Check if already rolled back
            cursor.execute('SELECT id FROM transactions WHERE note LIKE %s', (f'%ROLLBACK of {transaction_id}%',))
            if cursor.fetchone():
                return False, "Transaction has already been rolled back"
            
            # Reverse the transaction
            cursor.execute('UPDATE users SET balance = balance + %s WHERE id = %s', 
                         (transaction['amount'], transaction['sender_id']))
            cursor.execute('UPDATE users SET balance = balance - %s WHERE id = %s', 
                         (transaction['amount'], transaction['receiver_id']))
            
            # Create rollback transaction record
            rollback_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location)
                VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, %s)
            ''', (rollback_id, transaction['amount'], 'rollback', transaction['receiver_id'], transaction['sender_id'], 
                  f'ROLLBACK of {transaction_id}: {reason}', 'Refund', None))
            
            # Log the rollback only if admin_user_id is provided and exists
            if admin_user_id:
                try:
                    cursor.execute('SELECT id FROM users WHERE id = %s', (admin_user_id,))
                    if cursor.fetchone():
                        cursor.execute('''
                            INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details)
                            VALUES (%s, %s, %s, NOW(), %s)
                        ''', (str(uuid.uuid4()), admin_user_id, '127.0.0.1', 
                              f'Transaction {transaction_id} rolled back: {reason}'))
                except Exception as log_error:
                    # If logging fails, continue with rollback but log the error
                    print(f"Failed to log rollback action: {log_error}")
            
            conn.commit()
            return True, f"Transaction {transaction_id} successfully rolled back"
            
    except Exception as e:
        conn.rollback()
        return False, f"Rollback failed: {str(e)}"
    finally:
        conn.close()

def get_transaction_status(transaction_id):
    """Check if a transaction can be rolled back"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get the transaction
            cursor.execute('''
                SELECT id, sender_id, receiver_id, amount, timestamp
                FROM transactions 
                WHERE id = %s
            ''', (transaction_id,))
            transaction = cursor.fetchone()
            
            if not transaction:
                return "NOT_FOUND", False, "Transaction not found"
            
            # Check if already rolled back
            cursor.execute('SELECT id FROM transactions WHERE note LIKE %s', (f'%ROLLBACK of {transaction_id}%',))
            if cursor.fetchone():
                return "ROLLED_BACK", False, "Transaction has already been rolled back"
            
            # Check rollback window (72 hours)
            from datetime import datetime, timedelta
            if transaction['timestamp'] < datetime.now() - timedelta(hours=72):
                return "EXPIRED", False, "Transaction is too old to rollback (72 hour limit)"
            
            return "ELIGIBLE", True, "Transaction is eligible for rollback"
            
    except Exception as e:
        return "ERROR", False, f"Error checking status: {str(e)}"
    finally:
        conn.close()

def backup_user_balance(user_id, operation_type, admin_user_id=None):
    """Create a backup of user balance"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get current balance
            cursor.execute('SELECT balance FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return False, "User not found", None
            
            backup_id = str(uuid.uuid4())
            
            # Log the backup only if admin_user_id is provided and exists
            if admin_user_id:
                try:
                    cursor.execute('SELECT id FROM users WHERE id = %s', (admin_user_id,))
                    if cursor.fetchone():
                        cursor.execute('''
                            INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details)
                            VALUES (%s, %s, %s, NOW(), %s)
                        ''', (backup_id, admin_user_id, '127.0.0.1', 
                              f'Balance backup created for user {user_id}: {operation_type} - Balance: {user["balance"]}'))
                except Exception as log_error:
                    print(f"Failed to log backup action: {log_error}")
            
            conn.commit()
            return True, f"Balance backup created successfully", backup_id
            
    except Exception as e:
        conn.rollback()
        return False, f"Backup failed: {str(e)}", None
    finally:
        conn.close()

def restore_user_balance(backup_id, reason, admin_user_id=None):
    """Restore user balance from backup"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get backup information from admin_logs
            cursor.execute('''
                SELECT admin_id, details FROM admin_logs 
                WHERE id = %s AND details LIKE '%Balance backup created%'
            ''', (backup_id,))
            backup = cursor.fetchone()
            
            if not backup:
                return False, "Backup not found"
            
            # Extract balance from details (simple parsing)
            import re
            balance_match = re.search(r'Balance: (\d+(?:\.\d+)?)', backup['details'])
            if not balance_match:
                return False, "Unable to parse backup balance"
            
            balance = float(balance_match.group(1))
            # Extract user_id from details instead of using admin_id
            user_match = re.search(r'for user ([^:]+):', backup['details'])
            if user_match:
                user_id = user_match.group(1)
            else:
                # Fallback to admin_id if user_id not found in details
                user_id = backup['admin_id']
            
            # Restore the balance
            cursor.execute('UPDATE users SET balance = %s WHERE id = %s', (balance, user_id))
            
            # Log the restore only if admin_user_id is provided and exists
            if admin_user_id:
                try:
                    cursor.execute('SELECT id FROM users WHERE id = %s', (admin_user_id,))
                    if cursor.fetchone():
                        cursor.execute('''
                            INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details)
                            VALUES (%s, %s, %s, NOW(), %s)
                        ''', (str(uuid.uuid4()), admin_user_id, '127.0.0.1', 
                              f'Balance restored from backup {backup_id} for user {user_id}: {reason}'))
                except Exception as log_error:
                    print(f"Failed to log restore action: {log_error}")
            
            conn.commit()
            return True, f"Balance restored successfully from backup {backup_id}"
            
    except Exception as e:
        conn.rollback()
        return False, f"Restore failed: {str(e)}"
    finally:
        conn.close()

def auto_rollback_failed_transactions(hours_threshold=24, admin_user_id=None):
    """Auto-rollback failed transactions older than threshold"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            from datetime import datetime, timedelta
            
            # Find transactions that might be considered "failed"
            # For now, we'll look for transactions that are older than threshold
            # and don't have corresponding successful completions
            threshold_time = datetime.now() - timedelta(hours=hours_threshold)
            
            cursor.execute('''
                SELECT id, sender_id, receiver_id, amount
                FROM transactions 
                WHERE timestamp < %s 
                AND note NOT LIKE '%ROLLBACK%'
                AND type != 'Refund'
            ''', (threshold_time,))
            
            potential_failed = cursor.fetchall()
            rolled_back_count = 0
            
            for tx in potential_failed:
                # Check if this transaction has already been rolled back
                cursor.execute('SELECT id FROM transactions WHERE note LIKE %s', (f'%ROLLBACK of {tx["id"]}%',))
                if not cursor.fetchone():
                    # Try to rollback
                    success, message = rollback_transaction(tx['id'], 'Auto-rollback due to age', admin_user_id)
                    if success:
                        rolled_back_count += 1
            
            return True, f"Auto-rollback completed. {rolled_back_count} transactions rolled back.", rolled_back_count
            
    except Exception as e:
        return False, f"Auto-rollback failed: {str(e)}", 0
    finally:
        conn.close()

def get_transaction_history_with_status(user_id, limit=10, offset=0):
    """Get transaction history with rollback status"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT t.id, t.amount, t.timestamp, t.note, t.type, t.sender_id, t.receiver_id,
                       CASE 
                           WHEN rb.id IS NOT NULL THEN 'ROLLED_BACK'
                           WHEN t.timestamp < DATE_SUB(NOW(), INTERVAL 72 HOUR) THEN 'EXPIRED'
                           ELSE 'ELIGIBLE'
                       END as rollback_status
                FROM transactions t
                LEFT JOIN transactions rb ON rb.note LIKE CONCAT('%ROLLBACK of ', t.id, '%')
                WHERE t.sender_id = %s OR t.receiver_id = %s
                ORDER BY t.timestamp DESC
                LIMIT %s OFFSET %s
            ''', (user_id, user_id, limit, offset))
            
            transactions = cursor.fetchall()
            return transactions
            
    except Exception as e:
        return []
    finally:
        conn.close()

def get_failed_transactions(limit=50):
    """Get failed transactions for admin review"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            from datetime import datetime, timedelta
            
            # For now, we'll consider transactions older than 24 hours as potentially failed
            # In a real implementation, you'd have a proper failed_transactions table
            threshold_time = datetime.now() - timedelta(hours=24)
            
            cursor.execute('''
                SELECT t.id as attempted_transaction_id, t.amount, t.timestamp as failure_timestamp,
                       t.payment_method, t.note as failure_reason,
                       CONCAT(s.first_name, ' ', s.last_name) as sender_name,
                       CONCAT(r.first_name, ' ', r.last_name) as receiver_name
                FROM transactions t
                LEFT JOIN users s ON t.sender_id = s.id
                LEFT JOIN users r ON t.receiver_id = r.id
                LEFT JOIN transactions rb ON rb.note LIKE CONCAT('%ROLLBACK of ', t.id, '%')
                WHERE t.timestamp < %s 
                AND rb.id IS NULL
                AND t.type != 'Refund'
                ORDER BY t.timestamp DESC
                LIMIT %s
            ''', (threshold_time, limit))
            
            failed_transactions = cursor.fetchall()
            return failed_transactions
            
    except Exception as e:
        return []
    finally:
        conn.close()

def get_system_audit_log(limit=50, operation_type=None):
    """Get system audit log"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            if operation_type:
                cursor.execute('''
                    SELECT al.id, al.timestamp, al.details,
                           CASE 
                               WHEN al.details LIKE '%rollback%' THEN 'ROLLBACK'
                               WHEN al.details LIKE '%backup%' THEN 'BACKUP'
                               WHEN al.details LIKE '%restore%' THEN 'RESTORE'
                               ELSE 'OTHER'
                           END as operation_type,
                           'TRANSACTION' as entity_type,
                           CONCAT(u.first_name, ' ', u.last_name) as user_name,
                           TRUE as success
                    FROM admin_logs al
                    LEFT JOIN users u ON al.admin_id = u.id
                    WHERE al.details LIKE %s
                    ORDER BY al.timestamp DESC
                    LIMIT %s
                ''', (f'%{operation_type.lower()}%', limit))
            else:
                cursor.execute('''
                    SELECT al.id, al.timestamp, al.details,
                           CASE 
                               WHEN al.details LIKE '%rollback%' THEN 'ROLLBACK'
                               WHEN al.details LIKE '%backup%' THEN 'BACKUP'
                               WHEN al.details LIKE '%restore%' THEN 'RESTORE'
                               ELSE 'OTHER'
                           END as operation_type,
                           'TRANSACTION' as entity_type,
                           CONCAT(u.first_name, ' ', u.last_name) as user_name,
                           TRUE as success
                    FROM admin_logs al
                    LEFT JOIN users u ON al.admin_id = u.id
                    ORDER BY al.timestamp DESC
                    LIMIT %s
                ''', (limit,))
            
            audit_logs = cursor.fetchall()
            return audit_logs
            
    except Exception as e:
        return []
    finally:
        conn.close()