#!/usr/bin/env python3
"""
User Sync Utility for FinGuard
Syncs all users from MySQL database to Solidity blockchain
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from app.config import Config
from app.utils.solidity_blockchain import SolidityBlockchain
import pymysql

def create_app():
    """Create Flask app for database access"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    def get_db_connection():
        return pymysql.connect(
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME'],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
    
    app.get_db_connection = get_db_connection
    return app

def get_all_users_from_db(app):
    """Get all users from the database"""
    with app.app_context():
        conn = app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT u.id, u.first_name, u.last_name, u.balance,
                           c.email, c.phone
                    FROM users u
                    LEFT JOIN contact_info c ON u.id = c.user_id
                    ORDER BY u.id
                ''')
                users = cursor.fetchall()
            return users
        finally:
            conn.close()

def sync_users_to_solidity(users):
    """Sync all users to Solidity blockchain"""
    try:
        # Initialize Solidity blockchain
        solidity_blockchain = SolidityBlockchain()
        
        if not solidity_blockchain.connect():
            print("❌ Failed to connect to Solidity blockchain")
            return False
        
        if not solidity_blockchain.load_contracts():
            print("❌ Failed to load Solidity contracts")
            return False
        
        print(f"✅ Connected to Solidity blockchain")
        print(f"📊 Found {len(users)} users in database")
        
        registered_count = 0
        skipped_count = 0
        error_count = 0
        
        for user in users:
            user_id = user['id']
            first_name = user.get('first_name', '') or ''
            last_name = user.get('last_name', '') or ''
            email = user.get('email', '') or ''
            phone = user.get('phone', '') or ''
            balance = float(user.get('balance', 0) or 0)
            
            print(f"\n🔍 Processing user: {user_id}")
            
            # Check if user already exists in Solidity blockchain
            balance_check = solidity_blockchain.get_account_balance(user_id)
            
            if balance_check.get('error') == 'User address not found':
                # User doesn't exist, register them
                print(f"  📝 Registering new user: {user_id}")
                
                registration_result = solidity_blockchain.register_user(
                    user_id, first_name, last_name, email, phone
                )
                
                if registration_result.get('success'):
                    print(f"  ✅ Successfully registered user: {user_id}")
                    registered_count += 1
                    
                    # Set initial balance if the user has one
                    if balance > 0:
                        print(f"  💰 Setting initial balance: ${balance}")
                        # Note: You might need to implement set_balance method in SolidityBlockchain
                        # For now, we'll just log it
                        print(f"  ⚠️  Initial balance set to 0 (implement set_balance method)")
                    
                else:
                    print(f"  ❌ Failed to register user {user_id}: {registration_result.get('error')}")
                    error_count += 1
            
            elif 'balance' in balance_check:
                # User already exists
                current_balance = balance_check['balance']
                print(f"  ✅ User already exists with balance: ${current_balance}")
                skipped_count += 1
            
            else:
                # Other error
                print(f"  ❌ Error checking user {user_id}: {balance_check}")
                error_count += 1
        
        print(f"\n" + "="*50)
        print(f"📊 SYNC RESULTS:")
        print(f"   ✅ Registered: {registered_count}")
        print(f"   ⏭️  Skipped (already exists): {skipped_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"   📊 Total processed: {len(users)}")
        print(f"="*50)
        
        return error_count == 0
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        return False

def main():
    """Main function"""
    print("🔄 Starting User Sync to Solidity Blockchain...")
    print("="*50)
    
    # Create Flask app
    app = create_app()
    
    # Get all users from database
    print("📊 Fetching users from database...")
    users = get_all_users_from_db(app)
    
    if not users:
        print("⚠️  No users found in database")
        return
    
    # Sync users to Solidity blockchain
    success = sync_users_to_solidity(users)
    
    if success:
        print("\n🎉 User sync completed successfully!")
        print("💡 You can now try transactions with any user from the database")
    else:
        print("\n⚠️  User sync completed with errors")
        print("💡 Check the error messages above and try again")

if __name__ == "__main__":
    main()
