#!/usr/bin/env python3

import pymysql

def check_null_balances():
    
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='g85a',
            database='fin_guard',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        # Check for NULL balances
        cursor.execute('SELECT id, first_name, last_name, balance FROM users WHERE balance IS NULL')
        null_users = cursor.fetchall()
        print(f'Users with NULL balance: {len(null_users)}')
        for user in null_users:
            print(f"  - User {user['id']}: {user['first_name']} {user['last_name']} has NULL balance")
        
        # Check for "None" string balances
        cursor.execute('SELECT id, first_name, last_name, balance FROM users WHERE balance = "None"')
        none_users = cursor.fetchall()
        print(f'Users with "None" string balance: {len(none_users)}')
        for user in none_users:
            print(f"  - User {user['id']}: {user['first_name']} {user['last_name']} has \"None\" balance")
        
        # Check all users
        cursor.execute('SELECT id, first_name, last_name, balance FROM users')
        all_users = cursor.fetchall()
        print(f'\nAll users ({len(all_users)} total):')
        for user in all_users:
            print(f"  - User {user['id']}: {user['first_name']} {user['last_name']} has balance: {user['balance']} (type: {type(user['balance'])})")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking balances: {e}")

if __name__ == "__main__":
    check_null_balances()
