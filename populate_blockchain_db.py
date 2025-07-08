#!/usr/bin/env python3
"""
Test script to populate blockchain database tables with real transactions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.utils.blockchain import process_blockchain_transaction

def populate_blockchain_tables():
    """Populate blockchain tables with test transactions using real users"""
    print("🔄 Populating Blockchain Database Tables")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Get some real users from database
        conn = app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, first_name, last_name FROM users LIMIT 5")
                users = cursor.fetchall()
                
                if len(users) < 2:
                    print("❌ Need at least 2 users in database. Please run database_seed.py first.")
                    return
                
                print(f"✅ Found {len(users)} users in database")
                for user in users:
                    print(f"   - {user['first_name']} {user['last_name']} (ID: {user['id'][:8]}...)")
        finally:
            conn.close()
        
        # Create test transactions between real users
        print("\n📝 Creating blockchain transactions...")
        
        transactions = [
            {
                'sender': users[0]['id'],
                'receiver': users[1]['id'],
                'amount': 100.50,
                'type': 'Transfer',
                'note': 'Lunch payment'
            },
            {
                'sender': users[1]['id'],
                'receiver': users[2]['id'] if len(users) > 2 else users[0]['id'],
                'amount': 75.25,
                'type': 'Transfer',
                'note': 'Movie tickets'
            },
            {
                'sender': users[0]['id'],
                'receiver': users[2]['id'] if len(users) > 2 else users[1]['id'],
                'amount': 50.00,
                'type': 'Transfer',
                'note': 'Coffee'
            },
            {
                'sender': users[2]['id'] if len(users) > 2 else users[1]['id'],
                'receiver': users[0]['id'],
                'amount': 200.00,
                'type': 'Transfer',
                'note': 'Rent split'
            },
            {
                'sender': users[1]['id'],
                'receiver': users[0]['id'],
                'amount': 33.75,
                'type': 'Transfer',
                'note': 'Gas money'
            }
        ]
        
        successful_transactions = 0
        
        for i, tx in enumerate(transactions, 1):
            print(f"\n📤 Transaction {i}: ${tx['amount']} from {tx['sender'][:8]}... to {tx['receiver'][:8]}...")
            
            try:
                result = process_blockchain_transaction(
                    sender_id=tx['sender'],
                    receiver_id=tx['receiver'],
                    amount=tx['amount'],
                    transaction_type=tx['type'],
                    note=tx['note'],
                    location="Test Location"
                )
                
                if result:
                    successful_transactions += 1
                    print(f"   ✅ Transaction successful")
                else:
                    print(f"   ❌ Transaction failed")
                    
            except Exception as e:
                print(f"   ❌ Transaction error: {e}")
        
        print(f"\n📊 Summary:")
        print(f"   Total transactions attempted: {len(transactions)}")
        print(f"   Successful transactions: {successful_transactions}")
        
        # Verify database population
        print(f"\n🔍 Verifying database population...")
        conn = app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM blockchain")
                block_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM blockchain_transactions")
                tx_count = cursor.fetchone()['count']
                
                print(f"   ✅ Blocks in database: {block_count}")
                print(f"   ✅ Transactions in database: {tx_count}")
                
                # Show sample data
                print(f"\n📋 Sample blockchain data:")
                cursor.execute('''
                    SELECT b.index, LEFT(b.hash, 20) as hash_short, 
                           COUNT(bt.id) as tx_count
                    FROM blockchain b
                    LEFT JOIN blockchain_transactions bt ON b.transaction_id = bt.id
                    GROUP BY b.id, b.index, b.hash
                    ORDER BY b.index DESC
                    LIMIT 5
                ''')
                blocks = cursor.fetchall()
                
                for block in blocks:
                    print(f"   Block {block['index']}: {block['hash_short']}... ({block['tx_count']} linked txs)")
                
                print(f"\n💰 Sample transaction data:")
                cursor.execute('''
                    SELECT u.first_name, u.last_name, bt.amount, bt.method
                    FROM blockchain_transactions bt
                    JOIN users u ON bt.user_id = u.id
                    ORDER BY bt.timestamp DESC
                    LIMIT 5
                ''')
                transactions = cursor.fetchall()
                
                for tx in transactions:
                    amount_str = f"+${tx['amount']:.2f}" if tx['amount'] >= 0 else f"${tx['amount']:.2f}"
                    print(f"   {tx['first_name']} {tx['last_name']}: {amount_str} ({tx['method']})")
                    
        finally:
            conn.close()
        
        print(f"\n🎉 Database population completed!")
        print(f"💡 You can now view the populated tables at: /blockchain/database-view")
        print("=" * 50)

if __name__ == "__main__":
    populate_blockchain_tables()
