#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath('.'))

from app import create_app
from app.utils.transaction_utils import send_money, get_user_by_id, lookup_user_by_identifier

def test_transaction_balance_handling():
    """Test transaction processing with balance handling"""
    app = create_app()
    
    with app.app_context():
        print("Testing transaction balance handling...")
        
        # Try to get some sample users
        try:
            # Try first few users from our database query
            sender = get_user_by_id('user')  # regular user
            recipient = get_user_by_id('user2')  # another user
            
            if not sender:
                print("❌ Sender user not found")
                return
            if not recipient:
                print("❌ Recipient user not found")
                return
            
            print(f"Sender: {sender['id']} - {sender['first_name']} {sender['last_name']}")
            print(f"Sender balance: {sender['balance']} (type: {type(sender['balance'])})")
            print(f"Recipient: {recipient['id']} - {recipient['first_name']} {recipient['last_name']}")
            print(f"Recipient balance: {recipient['balance']} (type: {type(recipient['balance'])})")
            
            # Try a small transaction
            amount = 10.0
            payment_method = "Bank Transfer"
            note = "Test transaction"
            location = "Test Location"
            tx_type = "Transfer"
            
            print(f"\nAttempting transaction: ${amount} from {sender['id']} to {recipient['id']}")
            
            success, message, updated_user = send_money(
                sender['id'], 
                recipient['id'], 
                amount, 
                payment_method, 
                note, 
                location, 
                tx_type
            )
            
            if success:
                print(f"✅ Transaction successful: {message}")
                if updated_user:
                    print(f"Updated sender balance: {updated_user['balance']}")
            else:
                print(f"❌ Transaction failed: {message}")
                
        except Exception as e:
            print(f"❌ Error during transaction test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_transaction_balance_handling()
