#!/usr/bin/env python3
"""
Simple test for deployment-info.json loading
"""

import json
import os

print("🔍 Testing deployment-info.json loading...")

# Check current directory
print(f"Current directory: {os.getcwd()}")

# Check if file exists
file_path = "deployment-info.json"
if os.path.exists(file_path):
    print(f"✅ File exists: {file_path}")
    
    # Load and examine the file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        print(f"📊 File loaded successfully")
        print(f"🔑 Keys: {list(data.keys())}")
        
        if 'testAccounts' in data:
            accounts = data['testAccounts']
            print(f"👥 Test accounts found: {len(accounts)}")
            
            # Look for specific users
            user_found = False
            user15_found = False
            
            for account in accounts:  # Check all accounts
                if account['userId'] == 'user':
                    user_found = True
                    print(f"✅ Found 'user': {account['address']}, balance: {account['balance']}")
                elif account['userId'] == 'user15':
                    user15_found = True
                    print(f"✅ Found 'user15': {account['address']}, balance: {account['balance']}")
                    
            if not user_found:
                print("❌ 'user' not found in accounts")
            if not user15_found:
                print("❌ 'user15' not found in accounts")
        else:
            print("❌ 'testAccounts' key not found")
            
    except Exception as e:
        print(f"❌ Error loading file: {e}")
else:
    print(f"❌ File not found: {file_path}")
    print(f"Files in current directory:")
    for f in os.listdir('.'):
        print(f"  {f}")
