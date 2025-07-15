# Utility functions for transaction operations
from flask import current_app
import uuid
from .advanced_sql_utils import AdvancedSQLUtils

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
    """
    Send money between users using enhanced stored procedure
    """
    print(f"send_money called: sender_id={sender_id}, recipient_id={recipient_id}, amount={amount}")
    
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Use the enhanced stored procedure
            cursor.callproc('ProcessMoneyTransferEnhanced', [
                sender_id, recipient_id, float(amount), payment_method, 
                note, tx_type, location, None, None, None
            ])
            
            # Fetch the OUT parameters
            cursor.execute("SELECT @_ProcessMoneyTransferEnhanced_7 as success, @_ProcessMoneyTransferEnhanced_8 as message, @_ProcessMoneyTransferEnhanced_9 as transaction_id")
            result = cursor.fetchone()
            
            if result:
                success = bool(result['success'])
                message = result['message']
                transaction_id = result['transaction_id']
                
                # Get updated sender info if successful
                if success:
                    sender = get_user_by_id(sender_id)
                    log_message = f"Transaction successful: {message}, id={transaction_id}"
                    print(log_message)
                    
                    # Log to browser console via /log endpoint
                    try:
                        import requests
                        requests.post('http://localhost:5000/log', json={"message": log_message})
                    except Exception as e:
                        print(f"Failed to log to browser console: {e}")
                    
                    return True, message, sender
                else:
                    print(f"Transaction failed: {message}")
                    sender = get_user_by_id(sender_id)
                    return False, message, sender
            else:
                return False, 'Failed to get procedure result', None
                    
    except Exception as e:
        print(f"Exception in send_money: {e}")
        return False, f'Failed to send money: {str(e)}', None
    finally:
        conn.close()

def agent_add_money(agent_id, user_id, amount):
    """Agent add money using enhanced stored procedure"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Use the enhanced transfer procedure
            cursor.callproc('ProcessMoneyTransferEnhanced', [
                agent_id, user_id, float(amount), 'agent_add', 
                f'Agent {agent_id} added money', 'Deposit', 'Agent Office', 
                None, None, None
            ])
            
            cursor.execute("SELECT @_ProcessMoneyTransferEnhanced_7 as success, @_ProcessMoneyTransferEnhanced_8 as message")
            result = cursor.fetchone()
            
            if result and result['success']:
                return (result['message'], None)
            else:
                return (None, result['message'] if result else 'Unknown error')
                
    except Exception as e:
        return (None, f"Failed to add money: {str(e)}")
    finally:
        conn.close()

def agent_cash_out(agent_id, user_id, amount):
    """Agent cash out using enhanced stored procedure"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Use the enhanced transfer procedure
            cursor.callproc('ProcessMoneyTransferEnhanced', [
                user_id, agent_id, float(amount), 'agent_cashout', 
                f'Agent {agent_id} cashed out', 'Withdrawal', 'Agent Office', 
                None, None, None
            ])
            
            cursor.execute("SELECT @_ProcessMoneyTransferEnhanced_7 as success, @_ProcessMoneyTransferEnhanced_8 as message")
            result = cursor.fetchone()
            
            if result and result['success']:
                return (result['message'], None)
            else:
                return (None, result['message'] if result else 'Unknown error')
                
    except Exception as e:
        return (None, f"Failed to cash out: {str(e)}")
    finally:
        conn.close()

def get_user_risk_score(user_id):
    """Get user risk score using MySQL function"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT GetUserRiskScore(%s) as risk_score", (user_id,))
            result = cursor.fetchone()
            return float(result['risk_score']) if result and result['risk_score'] else 0.0
    except Exception as e:
        print(f"Error getting risk score: {e}")
        return 0.0
    finally:
        conn.close()

def check_spending_limit(user_id, amount):
    """Check if user is within spending limits using MySQL function"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT IsWithinSpendingLimit(%s, %s) as within_limit", (user_id, amount))
            result = cursor.fetchone()
            return bool(result['within_limit']) if result else False
    except Exception as e:
        print(f"Error checking spending limit: {e}")
        return False
    finally:
        conn.close()

