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
        cursor.execute('SELECT COUNT(*) as count FROM users')
        user_count = cursor.fetchone()
        print(f'Total users in database: {user_count["count"]}')
        
        cursor.execute('SELECT id, first_name, last_name FROM users ORDER BY id LIMIT 10')
        users = cursor.fetchall()
        print('First 10 users:')
        for user in users:
            print(f'  - {user["id"]}: {user.get("first_name", "")} {user.get("last_name", "")}')
finally:
    conn.close()
