#!/usr/bin/env python3
"""
Simple Web3 connection test
"""

from web3 import Web3

def test_connection():
    print("🧪 Testing Web3 Connection")
    print("=" * 30)
    
    try:
        # Connect to Hardhat node
        w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        
        # Test connection
        is_connected = w3.is_connected()
        print(f"Connected: {is_connected}")
        
        if is_connected:
            print(f"Chain ID: {w3.eth.chain_id}")
            print(f"Latest block: {w3.eth.block_number}")
            
            # Test accounts
            accounts = w3.eth.accounts
            print(f"Available accounts: {len(accounts)}")
            for i, account in enumerate(accounts[:3]):
                balance = w3.eth.get_balance(account)
                balance_eth = w3.from_wei(balance, 'ether')
                print(f"  Account {i}: {account} - {balance_eth:.4f} ETH")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()
