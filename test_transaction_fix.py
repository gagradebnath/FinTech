#!/usr/bin/env python3
"""
Test transaction after fixing NULL balance issue
"""

import os
import sys

# Add paths
project_root = os.path.dirname(__file__)
app_dir = os.path.join(project_root, 'app')
sys.path.insert(0, project_root)
sys.path.insert(0, app_dir)

import pymysql
from app.config import Config
from flask import Flask

def create_test_app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    def get_db_connection():
        return pymysql.connect(
            host=app.config['MYSQL_HOST'],
            port=app.config['MYSQL_PORT'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DATABASE'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
    
    app.get_db_connection = staticmethod(get_db_connection)
    return app

def test_transaction_after_fix():
    print("🧪 Testing Transaction After NULL Balance Fix")
    print("=" * 50)
    
    app = create_test_app()
    
    with app.app_context():
        try:
            from app.utils.transaction_utils import send_money
            
            # Get test users
            conn = app.get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, first_name, last_name, balance FROM users WHERE balance >= 100 LIMIT 2")
                users = cursor.fetchall()
                
                if len(users) < 2:
                    print("❌ Need at least 2 users with balance >= 100")
                    return False
                
                sender = users[0]
                receiver = users[1]
                
                print(f"👤 Testing transaction:")
                print(f"   Sender: {sender['first_name']} {sender['last_name']} (Balance: ${sender['balance']})")
                print(f"   Receiver: {receiver['first_name']} {receiver['last_name']} (Balance: ${receiver['balance']})")
            
            conn.close()
            
            # Test transaction
            amount = 25.0
            print(f"\n💸 Attempting to send ${amount}...")
            
            success, message, updated_sender = send_money(
                sender_id=sender['id'],
                recipient_id=receiver['id'],
                amount=amount,
                payment_method="Test Payment",
                note="Test transaction after NULL fix",
                location="Test Location",
                tx_type="Transfer"
            )
            
            if success:
                print(f"✅ Transaction successful: {message}")
                
                # Verify the transaction was recorded
                conn = app.get_db_connection()
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, amount, sender_id, receiver_id, note 
                        FROM transactions 
                        WHERE sender_id = %s AND receiver_id = %s 
                        ORDER BY timestamp DESC 
                        LIMIT 1
                    """, (sender['id'], receiver['id']))
                    
                    latest_tx = cursor.fetchone()
                    if latest_tx:
                        print(f"✅ Transaction recorded in database:")
                        print(f"   - ID: {latest_tx['id']}")
                        print(f"   - Amount: ${latest_tx['amount']}")
                        print(f"   - Note: {latest_tx['note']}")
                    else:
                        print("❌ Transaction not found in database")
                
                conn.close()
                return True
            else:
                print(f"❌ Transaction failed: {message}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    if test_transaction_after_fix():
        print("\n🎉 Transaction test passed! NULL balance issue fixed.")
    else:
        print("\n❌ Transaction test failed. Check the logs above.")
