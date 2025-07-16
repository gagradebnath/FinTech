# Utility functions for admin operations (moved from admin.py)
from flask import current_app
import uuid
from datetime import datetime
from .advanced_sql_utils import AdvancedSQLUtils, AdvancedReportingUtils

def get_role_name_by_id(role_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT name FROM roles WHERE id = %s', (role_id,))
            row = cursor.fetchone()
        return row['name'] if row else None
    finally:
        conn.close()

def get_all_users():
    """Get all users using optimized view"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT u.id, u.first_name, u.last_name, u.balance, u.risk_score, u.spending_pattern 
                FROM v_user_dashboard_summary u
                ORDER BY u.last_name, u.first_name
            ''')
            users = cursor.fetchall()
        return users
    except Exception as e:
        print(f"Error getting users: {e}")
        # Fallback to original query
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT u.id, u.first_name, u.last_name, u.balance FROM users u')
                users = cursor.fetchall()
            return users
        except Exception as fallback_error:
            print(f"Fallback query also failed: {fallback_error}")
            return []
    finally:
        conn.close()

def get_agents():
    """Get all agents using optimized view"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT u.id, u.first_name, u.last_name, u.balance, u.risk_score
                FROM v_user_dashboard_summary u
                JOIN users ur ON u.id = ur.id
                JOIN roles r ON ur.role_id = r.id 
                WHERE LOWER(r.name) = "agent"
                ORDER BY u.last_name, u.first_name
            ''')
            agents = cursor.fetchall()
        return agents
    except Exception as e:
        print(f"Error getting agents: {e}")
        # Fallback to original query
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT u.id, u.first_name, u.last_name, u.balance FROM users u JOIN roles r ON u.role_id = r.id WHERE LOWER(r.name) = "agent"')
                agents = cursor.fetchall()
            return agents
        except Exception as fallback_error:
            print(f"Fallback query also failed: {fallback_error}")
            return []
    finally:
        conn.close()

def get_all_transactions(limit=100):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''SELECT t.*, s.first_name as sender_first, s.last_name as sender_last, r.first_name as receiver_first, r.last_name as receiver_last FROM transactions t
                LEFT JOIN users s ON t.sender_id = s.id
                LEFT JOIN users r ON t.receiver_id = r.id
                ORDER BY t.timestamp DESC LIMIT %s''', (limit,))
            txs = cursor.fetchall()
        return txs
    finally:
        conn.close()

