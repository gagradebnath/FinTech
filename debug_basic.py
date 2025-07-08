#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath('.'))

print("Starting basic debug test...")

try:
    print("1. Testing imports...")
    from app import create_app
    print("✅ Flask app import successful")
    
    from app.utils.transaction_utils import send_money
    print("✅ send_money import successful")
    
    print("2. Testing app creation...")
    app = create_app()
    print("✅ App creation successful")
    
    print("3. Testing database connection...")
    with app.app_context():
        conn = app.get_db_connection()
        print("✅ Database connection successful")
        
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as user_count FROM users')
        result = cursor.fetchone()
        print(f"✅ Database query successful - User count: {result['user_count']}")
        conn.close()
    
    print("4. Testing send money function...")
    with app.app_context():
        # Test the function with dummy data
        result = send_money('user', 'user2', 1.0, 'bank', 'test', 'test', 'Transfer')
        print(f"✅ send_money function call successful: {result}")
    
    print("\n✅ All basic tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("Debug test complete.")
