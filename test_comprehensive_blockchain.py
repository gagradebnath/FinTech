#!/usr/bin/env python3
"""
Comprehensive Blockchain Integration Test
Tests both Python and Solidity blockchain integration with database updates
"""

import os
import sys
import time
import uuid

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.hybrid_blockchain import hybrid_blockchain
from app.utils.transaction_utils import send_money
from app.utils.solidity_blockchain import SolidityBlockchain
from flask import Flask
from app.config import Config
import pymysql

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
    
    app.get_db_connection = get_db_connection
    return app

def test_database_connection(app):
    """Test database connection"""
    print("🔗 Testing Database Connection...")
    try:
        with app.app_context():
            conn = app.get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM users")
                result = cursor.fetchone()
                print(f"✅ Database connected - {result['count']} users found")
            conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_blockchain_status():
    """Test blockchain initialization and status"""
    print("\n📊 Testing Blockchain Status...")
    
    status = hybrid_blockchain.get_blockchain_status()
    print(f"Python Blockchain: {'✅' if status['python_blockchain'] else '❌'}")
    print(f"Solidity Blockchain: {'✅' if status['solidity_blockchain'] else '❌'}")
    print(f"Solidity Connected: {'✅' if status['solidity_connected'] else '❌'}")
    
    return status['python_blockchain']

def test_user_balances(app):
    """Test getting user blockchain balances"""
    print("\n💰 Testing User Balances...")
    
    try:
        with app.app_context():
            # Test with admin users
            for user_id in ["admin", "admin2", "admin3"]:
                balance = hybrid_blockchain.get_user_balance(user_id)
                if "error" not in balance:
                    print(f"✅ {user_id}: {balance['eth_balance']:.4f} ETH, {balance['fgt_balance']:.2f} FGT")
                else:
                    print(f"⚠️ {user_id}: {balance['error']}")
        return True
    except Exception as e:
        print(f"❌ Balance test failed: {e}")
        return False

