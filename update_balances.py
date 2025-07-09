#!/usr/bin/env python3
"""
Update Deployment Info with Real Balances
Updates deployment-info.json to include real balances from MySQL database
"""

import pymysql
import json
import sys
import os

def get_all_users_with_balances():
    """Get all users with their actual balances from MySQL database"""
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
                SELECT u.id, u.first_name, u.last_name, COALESCE(u.balance, 0) as balance,
                       c.email, c.phone
                FROM users u
                LEFT JOIN contact_info c ON u.id = c.user_id
                ORDER BY u.id
            ''')
            users = cursor.fetchall()
            return users
    finally:
        conn.close()

def update_deployment_info_with_balances():
    """Update deployment-info.json with real balances from database"""
    
    print("🔄 Updating deployment-info.json with real balances...")
    print("=" * 60)
    
    # Get users with balances from database
    print("📊 Fetching users and balances from database...")
    users = get_all_users_with_balances()
    print(f"✅ Found {len(users)} users in database")
    
    # Load current deployment info
    try:
        with open("deployment-info.json", 'r') as f:
            deployment_info = json.load(f)
        print("✅ Loaded existing deployment-info.json")
    except Exception as e:
        print(f"❌ Error loading deployment-info.json: {e}")
        return False
    
    # Create a mapping of user_id to balance
    user_balances = {user['id']: float(user['balance']) for user in users}
    
    # Update testAccounts with real balances
    updated_count = 0
    total_balance_before = 0
    total_balance_after = 0
    
    print(f"\n🔄 Updating balances for {len(deployment_info.get('testAccounts', []))} accounts...")
    
    for account in deployment_info.get('testAccounts', []):
        user_id = account.get('userId')
        old_balance = float(account.get('balance', 0))
        total_balance_before += old_balance
        
        if user_id in user_balances:
            new_balance = user_balances[user_id]
            account['balance'] = str(new_balance)
            total_balance_after += new_balance
            updated_count += 1
            
            if new_balance != old_balance:
                print(f"  📝 {user_id}: ${old_balance:,.2f} → ${new_balance:,.2f}")
        else:
            print(f"  ⚠️  {user_id}: Not found in database")
            total_balance_after += old_balance
    
    # Save updated deployment info
    try:
        # Create backup first
        with open("deployment-info.json.backup", 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        # Save updated version
        with open("deployment-info.json", 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"\n✅ Successfully updated deployment-info.json")
        print(f"📊 Updated {updated_count} accounts")
        print(f"💰 Total balance before: ${total_balance_before:,.2f}")
        print(f"💰 Total balance after: ${total_balance_after:,.2f}")
        print(f"📈 Balance change: ${total_balance_after - total_balance_before:,.2f}")
        print(f"💾 Backup saved as deployment-info.json.backup")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving deployment-info.json: {e}")
        return False

def verify_specific_users():
    """Verify balances for the specific users from the transaction"""
    try:
        with open("deployment-info.json", 'r') as f:
            deployment_info = json.load(f)
        
        test_users = ['user', 'user15']
        print(f"\n🔍 Verifying balances for transaction users:")
        
        for account in deployment_info.get('testAccounts', []):
            user_id = account.get('userId')
            if user_id in test_users:
                balance = float(account.get('balance', 0))
                address = account.get('address', 'N/A')
                print(f"  ✅ {user_id}: ${balance:,.2f} (Address: {address[:10]}...)")
        
    except Exception as e:
        print(f"❌ Error verifying users: {e}")

def main():
    """Main function"""
    print("💰 Updating Deployment Info with Real Balances")
    print("=" * 60)
    
    # Update deployment info with real balances
    success = update_deployment_info_with_balances()
    
    if success:
        # Verify specific users from the transaction
        verify_specific_users()
        
        print(f"\n🎉 Balance update completed successfully!")
        print(f"💡 Now all users in deployment-info.json have their real database balances")
        print(f"🚀 You can try the transaction again - users should have sufficient funds")
    else:
        print(f"\n❌ Balance update failed")

if __name__ == "__main__":
    main()
