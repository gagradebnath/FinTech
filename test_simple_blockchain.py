#!/usr/bin/env python3
"""
Simple transaction test with blockchain integration
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

def test_simple_transaction():
    print("🧪 Testing Simple Transaction with Blockchain")
    print("=" * 50)
    
    # Test database connection
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
            # Check if we have test users
            cursor.execute("SELECT id, first_name, last_name, balance FROM users LIMIT 5")
            users = cursor.fetchall()
            
            if len(users) < 2:
                print("❌ Not enough test users in database")
                return False
            
            print(f"✅ Found {len(users)} users in database")
            for user in users:
                print(f"   - {user['first_name']} {user['last_name']} (Balance: ${user['balance']})")
            
            # Test blockchain tables
            cursor.execute("SELECT COUNT(*) as count FROM blockchain_transactions")
            bt_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM blockchain")
            b_count = cursor.fetchone()['count']
            
            print(f"✅ Blockchain tables exist:")
            print(f"   - blockchain_transactions: {bt_count} records")
            print(f"   - blockchain: {b_count} records")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
        
        from flask import Flask
        print("✅ Flask imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hybrid_blockchain():
    print("\n📊 Testing Hybrid Blockchain Status...")
    try:
        from app.utils.hybrid_blockchain import hybrid_blockchain
        status = hybrid_blockchain.get_blockchain_status()
        print(f"Status: {status}")
        return True
    except Exception as e:
        print(f"❌ Hybrid blockchain test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 SIMPLE BLOCKCHAIN TEST")
    print("=" * 40)
    
    if test_imports():
        test_hybrid_blockchain()
    
    print("\n✅ Simple test completed!")
