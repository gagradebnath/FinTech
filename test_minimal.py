#!/usr/bin/env python3

print("Testing minimal imports...")

try:
    import sys
    import os
    sys.path.append(os.path.abspath('.'))
    print("✅ Basic imports OK")
    
    from flask import Flask
    print("✅ Flask import OK")
    
    # Test pymysql directly
    import pymysql
    print("✅ PyMySQL import OK")
    
    # Test database connection directly
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='g85a',
        database='fin_guard',
        cursorclass=pymysql.cursors.DictCursor
    )
    print("✅ Database connection OK")
    
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM users')
    result = cursor.fetchone()
    print(f"✅ Database query OK - User count: {result['count']}")
    conn.close()
    
    # Now try flask app
    from app.config import Config
    print("✅ Config import OK")
    
    # Create minimal Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    print("✅ Flask app creation OK")
    
    print("\n🎉 All minimal tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
