#!/usr/bin/env python3
"""
Test reload functionality without Flask context
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_reload():
    try:
        # Direct import and test
        from app.utils.solidity_blockchain import SolidityBlockchain
        
        print("🔄 Testing Solidity blockchain reload...")
        
        # Create new instance
        solidity = SolidityBlockchain()
        
        # Connect
        if not solidity.connect():
            print("❌ Failed to connect")
            return False
        
        # Load contracts and accounts
        if not solidity.load_contracts():
            print("❌ Failed to load contracts")
            return False
        
        print(f"✅ Loaded {len(solidity.accounts)} accounts")
        
        # Test specific users
        test_users = ['user', 'user15']
        for user_id in test_users:
            if user_id in solidity.accounts:
                print(f"✅ {user_id}: Found at {solidity.accounts[user_id][:10]}...")
            else:
                print(f"❌ {user_id}: Not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_reload()
