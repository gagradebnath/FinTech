# Utility functions for fraud operations
from flask import current_app
import uuid

def lookup_user_by_identifier(identifier):
    """Look up user by ID, email, or phone with better error handling"""
    conn = None
    try:
        conn = current_app.get_db_connection()
        with conn.cursor() as cursor:
            # Use explicit COLLATE to avoid collation mismatch issues
            cursor.execute('''
                SELECT u.id FROM users u
                LEFT JOIN contact_info c ON u.id = c.user_id
                WHERE LOWER(u.id COLLATE utf8mb4_unicode_ci) = %s 
                   OR LOWER(COALESCE(c.email, '') COLLATE utf8mb4_unicode_ci) = %s 
                   OR c.phone = %s
            ''', (identifier.lower(), identifier.lower(), identifier))
            user = cursor.fetchone()
            return user
    except Exception as e:
        current_app.logger.error(f"Database error in lookup_user_by_identifier: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def add_fraud_report(reporter_id, reported_user_id, reason):
    """Add fraud report using direct SQL queries (no stored procedure)"""
    conn = None
    try:
        conn = current_app.get_db_connection()
        with conn.cursor() as cursor:
            # Start transaction
            cursor.execute("START TRANSACTION")
            
            # Validate input parameters
            if not reporter_id or not reported_user_id or not reason:
                conn.rollback()
                return False, 'All fields are required'
            
            if len(reason.strip()) < 10:
                conn.rollback()
                return False, 'Reason must be at least 10 characters long'
            
            if reporter_id == reported_user_id:
                conn.rollback()
                return False, 'You cannot report yourself'
            
            # Check if reporter exists
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE id COLLATE utf8mb4_unicode_ci = %s", (reporter_id,))
            reporter_exists = cursor.fetchone()['count']
            
            if reporter_exists == 0:
                conn.rollback()
                return False, 'Reporter user not found'
            
            # Check if reported user exists
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE id COLLATE utf8mb4_unicode_ci = %s", (reported_user_id,))
            reported_exists = cursor.fetchone()['count']
            
            if reported_exists == 0:
                conn.rollback()
                return False, 'Reported user not found'
            
            # Check for existing reports (prevent duplicates)
            cursor.execute("""
                SELECT COUNT(*) as count FROM fraud_list 
                WHERE user_id COLLATE utf8mb4_unicode_ci = %s 
                  AND reported_user_id COLLATE utf8mb4_unicode_ci = %s
            """, (reporter_id, reported_user_id))
            existing_reports = cursor.fetchone()['count']
            
            if existing_reports > 0:
                conn.rollback()
                return False, 'You have already reported this user'
            
            # Insert fraud report
            fraud_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO fraud_list (id, user_id, reported_user_id, reason, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (fraud_id, reporter_id, reported_user_id, reason.strip()))
            
            # Check if we should auto-suspend the user (simple risk calculation)
            cursor.execute("""
                SELECT COUNT(*) as report_count 
                FROM fraud_list 
                WHERE reported_user_id COLLATE utf8mb4_unicode_ci = %s
            """, (reported_user_id,))
            total_reports = cursor.fetchone()['report_count']
            
            # Auto-suspend if user has 3 or more fraud reports
            if total_reports >= 3:
                # Check if users table has is_suspended column
                cursor.execute("SHOW COLUMNS FROM users LIKE 'is_suspended'")
                if cursor.fetchone():
                    cursor.execute("""
                        UPDATE users 
                        SET is_suspended = TRUE 
                        WHERE id COLLATE utf8mb4_unicode_ci = %s
                    """, (reported_user_id,))
                    current_app.logger.info(f"Auto-suspended user {reported_user_id} due to {total_reports} fraud reports")
            
            # Commit transaction
            conn.commit()
            
            success_message = f'Fraud report submitted successfully. Report ID: {fraud_id}'
            if total_reports >= 3:
                success_message += ' (User has been auto-suspended due to multiple reports)'
            
            current_app.logger.info(f"Fraud report created: {fraud_id} by {reporter_id} against {reported_user_id}")
            return True, success_message
            
    except Exception as e:
        if conn:
            conn.rollback()
        current_app.logger.error(f"Database error in add_fraud_report: {str(e)}")
        return False, f"Failed to process fraud report: {str(e)}"
    finally:
        if conn:
            conn.close()

def get_fraud_reports(limit=50, offset=0):
    """Get fraud reports from the database"""
    conn = None
    try:
        conn = current_app.get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    fl.id,
                    fl.user_id,
                    fl.reported_user_id,
                    fl.reason,
                    fl.created_at,
                    CONCAT(u1.first_name, ' ', u1.last_name) as reporter_name,
                    CONCAT(u2.first_name, ' ', u2.last_name) as reported_user_name
                FROM fraud_list fl
                LEFT JOIN users u1 ON fl.user_id = u1.id
                LEFT JOIN users u2 ON fl.reported_user_id = u2.id
                ORDER BY fl.created_at DESC
                LIMIT %s OFFSET %s
            ''', (limit, offset))
            reports = cursor.fetchall()
            return reports
    except Exception as e:
        current_app.logger.error(f"Error getting fraud reports: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_user_fraud_reports(user_id, limit=10):
    """Get fraud reports for a specific user"""
    conn = None
    try:
        conn = current_app.get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    fl.id,
                    fl.reported_user_id,
                    fl.reason,
                    fl.created_at,
                    CONCAT(u.first_name, ' ', u.last_name) as reported_user_name
                FROM fraud_list fl
                LEFT JOIN users u ON fl.reported_user_id = u.id
                WHERE fl.user_id COLLATE utf8mb4_unicode_ci = %s
                ORDER BY fl.created_at DESC
                LIMIT %s
            ''', (user_id, limit))
            reports = cursor.fetchall()
            return reports
    except Exception as e:
        current_app.logger.error(f"Error getting user fraud reports: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_fraud_stats():
    """Get fraud reporting statistics"""
    conn = None
    try:
        conn = current_app.get_db_connection()
        with conn.cursor() as cursor:
            # Total reports
            cursor.execute("SELECT COUNT(*) as total_reports FROM fraud_list")
            total_reports = cursor.fetchone()['total_reports']
            
            # Reports this month
            cursor.execute("""
                SELECT COUNT(*) as monthly_reports 
                FROM fraud_list 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
            """)
            monthly_reports = cursor.fetchone()['monthly_reports']
            
            # Most reported users
            cursor.execute("""
                SELECT 
                    fl.reported_user_id,
                    COUNT(*) as report_count,
                    CONCAT(u.first_name, ' ', u.last_name) as user_name
                FROM fraud_list fl
                LEFT JOIN users u ON fl.reported_user_id = u.id
                GROUP BY fl.reported_user_id
                ORDER BY report_count DESC
                LIMIT 5
            """)
            most_reported = cursor.fetchall()
            
            return {
                'total_reports': total_reports,
                'monthly_reports': monthly_reports,
                'most_reported_users': most_reported
            }
    except Exception as e:
        current_app.logger.error(f"Error getting fraud stats: {e}")
        return {
            'total_reports': 0,
            'monthly_reports': 0,
            'most_reported_users': []
        }
    finally:
        if conn:
            conn.close()