def test_transaction_integration(app):
    """Test complete transaction integration with all blockchain systems"""
    print("\n💸 Testing Transaction Integration...")
    
    try:
        with app.app_context():
            conn = app.get_db_connection()
            
            # Get test users
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users LIMIT 2")
                users = cursor.fetchall()
                
                if len(users) < 2:
                    print("❌ Need at least 2 users for transaction test")
                    return False
                
                sender = users[0]
                receiver = users[1]
                
                print(f"Testing transaction: {sender['first_name']} -> {receiver['first_name']}")
                
                # Record balances before
                cursor.execute("SELECT balance FROM users WHERE id = %s", (sender['id'],))
                sender_balance_before = cursor.fetchone()['balance']
                
                cursor.execute("SELECT balance FROM users WHERE id = %s", (receiver['id'],))
                receiver_balance_before = cursor.fetchone()['balance']
                
                print(f"Before - Sender: ${sender_balance_before}, Receiver: ${receiver_balance_before}")
                
                # Test transaction
                amount = 50.0
                success, message, updated_sender = send_money(
                    sender['id'], 
                    receiver['id'], 
                    amount, 
                    'blockchain_test', 
                    'Blockchain integration test transaction',
                    'Test Location',
                    'Transfer'
                )
                
                if success:
                    print(f"✅ Transaction successful: {message}")
                    
                    # Check balances after
                    cursor.execute("SELECT balance FROM users WHERE id = %s", (sender['id'],))
                    sender_balance_after = cursor.fetchone()['balance']
                    
                    cursor.execute("SELECT balance FROM users WHERE id = %s", (receiver['id'],))
                    receiver_balance_after = cursor.fetchone()['balance']
                    
                    print(f"After - Sender: ${sender_balance_after}, Receiver: ${receiver_balance_after}")
                    
                    # Verify balance changes
                    if (sender_balance_after == sender_balance_before - amount and 
                        receiver_balance_after == receiver_balance_before + amount):
                        print("✅ Database balances updated correctly")
                    else:
                        print("❌ Database balance mismatch")
                    
                    # Check blockchain tables
                    cursor.execute("""
                        SELECT COUNT(*) as count FROM blockchain_transactions 
                        WHERE user_id IN (%s, %s) AND timestamp > DATE_SUB(NOW(), INTERVAL 1 MINUTE)
                    """, (sender['id'], receiver['id']))
                    blockchain_tx_count = cursor.fetchone()['count']
                    
                    cursor.execute("""
                        SELECT COUNT(*) as count FROM blockchain 
                        WHERE timestamp > DATE_SUB(NOW(), INTERVAL 1 MINUTE)
                    """)
                    blockchain_block_count = cursor.fetchone()['count']
                    
                    print(f"✅ Blockchain transactions created: {blockchain_tx_count}")
                    print(f"✅ Blockchain blocks created: {blockchain_block_count}")
                    
                    # Check main transactions table
                    cursor.execute("""
                        SELECT * FROM transactions 
                        WHERE sender_id = %s AND receiver_id = %s 
                        AND timestamp > DATE_SUB(NOW(), INTERVAL 1 MINUTE)
                        ORDER BY timestamp DESC LIMIT 1
                    """, (sender['id'], receiver['id']))
                    main_tx = cursor.fetchone()
                    
                    if main_tx:
                        print(f"✅ Main transaction recorded: {main_tx['id']}")
                        print(f"   Amount: ${main_tx['amount']}")
                        print(f"   Type: {main_tx['type']}")
                        print(f"   Note: {main_tx['note']}")
                    else:
                        print("❌ Main transaction not found")
                    
                    return True
                else:
                    print(f"❌ Transaction failed: {message}")
                    return False
                    
            conn.close()
            
    except Exception as e:
        print(f"❌ Transaction integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_solidity_blockchain_direct():
    """Test Solidity blockchain directly"""
    print("\n🔗 Testing Solidity Blockchain Direct Connection...")
    
    try:
        blockchain = SolidityBlockchain()
        
        # Test connection
        if not blockchain.connect():
            print("❌ Failed to connect to Solidity blockchain")
            return False
        
        # Test contract loading
        if not blockchain.load_contracts():
            print("❌ Failed to load contracts")
            return False
        
        print("✅ Solidity blockchain connected and contracts loaded")
        
        # Test a transaction
        tx_result = blockchain.create_transaction(
            sender_id="admin",
            receiver_id="admin2",
            amount=25.0,
            transaction_type="Test",
            note="Direct Solidity test",
            location="Test Location"
        )
        
        if tx_result.get("success"):
            print(f"✅ Direct Solidity transaction successful")
            print(f"   Hash: {tx_result['transaction_hash']}")
            print(f"   Gas Used: {tx_result['gas_used']}")
        else:
            print(f"❌ Direct Solidity transaction failed: {tx_result.get('error')}")
        
        return tx_result.get("success", False)
        
    except Exception as e:
        print(f"❌ Direct Solidity test failed: {e}")
        return False

def main():
    """Run comprehensive blockchain integration tests"""
    print("🧪 COMPREHENSIVE BLOCKCHAIN INTEGRATION TEST")
    print("=" * 60)
    
    # Create test app
    app = create_test_app()
    
    test_results = []
    
    # Test 1: Database Connection
    with app.app_context():
        test_results.append(("Database Connection", test_database_connection(app)))
    
    # Test 2: Blockchain Status
    test_results.append(("Blockchain Status", test_blockchain_status()))
    
    # Test 3: User Balances  
    with app.app_context():
        test_results.append(("User Balances", test_user_balances(app)))
    
    # Test 4: Direct Solidity Test
    test_results.append(("Direct Solidity", test_solidity_blockchain_direct()))
    
    # Test 5: Full Transaction Integration
    with app.app_context():
        test_results.append(("Transaction Integration", test_transaction_integration(app)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("\n🎉 ALL TESTS PASSED! Blockchain integration is working correctly!")
    else:
        print(f"\n⚠️ {len(test_results) - passed} tests failed. Check the errors above.")
    
    return passed == len(test_results)

if __name__ == "__main__":
    main()
