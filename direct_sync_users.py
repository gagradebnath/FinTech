#!/usr/bin/env python3
"""
Direct User Sync to Solidity Blockchain
Syncs all users from MySQL database to Solidity blockchain without Flask dependencies
"""

import pymysql
import sys
import os
import json
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_all_users_from_db():
    """Get all users from MySQL database"""
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='g85a',
        database='fin_guard',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT u.id, u.first_name, u.last_name, c.email, c.phone
                FROM users u
                LEFT JOIN contact_info c ON u.id = c.user_id
                ORDER BY u.id
            ''')
            users = cursor.fetchall()
            return users
    finally:
        conn.close()

def init_solidity_blockchain():
    """Initialize Solidity blockchain connection"""
    try:
        from app.utils.solidity_blockchain import SolidityBlockchain
        
        solidity = SolidityBlockchain()
        if solidity.connect():
            if solidity.load_contracts():
                print("✅ Solidity blockchain available")
                return solidity
            else:
                print("❌ Failed to load contracts")
                return None
        else:
            print("❌ Failed to connect to Solidity blockchain")
            return None
    except Exception as e:
        print(f"❌ Error initializing Solidity blockchain: {e}")
        return None

def register_user_in_solidity(solidity, user):
    """Register a single user in Solidity blockchain by adding to accounts"""
    try:
        user_id = user['id']
        
        # Check if user already exists
        if user_id in solidity.accounts:
            print(f"  ✅ {user_id} already has address: {solidity.accounts[user_id]}")
            return True
        
        # Generate a new Ethereum address for this user
        from eth_account import Account
        account = Account.create()
        
        # Add the user to solidity accounts
        solidity.accounts[user_id] = account.address
        
        print(f"  ✅ {user_id} assigned address: {account.address}")
        return True
            
    except Exception as e:
        print(f"  ❌ {user['id']} error: {e}")
        return False

def save_updated_deployment_info(solidity):
    """Save updated account mappings to deployment-info.json"""
    try:
        # Load existing deployment info
        with open("deployment-info.json", 'r') as f:
            deployment_info = json.load(f)
        
        # Update testAccounts with all users
        deployment_info['testAccounts'] = []
        for user_id, address in solidity.accounts.items():
            deployment_info['testAccounts'].append({
                "address": address,
                "userId": user_id,
                "balance": "0"  # Default balance
            })
        
        # Save back to file
        with open("deployment-info.json", 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"✅ Updated deployment-info.json with {len(solidity.accounts)} accounts")
        return True
        
    except Exception as e:
        print(f"❌ Error saving deployment info: {e}")
        return False

def main():
    print("🔄 Direct User Sync to Solidity Blockchain...")
    print("=" * 50)
    
    # Initialize Solidity blockchain
    print("🔗 Initializing Solidity blockchain...")
    solidity = init_solidity_blockchain()
    if not solidity:
        print("❌ Cannot proceed without Solidity blockchain connection")
        return False
    
    # Get all users from database
    print("📊 Fetching users from database...")
    try:
        users = get_all_users_from_db()
        print(f"📊 Found {len(users)} users in database")
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return False
    
    # Register users in batches
    print("🚀 Starting user registration...")
    success_count = 0
    fail_count = 0
    already_registered = 0
    
    for i, user in enumerate(users, 1):
        print(f"[{i}/{len(users)}] Processing {user['id']}...")
        
        # Check if already exists first
        if user['id'] in solidity.accounts:
            print(f"  ✅ {user['id']} already has address")
            already_registered += 1
            continue
        
        # Register user
        if register_user_in_solidity(solidity, user):
            success_count += 1
        else:
            fail_count += 1
        
        # Progress update every 50 users
        if i % 50 == 0:
            print(f"📊 Progress: {i}/{len(users)} processed (Success: {success_count}, Failed: {fail_count}, Already: {already_registered})")
    
    # Final summary
    print("=" * 50)
    print("📊 Final Summary:")
    print(f"✅ Successfully registered: {success_count}")
    print(f"🔄 Already registered: {already_registered}")
    print(f"❌ Failed to register: {fail_count}")
    print(f"📊 Total processed: {len(users)}")
    
    # Save updated deployment info
    if success_count > 0:
        print("\n💾 Saving updated account mappings...")
        save_updated_deployment_info(solidity)
    
    # Test the specific users from the transaction
    print("\n🔍 Testing specific users from transaction...")
    test_users = ['user', 'user15']
    
    for user_id in test_users:
        if user_id in solidity.accounts:
            address = solidity.accounts[user_id]
            print(f"✅ {user_id}: Address = {address}")
            
            try:
                balance_info = solidity.get_account_balance(user_id)
                if balance_info.get('error'):
                    print(f"   ⚠️  Balance check: {balance_info['error']}")
                else:
                    print(f"   💰 ETH Balance: {balance_info.get('eth_balance', 0)}")
                    print(f"   💰 FGT Balance: {balance_info.get('fgt_balance', 0)}")
            except Exception as e:
                print(f"   ⚠️  Balance check error: {e}")
        else:
            print(f"❌ {user_id}: Not registered")
    
    # Save updated deployment info
    print("💾 Saving updated deployment information...")
    save_updated_deployment_info(solidity)
    
    return success_count > 0 or already_registered > 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Sync interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
