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
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO fraud_list (id, user_id, reported_user_id, reason) VALUES (%s, %s, %s, %s)',
                         (str(uuid.uuid4()), reporter_id, reported_user_id, reason))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()
