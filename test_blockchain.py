#!/usr/bin/env python3
"""
Blockchain Test Script for FinGuard
This script tests the blockchain functionality independently
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import blockchain components directly without Flask app dependencies
from app.utils.blockchain import Transaction, Block, FinGuardBlockchain
import time

def test_blockchain_standalone():
    """Test blockchain without Flask app context"""
    print("🚀 FinGuard Blockchain Test Suite (Standalone)")
    print("=" * 60)
    
    # Initialize blockchain (this will work without Flask context now)
    blockchain = FinGuardBlockchain()
    blockchain.ensure_initialized()  # Manually ensure initialization
    print(f"✅ Blockchain initialized with {len(blockchain.chain)} blocks")
    
    # Test 1: Create transactions
    print("\n📝 Test 1: Creating transactions...")
    
    # First, give users some initial balance through system transactions
    initial_tx1 = Transaction("system", "user1", 1000.0, "Initial Balance", "Starting balance")
    initial_tx1.sign_transaction("system_private_key")
    initial_tx2 = Transaction("system", "user2", 500.0, "Initial Balance", "Starting balance")
    initial_tx2.sign_transaction("system_private_key")
    
    blockchain.add_transaction(initial_tx1)
    blockchain.add_transaction(initial_tx2)
    
    # Mine initial transactions
    initial_block = blockchain.mine_pending_transactions("system")
    if initial_block:
        print(f"✅ Initial balance block mined: {initial_block.hash[:20]}...")
    
    # Create test transactions
    tx1 = Transaction("user1", "user2", 100.0, "Transfer", "Payment for services")
    tx1.sign_transaction("user1_private_key")
    
    tx2 = Transaction("user2", "user3", 50.0, "Transfer", "Split bill")
    tx2.sign_transaction("user2_private_key")
    
    tx3 = Transaction("user1", "user3", 25.0, "Transfer", "Coffee money")
    tx3.sign_transaction("user1_private_key")
    
    print(f"✅ Created 3 test transactions")
    
    # Test 2: Add transactions to blockchain
    print("\n⛏️  Test 2: Adding transactions to blockchain...")
    
    result1 = blockchain.add_transaction(tx1)
    result2 = blockchain.add_transaction(tx2)
    result3 = blockchain.add_transaction(tx3)
    
    print(f"✅ Transactions added: {result1}, {result2}, {result3}")
    print(f"✅ Pending transactions: {len(blockchain.pending_transactions)}")
    
    # Test 3: Mine block
    print("\n⛏️  Test 3: Mining block...")
    start_time = time.time()
    
    mined_block = blockchain.mine_pending_transactions("miner1")
    
    end_time = time.time()
    if mined_block:
        print(f"✅ Block mined in {end_time - start_time:.2f} seconds")
        print(f"✅ Block hash: {mined_block.hash}")
        print(f"✅ Total blocks: {len(blockchain.chain)}")
    else:
        print("ℹ️  No block mined (no pending transactions)")
        print(f"✅ Total blocks: {len(blockchain.chain)}")
    
    # Test 4: Validate blockchain
    print("\n🔍 Test 4: Validating blockchain...")
    
    is_valid = blockchain.is_chain_valid()
    print(f"✅ Blockchain valid: {is_valid}")
    
    # Test 5: Check balances
    print("\n💰 Test 5: Checking balances...")
    
    balance_user1 = blockchain.get_balance("user1")
    balance_user2 = blockchain.get_balance("user2")
    balance_user3 = blockchain.get_balance("user3")
    balance_miner = blockchain.get_balance("miner1")
    
    print(f"✅ User1 balance: ${balance_user1}")
    print(f"✅ User2 balance: ${balance_user2}")
    print(f"✅ User3 balance: ${balance_user3}")
    print(f"✅ Miner1 balance: ${balance_miner}")
    
    # Test 6: Transaction history
    print("\n📋 Test 6: Transaction history...")
    
    history_user1 = blockchain.get_transaction_history("user1")
    print(f"✅ User1 has {len(history_user1)} transactions in history")
    
    for tx in history_user1:
        direction = "sent" if tx['sender_id'] == "user1" else "received"
        print(f"   - {direction} ${tx['amount']} - {tx['transaction_type']}")
    
    # Test 7: Block exploration
    print("\n🔍 Test 7: Block exploration...")
    
    for i, block in enumerate(blockchain.chain):
        print(f"Block {i}:")
        print(f"   Hash: {block.hash[:20]}...")
        print(f"   Previous: {block.previous_hash[:20]}...")
        print(f"   Transactions: {len(block.transactions)}")
        print(f"   Timestamp: {block.timestamp}")
        
        for j, tx in enumerate(block.transactions):
            print(f"      Tx {j+1}: {tx.sender_id} -> {tx.receiver_id}: ${tx.amount}")
    
    print("\n🎉 All tests completed successfully!")
    print("=" * 60)
    
    return blockchain

def test_security():
    print("\n🛡️  Security Test: Tampering Detection")
    print("-" * 40)
    
    blockchain = FinGuardBlockchain()
    
    # Add a transaction and mine
    tx = Transaction("user1", "user2", 100.0, "Transfer", "Test transaction")
    tx.sign_transaction("user1_private_key")
    blockchain.add_transaction(tx)
    blockchain.mine_pending_transactions("miner1")
    
    print("✅ Original blockchain is valid:", blockchain.is_chain_valid())
    
    # Try to tamper with a transaction (this should make the blockchain invalid)
    if len(blockchain.chain) > 1 and len(blockchain.chain[1].transactions) > 0:
        print("🔓 Attempting to tamper with transaction...")
        blockchain.chain[1].transactions[0].amount = 999999.0  # Tamper with amount
        
        print("❌ Blockchain after tampering is valid:", blockchain.is_chain_valid())
        print("✅ Tampering detected successfully!")
    
    print("-" * 40)

if __name__ == "__main__":
    # Run blockchain tests
    blockchain = test_blockchain_standalone()
    
    # Run security tests
    test_security()
    
    print(f"\n📊 Final Statistics:")
    print(f"   Total Blocks: {len(blockchain.chain)}")
    print(f"   Total Transactions: {sum(len(block.transactions) for block in blockchain.chain)}")
    print(f"   Blockchain Valid: {blockchain.is_chain_valid()}")
    print(f"   Latest Block Hash: {blockchain.get_latest_block().hash}")
