#!/usr/bin/env python3
"""
Transaction Test with Blockchain Integration
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

def test_transaction_with_blockchain():
    print("🧪 Testing Transaction with Full Blockchain Integration")
    print("=" * 60)
    
    app = create_test_app()
    
    with app.app_context():
        try:
            # Import transaction utilities within app context
            from app.utils.transaction_utils import send_money
            from app.utils.hybrid_blockchain import hybrid_blockchain
            
            # Get test users
            conn = app.get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, first_name, last_name, balance FROM users WHERE balance > 100 LIMIT 2")
                users = cursor.fetchall()
                
                if len(users) < 2:
                    print("❌ Need at least 2 users with balance > 100")
                    return False
                
                sender = users[0]
                receiver = users[1]
                
                print(f"👤 Sender: {sender['first_name']} {sender['last_name']} (Balance: ${sender['balance']})")
                print(f"👤 Receiver: {receiver['first_name']} {receiver['last_name']} (Balance: ${receiver['balance']})")
                
                # Record initial balances
                initial_sender_balance = float(sender['balance'])
                initial_receiver_balance = float(receiver['balance'])
                
                # Get initial blockchain counts
                cursor.execute("SELECT COUNT(*) as count FROM transactions")
                initial_tx_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM blockchain_transactions") 
                initial_bt_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM blockchain")
                initial_b_count = cursor.fetchone()['count']
                
                print(f"\n📊 Initial State:")
                print(f"   - Transactions: {initial_tx_count}")
                print(f"   - Blockchain Transactions: {initial_bt_count}")
                print(f"   - Blockchain Blocks: {initial_b_count}")
            
            conn.close()
            
            # Perform transaction
            amount = 50.0
            print(f"\n💸 Sending ${amount} from {sender['first_name']} to {receiver['first_name']}...")
            
            success, message, updated_sender = send_money(
                sender_id=sender['id'],
                recipient_id=receiver['id'],
                amount=amount,
                payment_method="Credit Card",
                note="Test blockchain transaction",
                location="Test Location",
                tx_type="Transfer"
            )
            
            if success:
                print(f"✅ Transaction successful: {message}")
                
                # Check final state
                conn = app.get_db_connection()
                with conn.cursor() as cursor:
                    # Check updated balances
                    cursor.execute("SELECT balance FROM users WHERE id = %s", (sender['id'],))
                    final_sender_balance = float(cursor.fetchone()['balance'])
                    
                    cursor.execute("SELECT balance FROM users WHERE id = %s", (receiver['id'],))
                    final_receiver_balance = float(cursor.fetchone()['balance'])
                    
                    # Check transaction counts
                    cursor.execute("SELECT COUNT(*) as count FROM transactions")
                    final_tx_count = cursor.fetchone()['count']
                    
                    cursor.execute("SELECT COUNT(*) as count FROM blockchain_transactions")
                    final_bt_count = cursor.fetchone()['count']
                    
                    cursor.execute("SELECT COUNT(*) as count FROM blockchain")
                    final_b_count = cursor.fetchone()['count']
                    
                    # Get latest transaction details
                    cursor.execute("""
                        SELECT id, amount, blockchain_hash, solidity_tx_hash, blockchain_status 
                        FROM transactions 
                        ORDER BY timestamp DESC 
                        LIMIT 1
                    """)
                    latest_tx = cursor.fetchone()
                    
                    cursor.execute("""
                        SELECT id, amount, solidity_tx_hash, gas_used
                        FROM blockchain_transactions 
                        ORDER BY timestamp DESC 
                        LIMIT 1
                    """)
                    latest_bt = cursor.fetchone()
                    
                    print(f"\n📊 Final State:")
                    print(f"   - Sender balance: ${initial_sender_balance} → ${final_sender_balance} (Δ: ${final_sender_balance - initial_sender_balance})")
                    print(f"   - Receiver balance: ${initial_receiver_balance} → ${final_receiver_balance} (Δ: ${final_receiver_balance - initial_receiver_balance})")
                    print(f"   - Transactions: {initial_tx_count} → {final_tx_count} (+{final_tx_count - initial_tx_count})")
                    print(f"   - Blockchain Transactions: {initial_bt_count} → {final_bt_count} (+{final_bt_count - initial_bt_count})")
                    print(f"   - Blockchain Blocks: {initial_b_count} → {final_b_count} (+{final_b_count - initial_b_count})")
                    
                    if latest_tx:
                        print(f"\n📋 Latest Transaction:")
                        print(f"   - ID: {latest_tx['id']}")
                        print(f"   - Amount: ${latest_tx['amount']}")
                        print(f"   - Blockchain Hash: {latest_tx['blockchain_hash'] or 'N/A'}")
                        print(f"   - Solidity TX Hash: {latest_tx['solidity_tx_hash'] or 'N/A'}")
                        print(f"   - Status: {latest_tx['blockchain_status']}")
                    
                    if latest_bt:
                        print(f"\n🔗 Latest Blockchain Transaction:")
                        print(f"   - ID: {latest_bt['id']}")
                        print(f"   - Amount: ${latest_bt['amount']}")
                        print(f"   - Solidity TX Hash: {latest_bt['solidity_tx_hash'] or 'N/A'}")
                        print(f"   - Gas Used: {latest_bt['gas_used'] or 'N/A'}")
                
                conn.close()
                
                # Validate the transaction
                balance_change_correct = (final_sender_balance == initial_sender_balance - amount and 
                                        final_receiver_balance == initial_receiver_balance + amount)
                
                tables_updated = (final_tx_count > initial_tx_count and 
                                final_bt_count > initial_bt_count)
                
                if balance_change_correct and tables_updated:
                    print(f"\n🎉 Transaction test PASSED!")
                    print(f"   ✅ Balances updated correctly")
                    print(f"   ✅ All blockchain tables updated")
                    return True
                else:
                    print(f"\n❌ Transaction test FAILED!")
                    if not balance_change_correct:
                        print(f"   ❌ Balance changes incorrect")
                    if not tables_updated:
                        print(f"   ❌ Blockchain tables not updated")
                    return False
                    
            else:
                print(f"❌ Transaction failed: {message}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    if test_transaction_with_blockchain():
        print("\n🏆 Blockchain integration is working perfectly!")
    else:
        print("\n💥 Blockchain integration needs attention!")
