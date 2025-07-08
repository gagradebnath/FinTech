#!/usr/bin/env python3
"""
Simple test to create a transaction with existing users
"""

from app import create_app
from app.utils.blockchain import process_blockchain_transaction

def test_real_transaction():
    app = create_app()
    
    with app.app_context():
        print("🔄 Creating test transaction with real users...")
        
        # Simple transaction between admin and admin2
        result = process_blockchain_transaction(
            sender_id="admin",
            receiver_id="admin2", 
            amount=25.00,
            transaction_type="Transfer",
            note="Test blockchain transaction",
            location="Test Location"
        )
        
        print(f"Transaction result: {result}")
        
        # Check database
        conn = app.get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM blockchain_transactions")
            tx_count = cursor.fetchone()['count']
            print(f"Total blockchain transactions in DB: {tx_count}")
            
            cursor.execute("""
                SELECT bt.user_id, bt.amount, bt.method, u.first_name, u.last_name
                FROM blockchain_transactions bt
                JOIN users u ON bt.user_id = u.id
                ORDER BY bt.timestamp DESC
                LIMIT 5
            """)
            recent_txs = cursor.fetchall()
            
            print("\nRecent blockchain transactions:")
            for tx in recent_txs:
                amount_str = f"+${tx['amount']:.2f}" if tx['amount'] >= 0 else f"${tx['amount']:.2f}"
                print(f"  {tx['first_name']} {tx['last_name']}: {amount_str} ({tx['method']})")
        
        conn.close()

if __name__ == "__main__":
    test_real_transaction()
