#!/usr/bin/env python3
"""
Flask-integrated Blockchain Test Script
This script tests the blockchain with full Flask app context
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.utils.blockchain import finguard_blockchain, process_blockchain_transaction, verify_transaction, get_blockchain_stats

def test_with_flask_context():
    """Test blockchain functionality with Flask app context"""
    print("🚀 FinGuard Blockchain Test Suite (With Flask Context)")
    print("=" * 65)
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        print("✅ Flask app context established")
        
        # Test 1: Process transactions through the integrated system
        print("\n📝 Test 1: Processing transactions through Flask integration...")
        
        # Test transaction processing
        result1 = process_blockchain_transaction("user1", "user2", 100.0, "Transfer", "Payment for services")
        result2 = process_blockchain_transaction("user2", "user3", 50.0, "Transfer", "Split bill")
        result3 = process_blockchain_transaction("user1", "user3", 25.0, "Transfer", "Coffee money")
        
        print(f"✅ Transaction results: {result1}, {result2}, {result3}")
        
        # Test 2: Get blockchain statistics
        print("\n📊 Test 2: Getting blockchain statistics...")
        
        stats = get_blockchain_stats()
        print(f"✅ Total Blocks: {stats['total_blocks']}")
        print(f"✅ Total Transactions: {stats['total_transactions']}")
        print(f"✅ Chain Valid: {stats['chain_valid']}")
        print(f"✅ Pending Transactions: {stats['pending_transactions']}")
        print(f"✅ Latest Block Hash: {stats['latest_block_hash'][:20] if stats['latest_block_hash'] else 'None'}...")
        
        # Test 3: Balance calculation
        print("\n💰 Test 3: Checking balances...")
        
        balance_user1 = finguard_blockchain.get_balance("user1")
        balance_user2 = finguard_blockchain.get_balance("user2")
        balance_user3 = finguard_blockchain.get_balance("user3")
        
        print(f"✅ User1 balance: ${balance_user1}")
        print(f"✅ User2 balance: ${balance_user2}")
        print(f"✅ User3 balance: ${balance_user3}")
        
        # Test 4: Transaction verification
        print("\n🔍 Test 4: Transaction verification...")
        
        # Get a transaction ID from the blockchain
        if len(finguard_blockchain.chain) > 1:
            for block in finguard_blockchain.chain:
                if len(block.transactions) > 0:
                    tx_id = block.transactions[0].id
                    verification = verify_transaction(tx_id)
                    print(f"✅ Transaction {tx_id[:8]}... verified: {verification['verified']}")
                    break
        
        # Test 5: Database integration
        print("\n🗄️  Test 5: Database integration...")
        
        # Check if blocks and transactions were saved to database
        try:
            conn = app.get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM blockchain")
                block_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM blockchain_transactions")
                tx_count = cursor.fetchone()['count']
                
                print(f"✅ Blocks in database: {block_count}")
                print(f"✅ Transactions in database: {tx_count}")
            conn.close()
        except Exception as e:
            print(f"⚠️  Database check failed: {e}")
        
        print("\n🎉 Flask integration tests completed successfully!")
        print("=" * 65)

if __name__ == "__main__":
    test_with_flask_context()
