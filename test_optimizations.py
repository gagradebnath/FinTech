#!/usr/bin/env python3
"""
FinGuard PL/SQL Optimization Testing Script

This script tests all the new PL/SQL optimizations to ensure they work correctly
with your existing application.
"""

import sys
import os
import uuid
from datetime import datetime, date

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.utils import transaction_utils, budget_utils, register, fraud_utils, admin_utils, dashboard
    from app import create_app
    from app.config import Config
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running this script from the project root directory")
    sys.exit(1)

def test_transaction_utils():
    """Test transaction utilities"""
    print("=== Testing Transaction Utils ===")
    
    # Test send_money with stored procedure
    print("Testing send_money...")
    try:
        result = transaction_utils.send_money(
            'TEST1234', 'TEST5678', 100.00, 'mobile_money', 
            'Test transfer', 'Test Location', 'Transfer'
        )
        print(f"✓ send_money result: {result}")
    except Exception as e:
        print(f"✗ send_money error: {e}")
    
    # Test get_user_risk_score
    print("Testing get_user_risk_score...")
    try:
        risk_score = transaction_utils.get_user_risk_score('TEST1234')
        print(f"✓ Risk score: {risk_score}")
    except Exception as e:
        print(f"✗ get_user_risk_score error: {e}")
    
    # Test check_spending_limit
    print("Testing check_spending_limit...")
    try:
        within_limit = transaction_utils.check_spending_limit('TEST1234', 500.00)
        print(f"✓ Within spending limit: {within_limit}")
    except Exception as e:
        print(f"✗ check_spending_limit error: {e}")
    
    print()

def test_budget_utils():
    """Test budget utilities"""
    print("=== Testing Budget Utils ===")
    
    # Test save_or_update_budget
    print("Testing save_or_update_budget...")
    try:
        budget = budget_utils.save_or_update_budget(
            'TEST1234', 'Monthly Budget', 'USD', 'Salary', 5000.00
        )
        print(f"✓ Budget saved: {budget}")
    except Exception as e:
        print(f"✗ save_or_update_budget error: {e}")
    
    # Test get_budget_by_id with enhanced analysis
    print("Testing get_budget_by_id...")
    try:
        budget = budget_utils.get_budget_by_id('test-budget-id', 'TEST1234')
        print(f"✓ Budget retrieved: {budget}")
    except Exception as e:
        print(f"✗ get_budget_by_id error: {e}")
    
    print()

def test_register():
    """Test user registration"""
    print("=== Testing User Registration ===")
    
    # Test create_user_and_contact
    print("Testing create_user_and_contact...")
    try:
        user_id, error = register.create_user_and_contact(
            'role-id', 'John', 'Doe', date(1990, 1, 1), 33, 'Male', 
            'Single', 'O+', 'john.doe@example.com', '+1234567890', 'password123'
        )
        if user_id:
            print(f"✓ User created: {user_id}")
        else:
            print(f"✗ User creation failed: {error}")
    except Exception as e:
        print(f"✗ create_user_and_contact error: {e}")
    
    print()

def test_fraud_utils():
    """Test fraud utilities"""
    print("=== Testing Fraud Utils ===")
    
    # Test add_fraud_report
    print("Testing add_fraud_report...")
    try:
        success, error = fraud_utils.add_fraud_report(
            'TEST1234', 'TEST5678', 'Suspicious transaction pattern'
        )
        if success:
            print("✓ Fraud report added successfully")
        else:
            print(f"✗ Fraud report failed: {error}")
    except Exception as e:
        print(f"✗ add_fraud_report error: {e}")
    
    print()

