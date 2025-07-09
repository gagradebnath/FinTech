#!/usr/bin/env python3
"""
Test Solidity blockchain connection and loading
"""

import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting Solidity blockchain test...")

try:
    from app.utils.solidity_blockchain import SolidityBlockchain
    print("Successfully imported SolidityBlockchain")
except Exception as e:
    print(f"Failed to import SolidityBlockchain: {e}")
    sys.exit(1)

def test_solidity_connection():
    """Test Solidity blockchain step by step"""
    print("Testing Solidity blockchain connection...")
    
    try:
        # Create instance
        solidity = SolidityBlockchain()
        print("SolidityBlockchain instance created")
        
        # Test connection
        print("Testing connection to Ethereum node...")
        connected = solidity.connect()
        print(f"Connection result: {connected}")
        
        if not connected:
            print("Failed to connect to Ethereum node")
            return False
            
        print("Connected to Ethereum node")
        print(f"   Connected: {solidity.is_connected}")
        
        # Test contract loading
        print("Testing contract loading...")
        contracts_loaded = solidity.load_contracts()
        print(f"Contract loading result: {contracts_loaded}")
        
        if not contracts_loaded:
            print("Failed to load contracts")
            return False
            
        print("Contracts loaded successfully")
        print(f"   Accounts loaded: {len(solidity.accounts)}")
        
        # Test specific accounts
        test_users = ['user', 'user15']
        for user_id in test_users:
            if user_id in solidity.accounts:
                address = solidity.accounts[user_id]
                print(f"Found {user_id}: {address}")
                
                # Test balance lookup
                balance_info = solidity.get_account_balance(user_id)
                print(f"   Balance info: {balance_info}")
            else:
                print(f"NOT FOUND {user_id}: Not found in loaded accounts")
                
        return True
        
    except Exception as e:
        print(f"Exception during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_solidity_connection()
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed!")