def get_all_frauds(limit=100):
    """Get all fraud reports with risk indicators"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT f.*, 
                       u1.first_name as reporter_first, u1.last_name as reporter_last, 
                       u2.first_name as reported_first, u2.last_name as reported_last,
                       f.created_at
                FROM fraud_list f
                LEFT JOIN users u1 ON f.user_id COLLATE utf8mb4_unicode_ci = u1.id COLLATE utf8mb4_unicode_ci
                LEFT JOIN users u2 ON f.reported_user_id COLLATE utf8mb4_unicode_ci = u2.id COLLATE utf8mb4_unicode_ci
                ORDER BY f.created_at DESC
                LIMIT %s
            ''', (limit,))
            frauds = cursor.fetchall()
        return frauds
    finally:
        conn.close()

def batch_update_user_balances(admin_id, user_ids, amounts, reason):
    """Batch update user balances using stored procedure"""
    conn = current_app.get_db_connection()
    try:
        # Convert lists to comma-separated strings
        user_ids_str = ','.join(user_ids)
        amounts_str = ','.join(str(amount) for amount in amounts)
        
        with conn.cursor() as cursor:
            cursor.callproc('AdminBatchBalanceUpdate', [
                admin_id, user_ids_str, amounts_str, reason,
                None, None, None  # OUT parameters
            ])
            
            # Fetch the OUT parameters
            cursor.execute("SELECT @_AdminBatchBalanceUpdate_4 as success, @_AdminBatchBalanceUpdate_5 as message, @_AdminBatchBalanceUpdate_6 as updated_count")
            result = cursor.fetchone()
            
            if result and result['success']:
                return True, result['message'], result['updated_count']
            else:
                return False, result['message'] if result else 'Unknown error', 0
                
    except Exception as e:
        return False, str(e), 0
    finally:
        conn.close()

def get_admin_logs(limit=100):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''SELECT l.*, a.first_name as admin_first, a.last_name as admin_last FROM admin_logs l LEFT JOIN users a ON l.admin_id = a.id ORDER BY l.timestamp DESC LIMIT %s''', (limit,))
            logs = cursor.fetchall()
        return logs
    finally:
        conn.close()

def update_user_balance(user_id, amount):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE users SET balance = balance + %s WHERE id = %s', (amount, user_id))
        conn.commit()
    finally:
        conn.close()

def insert_transaction_admin(tx_id, amount, sender_id, receiver_id, note, tx_type):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, %s)''',
                (tx_id, amount, 'admin_add', sender_id, receiver_id, note, tx_type, None))
        conn.commit()
    finally:
        conn.close()

def insert_admin_log(log_id, admin_id, ip_address, details):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details) VALUES (%s, %s, %s, %s, %s)',
                (log_id, admin_id, ip_address, datetime.now(), details))
        conn.commit()
    finally:
        conn.close()

def insert_fraud_list(fraud_id, user_id, reported_user_id, reason):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO fraud_list (id, user_id, reported_user_id, reason) VALUES (%s, %s, %s, %s)',
                (fraud_id, user_id, reported_user_id, reason))
        conn.commit()
    finally:
        conn.close()

def delete_fraud_list(reported_user_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM fraud_list WHERE reported_user_id = %s', (reported_user_id,))
        conn.commit()
    finally:
        conn.close()

def update_user_role(user_id, new_role_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE users SET role_id = %s WHERE id = %s', (new_role_id, user_id))
        conn.commit()
    finally:
        conn.close()

def get_role_id_by_name(role_name):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id FROM roles WHERE LOWER(name) = %s', (role_name.lower(),))
            row = cursor.fetchone()
        return row['id'] if row else None
    finally:
        conn.close()

# ============================================================================
# ENHANCED ADMIN FUNCTIONS USING ADVANCED SQL
# ============================================================================

def admin_bulk_balance_update(admin_id, user_id, amount, reason):
    """Admin bulk balance update using stored procedure"""
    try:
        return AdvancedSQLUtils.bulk_balance_update(admin_id, user_id, amount, reason)
    except Exception as e:
        print(f"Error in bulk balance update: {e}")
        return False, f"Failed to update balance: {str(e)}"

def get_comprehensive_user_stats(user_id):
    """Get comprehensive user statistics using advanced SQL"""
    try:
        stats = AdvancedSQLUtils.calculate_user_statistics(user_id)
        risk_score = AdvancedSQLUtils.get_user_risk_score(user_id)
        account_age = AdvancedSQLUtils.calculate_account_age(user_id)
        velocity = AdvancedSQLUtils.calculate_transaction_velocity(user_id, 30)
        
        stats.update({
            'risk_score': risk_score,
            'account_age_days': account_age,
            'monthly_velocity': velocity
        })
        return stats
    except Exception as e:
        print(f"Error getting comprehensive stats: {e}")
        return {}

def get_admin_dashboard_data():
    """Get comprehensive dashboard data for admin using advanced SQL"""
    try:
        return {
            'user_summary': AdvancedReportingUtils.get_user_transaction_summary()[:10],  # Top 10 users
            'daily_analytics': AdvancedReportingUtils.get_daily_analytics()[:7],  # Last 7 days
            'high_risk_users': AdvancedReportingUtils.get_high_risk_users()[:5],  # Top 5 risky users
            'monthly_report': AdvancedReportingUtils.get_monthly_transaction_report()[:6],  # Last 6 months
            'fraud_insights': AdvancedReportingUtils.get_fraud_detection_insights()
        }
    except Exception as e:
        print(f"Error getting dashboard data: {e}")
        return {}

def get_user_detailed_analysis(user_id):
    """Get detailed user analysis using advanced SQL"""
    try:
        return {
            'statistics': AdvancedSQLUtils.calculate_user_statistics(user_id),
            'risk_score': AdvancedSQLUtils.get_user_risk_score(user_id),
            'account_age': AdvancedSQLUtils.calculate_account_age(user_id),
            'transaction_velocity': AdvancedSQLUtils.calculate_transaction_velocity(user_id, 30),
            'pattern_analysis': AdvancedReportingUtils.get_transaction_pattern_analysis(user_id),
            'transaction_history': AdvancedSQLUtils.get_user_transaction_history(user_id, 20, 0)
        }
    except Exception as e:
        print(f"Error getting user analysis: {e}")
        return {}

def get_fraud_monitoring_report():
    """Get fraud monitoring report using advanced SQL"""
    try:
        fraud_insights = AdvancedReportingUtils.get_fraud_detection_insights()
        high_risk_users = AdvancedReportingUtils.get_high_risk_users()
        
        return {
            'insights': fraud_insights,
            'high_risk_users': high_risk_users,
            'summary': {
                'total_high_risk': len(high_risk_users),
                'avg_risk_score': sum(user.get('risk_score', 0) for user in high_risk_users) / max(len(high_risk_users), 1)
            }
        }
    except Exception as e:
        print(f"Error getting fraud monitoring report: {e}")
        return {}

def search_transactions_advanced(filters=None):
    """Advanced transaction search with complex queries"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            base_query = """
                SELECT t.*, 
                       s.first_name as sender_first, s.last_name as sender_last,
                       r.first_name as receiver_first, r.last_name as receiver_last,
                       GetUserRiskScore(t.sender_id) as sender_risk,
                       GetUserRiskScore(t.receiver_id) as receiver_risk
                FROM transactions t
                LEFT JOIN users s ON t.sender_id = s.id
                LEFT JOIN users r ON t.receiver_id = r.id
            """
            
            where_conditions = []
            params = []
            
            if filters:
                if filters.get('min_amount'):
                    where_conditions.append("t.amount >= %s")
                    params.append(filters['min_amount'])
                
                if filters.get('max_amount'):
                    where_conditions.append("t.amount <= %s")
                    params.append(filters['max_amount'])
                
                if filters.get('start_date'):
                    where_conditions.append("t.timestamp >= %s")
                    params.append(filters['start_date'])
                
                if filters.get('end_date'):
                    where_conditions.append("t.timestamp <= %s")
                    params.append(filters['end_date'])
                
                if filters.get('transaction_type'):
                    where_conditions.append("t.type = %s")
                    params.append(filters['transaction_type'])
                
                if filters.get('high_risk_only'):
                    where_conditions.append("(GetUserRiskScore(t.sender_id) > 50 OR GetUserRiskScore(t.receiver_id) > 50)")
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            base_query += " ORDER BY t.timestamp DESC LIMIT %s"
            params.append(filters.get('limit', 100) if filters else 100)
            
            cursor.execute(base_query, params)
            return list(cursor.fetchall())
    except Exception as e:
        print(f"Error in advanced transaction search: {e}")
        return []
    finally:
        conn.close()
