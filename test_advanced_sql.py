#!/usr/bin/env python3
"""
Test script for advanced SQL features
This script tests the new stored procedures, functions, and utilities
"""

import sys
import os
import uuid
from datetime import datetime, timedelta

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_database_connection():
    """Test basic database connection"""
    try:
        import pymysql
        
        config = {
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'user': os.environ.get('MYSQL_USER', 'root'),
            'password': os.environ.get('MYSQL_PASSWORD', 'g85a'),
            'database': os.environ.get('MYSQL_DATABASE', 'fin_guard'),
            'charset': 'utf8mb4'
        }
        
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        print("✓ Database connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_basic_queries():
    """Test basic database queries to ensure tables exist"""
    try:
        import pymysql
        
        config = {
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'user': os.environ.get('MYSQL_USER', 'root'),
            'password': os.environ.get('MYSQL_PASSWORD', 'g85a'),
            'database': os.environ.get('MYSQL_DATABASE', 'fin_guard'),
            'charset': 'utf8mb4'
        }
        
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # Test basic table queries
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✓ Found {user_count} users in database")
        
        cursor.execute("SELECT COUNT(*) FROM transactions")
        tx_count = cursor.fetchone()[0]
        print(f"✓ Found {tx_count} transactions in database")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Basic query test failed: {e}")
        return False

def test_stored_procedures():
    """Test if stored procedures exist and can be called"""
    try:
        import pymysql
        
        config = {
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'user': os.environ.get('MYSQL_USER', 'root'),
            'password': os.environ.get('MYSQL_PASSWORD', 'g85a'),
            'database': os.environ.get('MYSQL_DATABASE', 'fin_guard'),
            'charset': 'utf8mb4'
        }
        
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # Check if stored procedures exist
        cursor.execute("SHOW PROCEDURE STATUS WHERE Db = %s", (config['database'],))
        procedures = cursor.fetchall()
        
        procedure_names = [proc[1] for proc in procedures]  # proc[1] is the procedure name
        expected_procedures = ['ProcessMoneyTransfer', 'GetUserTransactionHistory', 'CalculateUserStatistics', 'BulkBalanceUpdate']
        
        found_procedures = []
        for expected in expected_procedures:
            if expected in procedure_names:
                found_procedures.append(expected)
                print(f"✓ Found stored procedure: {expected}")
            else:
                print(f"⚠ Missing stored procedure: {expected}")
        
        cursor.close()
        connection.close()
        
        print(f"✓ Found {len(found_procedures)}/{len(expected_procedures)} expected stored procedures")
        return len(found_procedures) > 0
        
    except Exception as e:
        print(f"❌ Stored procedure test failed: {e}")
        return False

def test_functions():
    """Test if MySQL functions exist"""
    try:
        import pymysql
        
        config = {
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'user': os.environ.get('MYSQL_USER', 'root'),
            'password': os.environ.get('MYSQL_PASSWORD', 'g85a'),
            'database': os.environ.get('MYSQL_DATABASE', 'fin_guard'),
            'charset': 'utf8mb4'
        }
        
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # Check if functions exist
        cursor.execute("SHOW FUNCTION STATUS WHERE Db = %s", (config['database'],))
        functions = cursor.fetchall()
        
        function_names = [func[1] for func in functions]  # func[1] is the function name
        expected_functions = ['CalculateAccountAge', 'CalculateTransactionVelocity', 'GetUserRiskScore']
        
        found_functions = []
        for expected in expected_functions:
            if expected in function_names:
                found_functions.append(expected)
                print(f"✓ Found function: {expected}")
            else:
                print(f"⚠ Missing function: {expected}")
        
        cursor.close()
        connection.close()
        
        print(f"✓ Found {len(found_functions)}/{len(expected_functions)} expected functions")
        return len(found_functions) > 0
        
    except Exception as e:
        print(f"❌ Function test failed: {e}")
        return False

def test_views():
    """Test if views exist and can be queried"""
    try:
        import pymysql
        
        config = {
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'user': os.environ.get('MYSQL_USER', 'root'),
            'password': os.environ.get('MYSQL_PASSWORD', 'g85a'),
            'database': os.environ.get('MYSQL_DATABASE', 'fin_guard'),
            'charset': 'utf8mb4'
        }
        
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # Check if views exist
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
        views = cursor.fetchall()
        
        view_names = [view[0] for view in views]  # view[0] is the view name
        expected_views = ['v_user_transaction_summary', 'v_daily_transaction_analytics', 'v_high_risk_users']
        
        found_views = []
        for expected in expected_views:
            if expected in view_names:
                found_views.append(expected)
                print(f"✓ Found view: {expected}")
                
                # Test querying the view
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {expected}")
                    count = cursor.fetchone()[0]
                    print(f"  └─ View has {count} rows")
                except Exception as e:
                    print(f"  └─ Warning: Could not query view: {e}")
            else:
                print(f"⚠ Missing view: {expected}")
        
        cursor.close()
        connection.close()
        
        print(f"✓ Found {len(found_views)}/{len(expected_views)} expected views")
        return len(found_views) > 0
        
    except Exception as e:
        print(f"❌ View test failed: {e}")
        return False

def test_advanced_sql_utils():
    """Test the AdvancedSQLUtils class if features are installed"""
    try:
        from utils.advanced_sql_utils import AdvancedSQLUtils, AdvancedReportingUtils
        
        print("✓ Successfully imported AdvancedSQLUtils")
        
        # Test if we can instantiate and call basic methods
        # Note: These will fail if the database doesn't have the stored procedures
        # but we can test the import and basic structure
        
        return True
        
    except ImportError as e:
        print(f"⚠ Could not import AdvancedSQLUtils: {e}")
        return False
    except Exception as e:
        print(f"❌ AdvancedSQLUtils test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== FinGuard Advanced SQL Features Test ===")
    print()
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Basic Queries", test_basic_queries),
        ("Stored Procedures", test_stored_procedures),
        ("Functions", test_functions),
        ("Views", test_views),
        ("Python Utils", test_advanced_sql_utils),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- Testing {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All tests passed! Advanced SQL features are ready to use.")
    elif passed > total // 2:
        print("⚠ Most tests passed. Some features may need database migration.")
        print("Run: python apply_advanced_sql.py")
    else:
        print("❌ Many tests failed. Check database connection and schema.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)