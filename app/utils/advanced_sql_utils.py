# Advanced SQL utilities using stored procedures, functions and complex queries
from flask import current_app
import uuid
from typing import Tuple, Optional, Dict, List


class AdvancedSQLUtils:
    """Utility class for advanced SQL operations using stored procedures and functions"""
    
    @staticmethod
    def process_money_transfer(sender_id: str, receiver_id: str, amount: float, 
                             payment_method: str, note: str, tx_type: str, 
                             location: str) -> Tuple[bool, str, Optional[str]]:
        """
        Process money transfer using stored procedure with enhanced validation
        Returns: (success, message, transaction_id)
        """
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Call stored procedure
                cursor.callproc('ProcessMoneyTransfer', [
                    sender_id, receiver_id, amount, payment_method, 
                    note, tx_type, location, None, None, None
                ])
                
                # Fetch the OUT parameters
                cursor.execute("SELECT @_ProcessMoneyTransfer_7, @_ProcessMoneyTransfer_8, @_ProcessMoneyTransfer_9")
                result = cursor.fetchone()
                
                if result:
                    success = bool(result['@_ProcessMoneyTransfer_7'])
                    message = result['@_ProcessMoneyTransfer_8']
                    transaction_id = result['@_ProcessMoneyTransfer_9']
                    return success, message, transaction_id
                else:
                    return False, 'Failed to get procedure result', None
                    
        except Exception as e:
            conn.rollback()
            return False, f'Database error: {str(e)}', None
        finally:
            conn.close()
    
    @staticmethod
    def get_user_transaction_history(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get user transaction history with analytics using stored procedure"""
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.callproc('GetUserTransactionHistory', [user_id, limit, offset])
                transactions = cursor.fetchall()
                return list(transactions) if transactions else []
        except Exception as e:
            print(f"Error fetching transaction history: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def calculate_user_statistics(user_id: str) -> Dict:
        """Calculate comprehensive user statistics using stored procedure"""
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.callproc('CalculateUserStatistics', [user_id, None, None, None, None, None])
                
                # Fetch the OUT parameters
                cursor.execute("""
                    SELECT @_CalculateUserStatistics_1 as total_sent,
                           @_CalculateUserStatistics_2 as total_received,
                           @_CalculateUserStatistics_3 as transaction_count,
                           @_CalculateUserStatistics_4 as avg_transaction,
                           @_CalculateUserStatistics_5 as last_transaction_date
                """)
                result = cursor.fetchone()
                
                if result:
                    return {
                        'total_sent': float(result['total_sent'] or 0),
                        'total_received': float(result['total_received'] or 0),
                        'transaction_count': int(result['transaction_count'] or 0),
                        'avg_transaction': float(result['avg_transaction'] or 0),
                        'last_transaction_date': result['last_transaction_date']
                    }
                else:
                    return {
                        'total_sent': 0.0,
                        'total_received': 0.0,
                        'transaction_count': 0,
                        'avg_transaction': 0.0,
                        'last_transaction_date': None
                    }
        except Exception as e:
            print(f"Error calculating user statistics: {e}")
            return {
                'total_sent': 0.0,
                'total_received': 0.0,
                'transaction_count': 0,
                'avg_transaction': 0.0,
                'last_transaction_date': None
            }
        finally:
            conn.close()
    
    @staticmethod
    def bulk_balance_update(admin_id: str, user_id: str, amount: float, reason: str) -> Tuple[bool, str]:
        """Perform bulk balance update using stored procedure"""
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.callproc('BulkBalanceUpdate', [admin_id, user_id, str(amount), reason, None, None])
                
                # Fetch the OUT parameters
                cursor.execute("SELECT @_BulkBalanceUpdate_4, @_BulkBalanceUpdate_5")
                result = cursor.fetchone()
                
                if result:
                    success = bool(result['@_BulkBalanceUpdate_4'])
                    message = result['@_BulkBalanceUpdate_5']
                    return success, message
                else:
                    return False, 'Failed to get procedure result'
        except Exception as e:
            conn.rollback()
            return False, f'Database error: {str(e)}'
        finally:
            conn.close()
    
    @staticmethod
    def get_user_risk_score(user_id: str) -> float:
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
    
    @staticmethod
    def calculate_account_age(user_id: str) -> int:
        """Calculate account age in days using MySQL function"""
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT CalculateAccountAge(%s) as age_days", (user_id,))
                result = cursor.fetchone()
                return int(result['age_days']) if result and result['age_days'] else 0
        except Exception as e:
            print(f"Error calculating account age: {e}")
            return 0
        finally:
            conn.close()
    
    @staticmethod
    def calculate_transaction_velocity(user_id: str, days: int = 30) -> float:
        """Calculate transaction velocity using MySQL function"""
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT CalculateTransactionVelocity(%s, %s) as velocity", (user_id, days))
                result = cursor.fetchone()
                return float(result['velocity']) if result and result['velocity'] else 0.0
        except Exception as e:
            print(f"Error calculating transaction velocity: {e}")
            return 0.0
        finally:
            conn.close()


class AdvancedReportingUtils:
    """Utility class for complex reporting queries"""
    
    @staticmethod
    def get_user_transaction_summary() -> List[Dict]:
        """Get user transaction summary using view"""
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM v_user_transaction_summary ORDER BY total_sent + total_received DESC")
                return list(cursor.fetchall())
        except Exception as e:
            print(f"Error getting transaction summary: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_daily_analytics() -> List[Dict]:
        """Get daily transaction analytics using view"""
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM v_daily_transaction_analytics LIMIT 30")
                return list(cursor.fetchall())
        except Exception as e:
            print(f"Error getting daily analytics: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_high_risk_users() -> List[Dict]:
        """Get high risk users using view"""
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM v_high_risk_users LIMIT 100")
                return list(cursor.fetchall())
        except Exception as e:
            print(f"Error getting high risk users: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_monthly_transaction_report() -> List[Dict]:
        """Get monthly transaction report with running totals"""
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                WITH monthly_data AS (
                    SELECT 
                        YEAR(timestamp) as year,
                        MONTH(timestamp) as month,
                        COUNT(*) as transaction_count,
                        SUM(amount) as total_volume,
                        AVG(amount) as avg_amount
                    FROM transactions
                    GROUP BY YEAR(timestamp), MONTH(timestamp)
                ),
                running_totals AS (
                    SELECT 
                        year,
                        month,
                        transaction_count,
                        total_volume,
                        avg_amount,
                        SUM(transaction_count) OVER (ORDER BY year, month) as cumulative_transactions,
                        SUM(total_volume) OVER (ORDER BY year, month) as cumulative_volume
                    FROM monthly_data
                )
                SELECT * FROM running_totals
                ORDER BY year DESC, month DESC
                LIMIT 12
                """
                cursor.execute(query)
                return list(cursor.fetchall())
        except Exception as e:
            print(f"Error getting monthly report: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_transaction_pattern_analysis(user_id: str) -> Dict:
        """Advanced transaction pattern analysis for a user"""
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Complex query with multiple subqueries and analytics
                query = """
                SELECT 
                    -- Basic stats
                    COUNT(*) as total_transactions,
                    AVG(amount) as avg_amount,
                    STDDEV(amount) as amount_stddev,
                    
                    -- Time-based patterns
                    COUNT(CASE WHEN HOUR(timestamp) BETWEEN 9 AND 17 THEN 1 END) as business_hours_txs,
                    COUNT(CASE WHEN DAYOFWEEK(timestamp) IN (1,7) THEN 1 END) as weekend_txs,
                    
                    -- Amount patterns
                    COUNT(CASE WHEN amount < 100 THEN 1 END) as small_txs,
                    COUNT(CASE WHEN amount BETWEEN 100 AND 1000 THEN 1 END) as medium_txs,
                    COUNT(CASE WHEN amount > 1000 THEN 1 END) as large_txs,
                    
                    -- Recent activity
                    COUNT(CASE WHEN timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) as recent_week_txs,
                    COUNT(CASE WHEN timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) as recent_month_txs,
                    
                    -- Location diversity
                    COUNT(DISTINCT location) as unique_locations,
                    
                    -- Payment method diversity
                    COUNT(DISTINCT payment_method) as unique_payment_methods,
                    
                    -- Counterparty analysis
                    COUNT(DISTINCT 
                        CASE WHEN sender_id = %s THEN receiver_id 
                             WHEN receiver_id = %s THEN sender_id 
                        END
                    ) as unique_counterparties
                FROM transactions
                WHERE sender_id = %s OR receiver_id = %s
                """
                cursor.execute(query, (user_id, user_id, user_id, user_id))
                result = cursor.fetchone()
                
                if result:
                    return dict(result)
                else:
                    return {}
        except Exception as e:
            print(f"Error getting transaction pattern analysis: {e}")
            return {}
        finally:
            conn.close()
    
    @staticmethod
    def get_fraud_detection_insights() -> Dict:
        """Get insights for fraud detection using complex queries"""
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Multiple complex queries for fraud detection
                
                # 1. Users with suspicious velocity
                cursor.execute("""
                    SELECT COUNT(*) as high_velocity_users
                    FROM (
                        SELECT sender_id,
                               COUNT(*) as tx_count,
                               COUNT(*) / GREATEST(DATEDIFF(MAX(timestamp), MIN(timestamp)), 1) as daily_velocity
                        FROM transactions 
                        WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                        GROUP BY sender_id
                        HAVING daily_velocity > 5
                    ) high_vel
                """)
                high_velocity = cursor.fetchone()['high_velocity_users']
                
                # 2. Round amount transactions (potential laundering)
                cursor.execute("""
                    SELECT COUNT(*) as round_amount_txs
                    FROM transactions 
                    WHERE amount = ROUND(amount, 0) 
                    AND amount >= 1000
                    AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                """)
                round_amounts = cursor.fetchone()['round_amount_txs']
                
                # 3. Unusual time patterns
                cursor.execute("""
                    SELECT COUNT(*) as off_hours_txs
                    FROM transactions 
                    WHERE (HOUR(timestamp) < 6 OR HOUR(timestamp) > 23)
                    AND amount > 500
                    AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                """)
                off_hours = cursor.fetchone()['off_hours_txs']
                
                # 4. Rapid sequence transactions
                cursor.execute("""
                    SELECT COUNT(*) as rapid_sequences
                    FROM (
                        SELECT sender_id, 
                               LAG(timestamp) OVER (PARTITION BY sender_id ORDER BY timestamp) as prev_time,
                               timestamp
                        FROM transactions
                        WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    ) t
                    WHERE TIMESTAMPDIFF(MINUTE, prev_time, timestamp) < 2
                """)
                rapid_sequences = cursor.fetchone()['rapid_sequences']
                
                return {
                    'high_velocity_users': high_velocity,
                    'round_amount_transactions': round_amounts,
                    'off_hours_transactions': off_hours,
                    'rapid_sequence_transactions': rapid_sequences
                }
                
        except Exception as e:
            print(f"Error getting fraud insights: {e}")
            return {}
        finally:
            conn.close()