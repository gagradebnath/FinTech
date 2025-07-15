#!/usr/bin/env python3
"""
FinGuard PL/SQL Optimization Deployment Script

This script will help you deploy all the PL/SQL optimizations to your database
and test the new functionality.
"""

import pymysql
import sys
import os

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Update this
    'database': 'fin_guard',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    """Get database connection"""
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database connection failed: {e}")
        sys.exit(1)

def execute_sql_file(filepath):
    """Execute SQL file"""
    print(f"Executing SQL file: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found")
        return False
    
    conn = get_db_connection()
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split by delimiter and execute each statement
        statements = sql_content.split('//')[:-1]  # Remove last empty element
        
        with conn.cursor() as cursor:
            for i, statement in enumerate(statements):
                statement = statement.strip()
                if statement and not statement.startswith('--') and not statement.startswith('DELIMITER'):
                    try:
                        cursor.execute(statement)
                        conn.commit()
                        print(f"  ✓ Statement {i+1} executed successfully")
                    except Exception as e:
                        print(f"  ✗ Error in statement {i+1}: {e}")
                        return False
        
        print(f"✓ {filepath} executed successfully")
        return True
        
    except Exception as e:
        print(f"Error executing {filepath}: {e}")
        return False
    finally:
        conn.close()

def test_stored_procedure(proc_name, params):
    """Test a stored procedure"""
    print(f"Testing stored procedure: {proc_name}")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc(proc_name, params)
            result = cursor.fetchone()
            print(f"  ✓ {proc_name} executed successfully")
            return result
    except Exception as e:
        print(f"  ✗ Error testing {proc_name}: {e}")
        return None
    finally:
        conn.close()

def test_function(func_name, params):
    """Test a MySQL function"""
    print(f"Testing function: {func_name}")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            param_str = ', '.join(['%s'] * len(params))
            cursor.execute(f"SELECT {func_name}({param_str}) as result", params)
            result = cursor.fetchone()
            print(f"  ✓ {func_name} executed successfully")
            return result
    except Exception as e:
        print(f"  ✗ Error testing {func_name}: {e}")
        return None
    finally:
        conn.close()

def test_view(view_name, limit=5):
    """Test a view"""
    print(f"Testing view: {view_name}")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {view_name} LIMIT %s", (limit,))
            result = cursor.fetchall()
            print(f"  ✓ {view_name} queried successfully - {len(result)} rows returned")
            return result
    except Exception as e:
        print(f"  ✗ Error testing {view_name}: {e}")
        return None
    finally:
        conn.close()

def main():
    """Main deployment function"""
    print("=== FinGuard PL/SQL Optimization Deployment ===")
    print()
    
    # Step 1: Update database schema
    print("Step 1: Updating database schema...")
    if execute_sql_file('schema_updates.sql'):
        print("✓ Schema updated successfully")
    else:
        print("✗ Schema update failed")
        return
    
    print()
    
    # Step 2: Deploy PL/SQL optimizations
    print("Step 2: Deploying PL/SQL optimizations...")
    if execute_sql_file('PL_SQL_Optimizations.sql'):
        print("✓ PL/SQL optimizations deployed successfully")
    else:
        print("✗ PL/SQL optimization deployment failed")
        return
    
    print()
    
    # Step 3: Test stored procedures
    print("Step 3: Testing stored procedures...")
    
    # Test RegisterUser (need to create a test user first)
    test_stored_procedure('RegisterUser', [
        'user', 'Test', 'User', '1990-01-01', 33, 'Male', 'Single', 'O+',
        'test@example.com', '+1234567890', 'hashed_password',
        None, None, None
    ])
    
    # Test GetUserDashboardData (use a test user ID)
    test_stored_procedure('GetUserDashboardData', [
        'TEST1234', None, None, None, None, None
    ])
    
    print()
    
    # Step 4: Test functions
    print("Step 4: Testing functions...")
    
    # Test GetUserRiskScore
    test_function('GetUserRiskScore', ['TEST1234'])
    
    # Test CalculateSpendingPattern
    test_function('CalculateSpendingPattern', ['TEST1234'])
    
    # Test IsWithinSpendingLimit
    test_function('IsWithinSpendingLimit', ['TEST1234', 100.00])
    
    print()
    
    # Step 5: Test views
    print("Step 5: Testing views...")
    
    test_view('v_user_dashboard_summary')
    test_view('v_budget_analysis')
    test_view('v_fraud_indicators')
    
    print()
    print("=== Deployment Complete ===")
    print()
    print("Next steps:")
    print("1. Test your Python application with the new optimized queries")
    print("2. Monitor database performance")
    print("3. Check application logs for any errors")
    print("4. Run your existing test suite to ensure compatibility")
    print()
    print("The following Python files have been updated:")
    print("- app/utils/transaction_utils.py")
    print("- app/utils/budget_utils.py")
    print("- app/utils/register.py")
    print("- app/utils/fraud_utils.py")
    print("- app/utils/admin_utils.py")
    print("- app/utils/dashboard.py")

if __name__ == "__main__":
    # Update DB_CONFIG with your actual database credentials
    print("Please update the DB_CONFIG in this script with your database credentials")
    print("Then run this script to deploy the optimizations")
    
    # Uncomment the next line after updating DB_CONFIG
    # main()
