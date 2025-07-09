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
        # Check balance statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_users,
                SUM(COALESCE(balance, 0)) as total_balance,
                AVG(COALESCE(balance, 0)) as avg_balance,
                MIN(COALESCE(balance, 0)) as min_balance,
                MAX(COALESCE(balance, 0)) as max_balance
            FROM users
        ''')
        stats = cursor.fetchone()
        
        print("💰 Database Balance Statistics:")
        print(f"  Total Users: {stats['total_users']}")
        print(f"  Total Balance: ${stats['total_balance']:,.2f}")
        print(f"  Average Balance: ${stats['avg_balance']:,.2f}")
        print(f"  Min Balance: ${stats['min_balance']:,.2f}")
        print(f"  Max Balance: ${stats['max_balance']:,.2f}")
        
        # Show some users with balances
        cursor.execute('''
            SELECT id, first_name, last_name, COALESCE(balance, 0) as balance
            FROM users 
            WHERE COALESCE(balance, 0) > 0
            ORDER BY balance DESC
            LIMIT 10
        ''')
        users = cursor.fetchall()
        
        print(f"\n🏆 Top 10 Users by Balance:")
        for user in users:
            print(f"  {user['id']}: ${user['balance']:,.2f} ({user.get('first_name', '')} {user.get('last_name', '')})")

finally:
    conn.close()
