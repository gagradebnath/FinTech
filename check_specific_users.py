import pymysql

# Database connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='g85a',
    database='fin_guard',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        # Check for specific users from the transaction log
        test_users = ['user', 'user15']
        
        for user_id in test_users:
            cursor.execute('SELECT id, first_name, last_name, balance FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            
            if user:
                balance = user.get('balance', 0) or 0
                print(f'✅ User "{user_id}" exists: {user.get("first_name", "")} {user.get("last_name", "")} (Balance: ${balance})')
            else:
                print(f'❌ User "{user_id}" does not exist in database')
        
        # Also check how many users start with "user"
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE id LIKE "user%"')
        user_count = cursor.fetchone()
        print(f'\n📊 Total users with ID starting with "user": {user_count["count"]}')
        
        # Show some examples
        cursor.execute('SELECT id, first_name, last_name FROM users WHERE id LIKE "user%" ORDER BY id LIMIT 10')
        users = cursor.fetchall()
        print('First 10 users with "user" prefix:')
        for user in users:
            print(f'  - {user["id"]}: {user.get("first_name", "")} {user.get("last_name", "")}')

finally:
    conn.close()
