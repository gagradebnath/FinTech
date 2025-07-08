#!/usr/bin/env python3
"""
Fix NULL balances in database
"""

import os
import sys

# Add paths
project_root = os.path.dirname(__file__)
app_dir = os.path.join(project_root, 'app')
sys.path.insert(0, project_root)
sys.path.insert(0, app_dir)

import pymysql
from app.config import Config

def fix_null_balances():
    print("🔧 Fixing NULL balances in database...")
    
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            # Check for NULL balances
            cursor.execute("SELECT id, first_name, last_name, balance FROM users WHERE balance IS NULL")
            null_balance_users = cursor.fetchall()
            
            if null_balance_users:
                print(f"Found {len(null_balance_users)} users with NULL balances:")
                for user in null_balance_users:
                    print(f"   - {user['first_name']} {user['last_name']} (ID: {user['id']})")
                
                # Fix NULL balances by setting them to 1000.00
                cursor.execute("UPDATE users SET balance = 1000.00 WHERE balance IS NULL")
                affected_rows = cursor.rowcount
                
                print(f"✅ Fixed {affected_rows} NULL balances, set to $1000.00")
                
                # Verify fix
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE balance IS NULL")
                remaining_nulls = cursor.fetchone()['count']
                
                if remaining_nulls == 0:
                    print("✅ All NULL balances fixed!")
                else:
                    print(f"⚠️ Still {remaining_nulls} NULL balances remaining")
                    
            else:
                print("✅ No NULL balances found")
            
            # Show current balance status
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN balance IS NOT NULL THEN 1 END) as users_with_balance,
                    MIN(balance) as min_balance,
                    MAX(balance) as max_balance,
                    AVG(balance) as avg_balance
                FROM users
            """)
            stats = cursor.fetchone()
            
            print(f"\n📊 Balance Statistics:")
            print(f"   - Total users: {stats['total_users']}")
            print(f"   - Users with balance: {stats['users_with_balance']}")
            print(f"   - Min balance: ${stats['min_balance']:.2f}")
            print(f"   - Max balance: ${stats['max_balance']:.2f}")
            print(f"   - Average balance: ${stats['avg_balance']:.2f}")
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing balances: {e}")
        return False

if __name__ == "__main__":
    fix_null_balances()
