import urllib.request
import urllib.error
import json

def test_reload_via_urllib():
    """Test reload endpoint using urllib"""
    url = "http://localhost:5000/reload-blockchain-accounts"
    
    try:
        print("Testing reload endpoint...")
        
        # Create POST request
        data = b''  # Empty POST data
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        # Make request
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(f"Status: {response.status}")
            print(f"Response: {result}")
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(f"Response: {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"URL Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_reload_via_urllib()
