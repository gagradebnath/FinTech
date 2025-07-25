# Utility functions for fraud operations
from flask import current_app
import uuid

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

def add_fraud_report(reporter_id, reported_user_id, reason):
    """Add fraud report using stored procedure"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc('ProcessFraudReport', [
                reporter_id, reported_user_id, reason, None, None  # OUT parameters
            ])
            
            # Fetch the OUT parameters
            cursor.execute("SELECT @_ProcessFraudReport_3 as success, @_ProcessFraudReport_4 as message")
            result = cursor.fetchone()
            
            if result and result['success']:
                return True, None
            else:
                return False, result['message'] if result else 'Unknown error'
                
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_fraud_reports(limit=50, offset=0):
    """Get fraud reports from the database"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT id, user_id, reported_user_id, reason, created_at
                FROM fraud_list
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            ''', (limit, offset))
            reports = cursor.fetchall()
            return reports
    except Exception as e:
        print(f"Error getting fraud reports: {e}")
        return []
    finally:
        conn.close()
