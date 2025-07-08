#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath('.'))

import pymysql
from app import create_app
from app.utils.transaction_utils import send_money, get_user_by_id

def test_null_balance_fix():
    """Test that NULL balance handling is working correctly"""
    print("Testing NULL balance handling...")
    
    # First, create a user with NULL balance to test with
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='g85a',
            database='fin_guard',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        # Create test users with NULL balance
        test_user_id = 'test_null_user'
        test_user_id2 = 'test_null_user2'
        
        # Insert test users with NULL balance
        cursor.execute('''
            INSERT IGNORE INTO users (id, first_name, last_name, email, phone, password, balance) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (test_user_id, 'Test', 'User1', 'test1@test.com', '1234567890', 'password', None))
        
        cursor.execute('''
            INSERT IGNORE INTO users (id, first_name, last_name, email, phone, password, balance) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (test_user_id2, 'Test', 'User2', 'test2@test.com', '1234567891', 'password', None))
        
        conn.commit()
        
        # Verify they have NULL balance
        cursor.execute('SELECT id, balance FROM users WHERE id IN (%s, %s)', (test_user_id, test_user_id2))
        test_users = cursor.fetchall()
        print(f"Test users created: {test_users}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error setting up test users: {e}")
        return
    
    # Now test the transaction with Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Test 1: Check that get_user_by_id works with NULL balance
            user1 = get_user_by_id(test_user_id)
            user2 = get_user_by_id(test_user_id2)
            
            print(f"User 1: {user1['id']} - Balance: {user1['balance']} (type: {type(user1['balance'])})")
            print(f"User 2: {user2['id']} - Balance: {user2['balance']} (type: {type(user2['balance'])})")
            
            # Test 2: Give user1 some money so they can send to user2
            conn = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='g85a',
                database='fin_guard',
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET balance = 100.0 WHERE id = %s', (test_user_id,))
            conn.commit()
            conn.close()
            
            # Test 3: Try sending money from user1 (with balance) to user2 (with NULL balance)
            print(f"\nTesting transaction from {test_user_id} to {test_user_id2}...")
            
            success, message, updated_user = send_money(
                test_user_id,
                test_user_id2, 
                10.0,
                "Bank Transfer",
                "Test transaction with NULL balance", 
                "Test Location",
                "Transfer"
            )
            
            if success:
                print(f"✅ Transaction successful: {message}")
                print(f"Updated sender balance: {updated_user['balance'] if updated_user else 'None'}")
                
                # Check final balances
                user1_final = get_user_by_id(test_user_id)
                user2_final = get_user_by_id(test_user_id2)
                print(f"Final User 1 balance: {user1_final['balance']}")
                print(f"Final User 2 balance: {user2_final['balance']}")
                
            else:
                print(f"❌ Transaction failed: {message}")
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
        
        # Clean up test users
        try:
            conn = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='g85a',
                database='fin_guard',
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id IN (%s, %s)', (test_user_id, test_user_id2))
            cursor.execute('DELETE FROM transactions WHERE sender_id IN (%s, %s) OR receiver_id IN (%s, %s)', 
                          (test_user_id, test_user_id2, test_user_id, test_user_id2))
            conn.commit()
            conn.close()
            print("\n🧹 Test users cleaned up")
        except Exception as e:
            print(f"Warning: Could not clean up test users: {e}")

if __name__ == "__main__":
    test_null_balance_fix()
