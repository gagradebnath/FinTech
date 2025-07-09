import urllib.request
import urllib.error
import json
import time

def wait_for_server(max_wait=30):
    """Wait for Flask server to be ready"""
    print("Waiting for Flask server to start...")
    for i in range(max_wait):
        try:
            req = urllib.request.Request("http://localhost:5000/")
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    print(f"Server ready after {i+1} seconds")
                    return True
        except:
            time.sleep(1)
            if i % 5 == 4:
                print(f"Still waiting... ({i+1}s)")
    print("Server failed to start within timeout")
    return False

def test_reload_endpoint():
    """Test the reload endpoint"""
    url = "http://localhost:5000/reload-blockchain-accounts"
    
    try:
        print("Testing reload endpoint...")
        
        # Create POST request
        data = b''
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        # Make request
        with urllib.request.urlopen(req, timeout=15) as response:
            result = response.read().decode('utf-8')
            print(f"Status: {response.status}")
            print(f"Response: {result}")
            
            # Parse response
            try:
                data = json.loads(result)
                if data.get('success'):
                    print("SUCCESS: Accounts reloaded successfully!")
                    if 'test_results' in data:
                        print("Test user status:")
                        for user, status in data['test_results'].items():
                            print(f"  {user}: {status}")
                    return True
                else:
                    print(f"FAILED: {data.get('error', 'Unknown error')}")
                    return False
            except json.JSONDecodeError:
                print("Response is not valid JSON")
                return False
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        try:
            error_response = e.read().decode('utf-8')
            print(f"Error response: {error_response}")
        except:
            pass
        return False
    except urllib.error.URLError as e:
        print(f"URL Error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_transaction_simulation():
    """Simulate a transaction to test the fix"""
    print("\nNOTE: To test the transaction fix:")
    print("1. Go to http://localhost:5000/")
    print("2. Login as 'user' (or any test user)")  
    print("3. Try sending money to 'user15'")
    print("4. Check the console output for blockchain messages")
    print("5. Look for 'All required users found in Solidity blockchain' message")

if __name__ == "__main__":
    print("=== Testing Blockchain Account Reload Fix ===")
    
    if wait_for_server():
        print("\n--- Testing Reload Endpoint ---")
        if test_reload_endpoint():
            print("\n--- Ready for Transaction Testing ---")
            test_transaction_simulation()
        else:
            print("\nReload endpoint failed - check Flask logs")
    else:
        print("Flask server is not responding")
        print("Make sure to run: python run.py")