def rollback_transaction(transaction_id, reason="Manual rollback"):
    """Rollback a completed transaction using stored procedure"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc('RollbackTransaction', [transaction_id, reason, None, None])
            
            cursor.execute("SELECT @_RollbackTransaction_2 as success, @_RollbackTransaction_3 as message")
            result = cursor.fetchone()
            
            if result and result['success']:
                return True, result['message']
            else:
                return False, result['message'] if result else 'Unknown error'
                
    except Exception as e:
        print(f"Error rolling back transaction: {e}")
        return False, f"Rollback failed: {str(e)}"
    finally:
        conn.close()

def get_transaction_status(transaction_id):
    """Get transaction status and rollback capability"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc('GetTransactionStatus', [transaction_id, None, None, None])
            
            cursor.execute("SELECT @_GetTransactionStatus_1 as status, @_GetTransactionStatus_2 as can_rollback, @_GetTransactionStatus_3 as message")
            result = cursor.fetchone()
            
            if result:
                return result['status'], bool(result['can_rollback']), result['message']
            else:
                return None, False, 'Failed to get transaction status'
                
    except Exception as e:
        print(f"Error getting transaction status: {e}")
        return None, False, f"Status check failed: {str(e)}"
    finally:
        conn.close()

def backup_user_balance(user_id, operation_type="Manual backup"):
    """Create a backup of user balance"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc('BackupUserBalance', [user_id, operation_type, None, None, None])
            
            cursor.execute("SELECT @_BackupUserBalance_2 as backup_id, @_BackupUserBalance_3 as success, @_BackupUserBalance_4 as message")
            result = cursor.fetchone()
            
            if result and result['success']:
                return True, result['message'], result['backup_id']
            else:
                return False, result['message'] if result else 'Unknown error', None
                
    except Exception as e:
        print(f"Error backing up user balance: {e}")
        return False, f"Backup failed: {str(e)}", None
    finally:
        conn.close()

def restore_user_balance(backup_id, reason="Manual restore"):
    """Restore user balance from backup"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc('RestoreUserBalance', [backup_id, reason, None, None])
            
            cursor.execute("SELECT @_RestoreUserBalance_2 as success, @_RestoreUserBalance_3 as message")
            result = cursor.fetchone()
            
            if result and result['success']:
                return True, result['message']
            else:
                return False, result['message'] if result else 'Unknown error'
                
    except Exception as e:
        print(f"Error restoring user balance: {e}")
        return False, f"Restore failed: {str(e)}"
    finally:
        conn.close()

