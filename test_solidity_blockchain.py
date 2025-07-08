#!/usr/bin/env python3
"""
Test script for Solidity blockchain integration
"""

import os
import sys

# Add the project root and app directory to the Python path
project_root = os.path.dirname(__file__)
app_dir = os.path.join(project_root, 'app')
sys.path.insert(0, project_root)
sys.path.insert(0, app_dir)

from app.utils.solidity_blockchain import SolidityBlockchain

def test_solidity_integration():
    print("🧪 Testing Solidity Blockchain Integration")
    print("=" * 50)
    
    try:
        # Initialize blockchain
        print("📦 Initializing SolidityBlockchain...")
        blockchain = SolidityBlockchain()
        print("✅ SolidityBlockchain initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize SolidityBlockchain: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Connect to Hardhat node
    print("🔗 Connecting to Hardhat node...")
    if not blockchain.connect("http://127.0.0.1:8545"):
        print("❌ Failed to connect to blockchain")
        return False
    
    # Load contracts
    print("📄 Loading contracts...")
    if not blockchain.load_contracts("deployment-info.json"):
        print("❌ Failed to load contracts")
        return False
    
    # Test account balances
    print("\n💰 Testing account balances...")
    for user_id in ["admin", "admin2", "admin3"]:
        balance = blockchain.get_account_balance(user_id)
        if "error" in balance:
            print(f"❌ Error getting balance for {user_id}: {balance['error']}")
        else:
            print(f"✅ {user_id}: {balance['eth_balance']:.4f} ETH, {balance['fgt_balance']:.2f} FGT")
    
    # Test transaction creation
    print("\n💸 Testing transaction creation...")
    try:
        tx_result = blockchain.create_transaction(
            sender_id="admin",
            receiver_id="admin2", 
            amount=100.0,
            transaction_type="Transfer",
            note="Test transaction from Python",
            location="Test Location"
        )
        
        if tx_result["success"]:
            print(f"✅ Transaction successful!")
            print(f"   📋 Transaction Hash: {tx_result['transaction_hash']}")
            print(f"   🆔 Transaction ID: {tx_result['transaction_id']}")
            print(f"   ⛽ Gas Used: {tx_result['gas_used']}")
        else:
            print(f"❌ Transaction failed: {tx_result['error']}")
    except Exception as e:
        print(f"❌ Exception during transaction: {e}")
    
    # Check balances after transaction
    print("\n💰 Checking balances after transaction...")
    for user_id in ["admin", "admin2"]:
        balance = blockchain.get_account_balance(user_id)
        if "error" in balance:
            print(f"❌ Error getting balance for {user_id}: {balance['error']}")
        else:
            print(f"✅ {user_id}: {balance['eth_balance']:.4f} ETH, {balance['fgt_balance']:.2f} FGT")
    
    print("\n🎉 Solidity blockchain integration test completed!")
    return True

if __name__ == "__main__":
    test_solidity_integration()