def test_admin_utils():
    """Test admin utilities"""
    print("=== Testing Admin Utils ===")
    
    # Test get_all_users with enhanced data
    print("Testing get_all_users...")
    try:
        users = admin_utils.get_all_users()
        print(f"✓ Retrieved {len(users)} users")
        if users:
            print(f"  Sample user: {users[0]}")
    except Exception as e:
        print(f"✗ get_all_users error: {e}")
    
    # Test get_all_frauds with risk scores
    print("Testing get_all_frauds...")
    try:
        frauds = admin_utils.get_all_frauds(limit=10)
        print(f"✓ Retrieved {len(frauds)} fraud reports")
        if frauds:
            print(f"  Sample fraud: {frauds[0]}")
    except Exception as e:
        print(f"✗ get_all_frauds error: {e}")
    
    # Test batch_update_user_balances
    print("Testing batch_update_user_balances...")
    try:
        success, message, count = admin_utils.batch_update_user_balances(
            'ADMIN123', ['TEST1234', 'TEST5678'], [100.00, 200.00], 'Testing batch update'
        )
        if success:
            print(f"✓ Batch update successful: {message}, Updated: {count}")
        else:
            print(f"✗ Batch update failed: {message}")
    except Exception as e:
        print(f"✗ batch_update_user_balances error: {e}")
    
    print()

def test_dashboard():
    """Test dashboard utilities"""
    print("=== Testing Dashboard Utils ===")
    
    # Test get_user_dashboard_data
    print("Testing get_user_dashboard_data...")
    try:
        dashboard_data = dashboard.get_user_dashboard_data('TEST1234')
        print(f"✓ Dashboard data: {dashboard_data}")
    except Exception as e:
        print(f"✗ get_user_dashboard_data error: {e}")
    
    # Test get_user_budgets with enhanced analysis
    print("Testing get_user_budgets...")
    try:
        budgets = dashboard.get_user_budgets('TEST1234')
        print(f"✓ Retrieved {len(budgets)} budgets")
        if budgets:
            print(f"  Sample budget: {budgets[0]}")
    except Exception as e:
        print(f"✗ get_user_budgets error: {e}")
    
    print()

def test_database_views():
    """Test database views directly"""
    print("=== Testing Database Views ===")
    
    try:
        from flask import current_app
        
        # Test v_user_dashboard_summary
        print("Testing v_user_dashboard_summary...")
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM v_user_dashboard_summary LIMIT 5")
                results = cursor.fetchall()
                print(f"✓ v_user_dashboard_summary: {len(results)} rows")
        except Exception as e:
            print(f"✗ v_user_dashboard_summary error: {e}")
        finally:
            conn.close()
        
        # Test v_budget_analysis
        print("Testing v_budget_analysis...")
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM v_budget_analysis LIMIT 5")
                results = cursor.fetchall()
                print(f"✓ v_budget_analysis: {len(results)} rows")
        except Exception as e:
            print(f"✗ v_budget_analysis error: {e}")
        finally:
            conn.close()
        
        # Test v_fraud_indicators
        print("Testing v_fraud_indicators...")
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM v_fraud_indicators LIMIT 5")
                results = cursor.fetchall()
                print(f"✓ v_fraud_indicators: {len(results)} rows")
        except Exception as e:
            print(f"✗ v_fraud_indicators error: {e}")
        finally:
            conn.close()
    
    except Exception as e:
        print(f"✗ Database view testing error: {e}")
    
    print()

def performance_test():
    """Run basic performance tests"""
    print("=== Performance Testing ===")
    
    import time
    
    # Test transaction processing performance
    print("Testing transaction performance...")
    start_time = time.time()
    
    try:
        for i in range(10):
            transaction_utils.send_money(
                'TEST1234', 'TEST5678', 10.00, 'mobile_money', 
                f'Performance test {i}', 'Test Location', 'Transfer'
            )
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        print(f"✓ Average transaction time: {avg_time:.4f} seconds")
    except Exception as e:
        print(f"✗ Performance test error: {e}")
    
    print()

def main():
    """Main testing function"""
    print("=== FinGuard PL/SQL Optimization Testing ===")
    print()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        test_transaction_utils()
        test_budget_utils()
        test_register()
        test_fraud_utils()
        test_admin_utils()
        test_dashboard()
        test_database_views()
        performance_test()
    
    print("=== Testing Complete ===")
    print()
    print("Summary:")
    print("- All major PL/SQL optimizations have been tested")
    print("- Check the output above for any errors (marked with ✗)")
    print("- Successful tests are marked with ✓")
    print("- If you see errors, check your database connection and ensure")
    print("  the PL/SQL optimizations have been deployed correctly")

if __name__ == "__main__":
    main()