def auto_rollback_failed_transactions(hours_threshold=24):
    """Auto-rollback failed transactions older than threshold"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc('AutoRollbackFailedTransactions', [hours_threshold, None, None])
            
            cursor.execute("SELECT @_AutoRollbackFailedTransactions_1 as rolled_back_count, @_AutoRollbackFailedTransactions_2 as message")
            result = cursor.fetchone()
            
            if result:
                return True, result['message'], result['rolled_back_count']
            else:
                return False, 'Failed to auto-rollback transactions', 0
                
    except Exception as e:
        print(f"Error in auto-rollback: {e}")
        return False, f"Auto-rollback failed: {str(e)}", 0
    finally:
        conn.close()

def get_transaction_history_with_status(user_id, limit=10, offset=0):
    """Get transaction history with status and rollback information"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    t.id,
                    t.amount,
                    t.payment_method,
                    t.timestamp,
                    t.sender_id,
                    t.receiver_id,
                    t.note,
                    t.type,
                    t.location,
                    t.status,
                    s.first_name AS sender_name,
                    r.first_name AS receiver_name,
                    tb.backup_id,
                    tb.rollback_timestamp,
                    tb.rollback_reason
                FROM transactions t
                LEFT JOIN users s ON t.sender_id = s.id
                LEFT JOIN users r ON t.receiver_id = r.id
                LEFT JOIN transaction_backups tb ON t.id = tb.original_transaction_id
                WHERE t.sender_id = %s OR t.receiver_id = %s
                ORDER BY t.timestamp DESC
                LIMIT %s OFFSET %s
            """, (user_id, user_id, limit, offset))
            
            transactions = cursor.fetchall()
            
            # Convert to list of dictionaries for easier handling
            result = []
            for transaction in transactions:
                tx_dict = dict(transaction)
                if tx_dict['timestamp']:
                    tx_dict['timestamp'] = tx_dict['timestamp'].isoformat()
                if tx_dict['rollback_timestamp']:
                    tx_dict['rollback_timestamp'] = tx_dict['rollback_timestamp'].isoformat()
                result.append(tx_dict)
            
            return result
            
    except Exception as e:
        print(f"Error getting transaction history: {e}")
        return []
    finally:
        conn.close()

def get_failed_transactions(limit=50):
    """Get failed transactions for admin review"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    ft.id,
                    ft.attempted_transaction_id,
                    ft.sender_id,
                    ft.receiver_id,
                    ft.amount,
                    ft.payment_method,
                    ft.failure_reason,
                    ft.failure_timestamp,
                    s.first_name AS sender_name,
                    r.first_name AS receiver_name
                FROM failed_transactions ft
                LEFT JOIN users s ON ft.sender_id = s.id
                LEFT JOIN users r ON ft.receiver_id = r.id
                ORDER BY ft.failure_timestamp DESC
                LIMIT %s
            """, (limit,))
            
            failed_transactions = cursor.fetchall()
            
            # Convert to list of dictionaries
            result = []
            for transaction in failed_transactions:
                tx_dict = dict(transaction)
                if tx_dict['failure_timestamp']:
                    tx_dict['failure_timestamp'] = tx_dict['failure_timestamp'].isoformat()
                result.append(tx_dict)
            
            return result
            
    except Exception as e:
        print(f"Error getting failed transactions: {e}")
        return []
    finally:
        conn.close()

def get_system_audit_log(limit=100, operation_type=None):
    """Get system audit log for monitoring"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    sal.id,
                    sal.operation_type,
                    sal.entity_type,
                    sal.entity_id,
                    sal.user_id,
                    sal.old_values,
                    sal.new_values,
                    sal.timestamp,
                    sal.success,
                    sal.error_message,
                    u.first_name AS user_name
                FROM system_audit_log sal
                LEFT JOIN users u ON sal.user_id = u.id
            """
            
            params = []
            if operation_type:
                query += " WHERE sal.operation_type = %s"
                params.append(operation_type)
            
            query += " ORDER BY sal.timestamp DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            audit_logs = cursor.fetchall()
            
            # Convert to list of dictionaries
            result = []
            for log in audit_logs:
                log_dict = dict(log)
                if log_dict['timestamp']:
                    log_dict['timestamp'] = log_dict['timestamp'].isoformat()
                result.append(log_dict)
            
            return result
            
    except Exception as e:
        print(f"Error getting audit log: {e}")
        return []
    finally:
        conn.close()


def lookup_user_by_identifier(identifier):
    """
    Look up a user by email, phone, or username
    """
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Try to find user by email, phone, or username
            cursor.execute('''
                SELECT * FROM users 
                WHERE email = %s OR phone = %s OR username = %s
            ''', (identifier, identifier, identifier))
            user = cursor.fetchone()
            return user
    except Exception as e:
        print(f"Error looking up user: {e}")
        return None
    finally:
        conn.close()


def is_user_flagged_fraud(user_id):
    """
    Check if a user is flagged for fraud
    """
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT COUNT(*) as count FROM fraud_list 
                WHERE reported_user_id = %s
            ''', (user_id,))
            result = cursor.fetchone()
            return result['count'] > 0 if result else False
    except Exception as e:
        print(f"Error checking fraud status: {e}")
        return False
    finally:
        conn.close()
