#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath('.'))

from app import create_app
from app.utils.transaction_utils import send_money, lookup_user_by_identifier, get_user_by_id
from app.utils.user_utils import get_current_user
from app.utils.permissions_utils import has_permission
from app.utils.overspending_detector import detect_overspending

def test_send_money_flow():
    """Test the complete send money flow step by step"""
    print("=== TESTING SEND MONEY FLOW ===\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test 1: Get current user (simulate session)
            print("1. Testing get_current_user()...")
            user = get_current_user()
            if user:
                print(f"✅ User found: {user['id']} - {user['first_name']} {user['last_name']}")
                print(f"   Balance: {user['balance']} (type: {type(user['balance'])})")
            else:
                print("❌ No user found")
                return
            
            # Test 2: Check permissions
            print(f"\n2. Testing permissions for user {user['id']}...")
            has_send_perm = has_permission(user['id'], 'perm_send_money')
            print(f"   Has send money permission: {has_send_perm}")
            
            # Test 3: Lookup another user to send money to
            print(f"\n3. Testing user lookup...")
            # Try to find a different user
            test_recipient_id = 'user2' if user['id'] != 'user2' else 'user3'
            recipient = lookup_user_by_identifier(test_recipient_id)
            if recipient:
                print(f"✅ Recipient found: {recipient['id']}")
                # Get full user details
                recipient_full = get_user_by_id(recipient['id'])
                if recipient_full:
                    print(f"   Full recipient: {recipient_full['first_name']} {recipient_full['last_name']}")
                    print(f"   Balance: {recipient_full['balance']} (type: {type(recipient_full['balance'])})")
                else:
                    print("❌ Could not get full recipient details")
                    return
            else:
                print(f"❌ Recipient {test_recipient_id} not found")
                return
            
            # Test 4: Check overspending
            print(f"\n4. Testing overspending detection...")
            amount = 10.0
            try:
                overspending = detect_overspending(user['id'], 'Test transaction', amount)
                print(f"   Overspending result: {overspending}")
            except Exception as e:
                print(f"❌ Overspending detection failed: {e}")
                return
            
            # Test 5: Actual send money transaction
            print(f"\n5. Testing send_money function...")
            print(f"   Sending ${amount} from {user['id']} to {recipient['id']}")
            
            success, message, updated_user = send_money(
                user['id'],
                recipient['id'],
                amount,
                'bank',  # payment method
                'Test transaction',  # note
                'Test Location',  # location
                'Transfer'  # transaction type
            )
            
            if success:
                print(f"✅ Transaction successful: {message}")
                if updated_user:
                    print(f"   Updated sender balance: {updated_user['balance']}")
            else:
                print(f"❌ Transaction failed: {message}")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_send_money_flow()
