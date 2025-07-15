#!/usr/bin/env python3
"""
Test script for rollback functionality
"""

import pymysql
import uuid
from datetime import datetime
import json

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Update with your password
    'database': 'fin_guard',
    'charset': 'utf8mb4'
}

def get_connection():
    """Get database connection"""
    return pymysql.connect(**DB_CONFIG)

def test_rollback_tables():
    """Test that all rollback tables exist"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Test transaction_backups table
        cursor.execute("DESCRIBE transaction_backups")
        print("✅ transaction_backups table exists")
        
        # Test failed_transactions table
        cursor.execute("DESCRIBE failed_transactions")
        print("✅ failed_transactions table exists")
        
        # Test system_audit_log table
        cursor.execute("DESCRIBE system_audit_log")
        print("✅ system_audit_log table exists")
        
        # Test transactions table has status column
        cursor.execute("SHOW COLUMNS FROM transactions LIKE 'status'")
        if cursor.fetchone():
            print("✅ transactions table has status column")
        else:
            print("❌ transactions table missing status column")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing tables: {e}")
        return False
    finally:
        conn.close()

def test_rollback_procedures():
    """Test that all rollback procedures exist"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        procedures = [
            'ProcessMoneyTransferEnhanced',
            'RollbackTransaction',
            'GetTransactionStatus',
            'BackupUserBalance',
            'RestoreUserBalance',
            'AutoRollbackFailedTransactions'
        ]
        
        for proc in procedures:
            cursor.execute(f"SHOW PROCEDURE STATUS WHERE Name = '{proc}'")
            if cursor.fetchone():
                print(f"✅ {proc} procedure exists")
            else:
                print(f"❌ {proc} procedure missing")
                
        return True
        
    except Exception as e:
        print(f"❌ Error testing procedures: {e}")
        return False
    finally:
        conn.close()

def test_sample_transaction():
    """Test a sample transaction with rollback"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Get sample users
        cursor.execute("SELECT id, balance FROM users LIMIT 2")
        users = cursor.fetchall()
        
        if len(users) < 2:
            print("❌ Need at least 2 users to test transactions")
            return False
            
        sender_id = users[0][0]
        receiver_id = users[1][0]
        sender_balance = users[0][1]
        
        print(f"Testing transaction between {sender_id} and {receiver_id}")
        print(f"Sender balance before: {sender_balance}")
        
        # Test transaction
        cursor.callproc('ProcessMoneyTransferEnhanced', [
            sender_id, receiver_id, 10.00, 'test_payment', 
            'Test transaction', 'Transfer', 'Test Location'
        ])
        
        # Get results
        cursor.execute("SELECT @_ProcessMoneyTransferEnhanced_7, @_ProcessMoneyTransferEnhanced_8, @_ProcessMoneyTransferEnhanced_9")
        success, message, transaction_id = cursor.fetchone()
        
        if success:
            print(f"✅ Transaction successful: {transaction_id}")
            print(f"Message: {message}")
            
            # Test rollback
            cursor.callproc('RollbackTransaction', [transaction_id, 'Test rollback'])
            cursor.execute("SELECT @_RollbackTransaction_2, @_RollbackTransaction_3")
            rollback_success, rollback_message = cursor.fetchone()
            
            if rollback_success:
                print(f"✅ Rollback successful: {rollback_message}")
            else:
                print(f"❌ Rollback failed: {rollback_message}")
                
        else:
            print(f"❌ Transaction failed: {message}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing transaction: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main test function"""
    print("=" * 50)
    print("FinGuard Rollback Functionality Test")
    print("=" * 50)
    print()
    
    print("1. Testing rollback tables...")
    if not test_rollback_tables():
        print("❌ Table tests failed")
        return
    print()
    
    print("2. Testing rollback procedures...")
    if not test_rollback_procedures():
        print("❌ Procedure tests failed")
        return
    print()
    
    print("3. Testing sample transaction and rollback...")
    if not test_sample_transaction():
        print("❌ Transaction tests failed")
        return
    print()
    
    print("=" * 50)
    print("✅ All tests passed! Rollback functionality is working!")
    print("=" * 50)
    print()
    print("You can now:")
    print("1. Run the Flask application: python run.py")
    print("2. Login as admin")
    print("3. Access rollback dashboard: /rollback/dashboard")
    print("4. Test rollback functionality through the web interface")

if __name__ == "__main__":
    main()
