#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath('.'))

from app import create_app

def test_send_money_route():
    """Test if the send money route is accessible"""
    print("=== TESTING SEND MONEY ROUTE ACCESS ===\n")
    
    app = create_app()
    
    with app.test_client() as client:
        try:
            # Test GET request to send-money route
            print("1. Testing GET /send-money...")
            response = client.get('/send-money')
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Route accessible")
                # Check if the response contains expected content
                if b'Send Money' in response.data:
                    print("✅ Send Money form found in response")
                else:
                    print("❌ Send Money form not found in response")
            elif response.status_code == 302:
                print(f"📍 Redirect to: {response.headers.get('Location', 'Unknown')}")
                print("   (This might be due to authentication requirement)")
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                
            # Try to test with a mock session
            print("\n2. Testing with mock session...")
            with client.session_transaction() as sess:
                sess['user_id'] = 'user'  # Set a test user
            
            response = client.get('/send-money')
            print(f"   Status Code with session: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Route accessible with session")
                if b'Send Money' in response.data:
                    print("✅ Send Money form found")
                    
                    # Test a POST request
                    print("\n3. Testing POST to /send-money...")
                    post_data = {
                        'recipient_identifier': 'user2',
                        'amount': '10.00',
                        'payment_method': 'bank',
                        'note': 'Test transaction',
                        'location': 'Test Location'
                    }
                    
                    post_response = client.post('/send-money', data=post_data)
                    print(f"   POST Status Code: {post_response.status_code}")
                    
                    if post_response.status_code == 200:
                        print("✅ POST request processed")
                        # Check for success or error messages
                        response_text = post_response.data.decode('utf-8')
                        if 'Successfully sent' in response_text:
                            print("✅ Transaction appears successful")
                        elif 'error' in response_text.lower():
                            print("⚠️ Error message found in response")
                            # Extract error for debugging
                            start = response_text.find('error')
                            snippet = response_text[max(0, start-50):start+200]
                            print(f"   Error snippet: {snippet}")
                        else:
                            print("ℹ️ No clear success/error message found")
                    else:
                        print(f"❌ POST failed with status: {post_response.status_code}")
                else:
                    print("❌ Send Money form not found")
            else:
                print(f"❌ Route not accessible even with session: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error during route test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_send_money_route()
