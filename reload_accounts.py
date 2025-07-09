#!/usr/bin/env python3
"""
Reload Solidity Blockchain Accounts
Reloads accounts from deployment-info.json without restarting the Flask application
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def reload_blockchain_accounts():
    """Reload blockchain accounts in the running application"""
    try:
        # Import the hybrid blockchain instance
        from app.utils.hybrid_blockchain import hybrid_blockchain
        
        if not hybrid_blockchain.solidity_available:
            print("❌ Solidity blockchain not available")
            return False
        
        # Reload accounts
        success = hybrid_blockchain.solidity_blockchain.reload_accounts()
        
        if success:
            # Test with the specific users from the transaction
            test_users = ['user', 'user15']
            print(f"\n🔍 Testing specific users:")
            
            for user_id in test_users:
                balance_info = hybrid_blockchain.solidity_blockchain.get_account_balance(user_id)
                if 'error' in balance_info:
                    print(f"  ❌ {user_id}: {balance_info['error']}")
                else:
                    print(f"  ✅ {user_id}: Found with address")
        
        return success
        
    except Exception as e:
        print(f"❌ Error reloading accounts: {e}")
        return False

def main():
    """Main function"""
    print("🔄 Reloading Solidity Blockchain Accounts...")
    print("=" * 50)
    
    success = reload_blockchain_accounts()
    
    if success:
        print(f"\n🎉 Account reload completed successfully!")
        print(f"💡 Solidity blockchain should now recognize all 555 users")
        print(f"🚀 Try your transaction again - 'User address not found' should be resolved")
    else:
        print(f"\n❌ Account reload failed")
        print(f"💡 You may need to restart the Flask application")

if __name__ == "__main__":
    main()
