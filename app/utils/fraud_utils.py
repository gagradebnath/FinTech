# Utility functions for fraud operations
from flask import current_app
import uuid

def lookup_user_by_identifier(identifier):
    conn = current_app.get_db_connection()
    user = conn.execute('''
        SELECT u.id FROM users u
        LEFT JOIN contact_info c ON u.id = c.user_id
        WHERE LOWER(u.id) = ? OR LOWER(c.email) = ? OR c.phone = ?
    ''', (identifier.lower(), identifier.lower(), identifier)).fetchone()
    conn.close()
    return user

def add_fraud_report(reporter_id, reported_user_id, reason):
    conn = current_app.get_db_connection()
    try:
        conn.execute('INSERT INTO fraud_list (id, user_id, reported_user_id, reason) VALUES (?, ?, ?, ?)',
                     (str(uuid.uuid4()), reporter_id, reported_user_id, reason))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()
