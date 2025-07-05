import pymysql
from datetime import date, datetime, timedelta
import uuid
import random
import os
import sys

# Windows Unicode print handling
def safe_print(message):
    """Safely print Unicode messages on Windows"""
    try:
        print(message)
    except UnicodeEncodeError:
        # Replace Unicode characters with ASCII equivalents for Windows CMD
        message = message.replace('✅', '[OK]').replace('❌', '[ERROR]').replace('⚠️', '[WARNING]').replace('ℹ️', '[INFO]')
        print(message)

# MySQL Database Configuration
# Priority: Environment variables > mysql_config.py > defaults
def get_mysql_config():
    """Get MySQL configuration from environment variables or config file"""
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '',
        'database': 'fin_guard',
        'charset': 'utf8mb4'
    }
    
    # Try to load from mysql_config.py file first
    try:
        from mysql_config import MYSQL_CONFIG as file_config
        config.update(file_config)
        safe_print("✅ Loaded configuration from mysql_config.py")
    except ImportError:
        pass  # File doesn't exist, use environment variables or defaults
    
    # Override with environment variables if they exist
    env_config = {
        'host': os.environ.get('MYSQL_HOST'),
        'port': os.environ.get('MYSQL_PORT'),
        'user': os.environ.get('MYSQL_USER'),
        'password': os.environ.get('MYSQL_PASSWORD'),
        'database': os.environ.get('MYSQL_DATABASE'),
    }
    
    # Only override if environment variable is set and not empty
    for key, value in env_config.items():
        if value:
            if key == 'port':
                config[key] = int(value)
            else:
                config[key] = value
    
    return config

MYSQL_CONFIG = get_mysql_config()

# Path to your MySQL schema file
SCHEMA_PATH = 'DatabaseSchema_MySQL.sql'

def print_config():
    """Print the current configuration (hiding password)"""
    config_display = MYSQL_CONFIG.copy()
    config_display['password'] = '[HIDDEN]'
    print("Using MySQL Configuration:")
    for key, value in config_display.items():
        print(f"  {key}: {value}")
    print()

def create_database():
    """Create the database if it doesn't exist"""
    config = MYSQL_CONFIG.copy()
    database = config.pop('database')
    
    print(f"Connecting to MySQL server at {config['host']}:{config['port']}...")
    
    try:
        conn = pymysql.connect(**config)
    except Exception as e:
        safe_print(f"❌ Failed to connect to MySQL server: {e}")
        print("Please check:")
        print("- MySQL server is running")
        print("- Host and port are correct")
        print("- Username and password are correct")
        print("- User has permission to create databases")
        raise
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        safe_print(f"✅ Database '{database}' created or already exists.")
    finally:
        conn.close()

def run_schema(cursor):
    """Execute the MySQL schema file"""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Split by semicolon and execute each statement
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        if stmt.strip():
            cursor.execute(stmt)
    print("Schema executed successfully.")

def insert_dummy_data(cursor):
    """Insert dummy data for testing"""
    # Insert roles
    admin_role_id = str(uuid.uuid4())
    agent_role_id = str(uuid.uuid4())
    user_role_id = str(uuid.uuid4())
    
    cursor.execute("INSERT INTO roles (id, name, description) VALUES (%s, %s, %s)", 
                   (admin_role_id, 'admin', 'Administrator'))
    cursor.execute("INSERT INTO roles (id, name, description) VALUES (%s, %s, %s)", 
                   (agent_role_id, 'agent', 'Agent'))
    cursor.execute("INSERT INTO roles (id, name, description) VALUES (%s, %s, %s)", 
                   (user_role_id, 'user', 'Regular User'))

    # Insert users with fixed IDs and passwords
    today = date.today().isoformat()
    cursor.execute("""INSERT INTO users (id, first_name, last_name, dob, age, gender, 
                      marital_status, blood_group, balance, joining_date, role_id) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        ('admin', 'Admin', 'User', '1990-01-01', 35, 'M', 'Single', 'O+', 10000, today, admin_role_id))
    cursor.execute("""INSERT INTO users (id, first_name, last_name, dob, age, gender, 
                      marital_status, blood_group, balance, joining_date, role_id) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        ('agent', 'Agent', 'Smith', '1992-02-02', 33, 'M', 'Married', 'A+', 10000, today, agent_role_id))
    cursor.execute("""INSERT INTO users (id, first_name, last_name, dob, age, gender, 
                      marital_status, blood_group, balance, joining_date, role_id) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        ('user', 'John', 'Doe', '1995-03-03', 30, 'M', 'Single', 'B+', 10000, today, user_role_id))

    # Insert passwords
    cursor.execute('INSERT INTO user_passwords (user_id, password) VALUES (%s, %s)', ('admin', 'admin'))
    cursor.execute('INSERT INTO user_passwords (user_id, password) VALUES (%s, %s)', ('agent', 'agent'))
    cursor.execute('INSERT INTO user_passwords (user_id, password) VALUES (%s, %s)', ('user', 'user'))

    # Insert permissions
    permissions = [
        ('perm_manage_users', 'Manage users'),
        ('perm_manage_agents', 'Manage agents'),
        ('perm_manage_fraud', 'Manage fraud list'),
        ('perm_manage_permissions', 'Manage role permissions'),
        ('perm_add_money', 'Add money'),
        ('perm_cash_out', 'Cash out'),
        ('perm_send_money', 'Send money'),
        ('perm_view_dashboard', 'View dashboard'),
        ('perm_report_fraud', 'Report fraud'),
        ('perm_edit_profile', 'Edit profile'),
    ]
    
    permission_ids = {}
    for perm_name, perm_desc in permissions:
        perm_id = str(uuid.uuid4())
        permission_ids[perm_name] = perm_id
        cursor.execute("INSERT INTO permissions (id, name, description) VALUES (%s, %s, %s)", 
                       (perm_id, perm_name, perm_desc))

    # Assign permissions to roles
    def assign_perms(role_id, perm_names):
        for perm_name in perm_names:
            rp_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO role_permissions (id, role_id, permission_id) VALUES (%s, %s, %s)", 
                           (rp_id, role_id, permission_ids[perm_name]))

    # Admin: all permissions
    assign_perms(admin_role_id, [p[0] for p in permissions])
    # Agent: add_money, cash_out, view_dashboard, edit_profile
    assign_perms(agent_role_id, ['perm_add_money', 'perm_cash_out', 'perm_view_dashboard', 'perm_edit_profile'])
    # User: send_money, view_dashboard, report_fraud, edit_profile
    assign_perms(user_role_id, ['perm_send_money', 'perm_view_dashboard', 'perm_report_fraud', 'perm_edit_profile'])

    print('Dummy data inserted!')
    print('--- LOGIN DETAILS ---')
    print('Admin:   id=admin   password=admin')
    print('Agent:   id=agent   password=agent')
    print('User:    id=user    password=user')
    print('---------------------')

def create_transactions_table(cursor):
    """Create and populate transactions with dummy data"""
    # Insert random transactions for each user
    users = ['admin', 'agent', 'user']
    payment_methods = ['Bank Transfer', 'Credit Card', 'Debit Card', 'Mobile Wallet', 'Cash']
    transaction_types = ['Transfer', 'Deposit', 'Withdrawal', 'Payment', 'Refund']
    locations = ['New York', 'London', 'Tokyo', 'Sydney', 'Paris', 'Berlin', 'Mumbai', 'São Paulo', 'Dubai']
    
    now = datetime.now()
    
    for user in users:
        for _ in range(20):  # 20 dummy transactions per user
            # Generate a random amount between 10 and 1000
            amount = round(random.uniform(10.0, 1000.0), 2)
            
            # Randomly decide if this is a send or receive transaction
            is_sender = random.choice([True, False])
            
            # Set sender and receiver based on transaction type
            if is_sender:
                sender_id = user
                receiver_id = random.choice([u for u in users if u != user])
                amount = -amount  # Negative amount for outgoing
                note = f'Payment to {receiver_id}'
            else:
                sender_id = random.choice([u for u in users if u != user])
                receiver_id = user
                note = f'Payment from {sender_id}'
            
            # Generate a random timestamp within the last 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            transaction_time = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # Random payment method, type, and location
            payment_method = random.choice(payment_methods)
            transaction_type = random.choice(transaction_types)
            location = random.choice(locations)
            
            # Insert the transaction
            insert_dummy_transaction(
                cursor, 
                amount, 
                payment_method, 
                transaction_time, 
                sender_id, 
                receiver_id, 
                note, 
                transaction_type, 
                location
            )

def insert_dummy_transaction(cursor, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location):
    """Insert a single transaction"""
    transaction_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO transactions (id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (transaction_id, amount, payment_method, timestamp, sender_id, receiver_id, note, type, location)
    )

def create_budgets_table(cursor):
    """Create and populate budgets with dummy data"""
    # Insert dummy budgets for each user
    users = ['admin', 'agent', 'user']
    currencies = ['USD', 'EUR', 'GBP', 'JPY']
    income_sources = ['Salary', 'Freelance', 'Investment', 'Business']
    
    for user in users:
        for i in range(2):  # 2 budgets per user
            budget_id = str(uuid.uuid4())
            name = f'{user.title()} Budget {i+1}'
            currency = random.choice(currencies)
            income_source = random.choice(income_sources)
            amount = round(random.uniform(3000.0, 10000.0), 2)
            
            cursor.execute("""
                INSERT INTO budgets (id, user_id, name, currency, income_source, amount) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (budget_id, user, name, currency, income_source, amount)
            )

def main():
    """Main function to set up the database"""
    print("=" * 50)
    print("FinGuard MySQL Database Setup")
    print("=" * 50)
    
    # Display configuration
    print_config()
    
    # Validate required configuration
    if not MYSQL_CONFIG['password']:
        safe_print("❌ ERROR: MySQL password is required")
        print("Please set the MYSQL_PASSWORD environment variable")
        return
    
    try:
        # Create database
        create_database()
        
        # Connect to the database
        print(f"Connecting to database '{MYSQL_CONFIG['database']}'...")
        conn = pymysql.connect(**MYSQL_CONFIG)
        
        try:
            with conn.cursor() as cursor:
                print("📋 Running schema...")
                run_schema(cursor)
                
                print("📊 Inserting dummy data...")
                insert_dummy_data(cursor)
                
                print("💳 Creating transactions...")
                create_transactions_table(cursor)
                
                print("📈 Creating budgets...")
                create_budgets_table(cursor)
                
            conn.commit()
            print()
            print("=" * 50)
            safe_print("✅ Database seeding completed successfully!")
            print("=" * 50)
            print("📊 Created:")
            print("  - 20 random transactions per user")
            print("  - 2 budgets per user")
            print("  - Sample user accounts (admin, agent, user)")
            print()
            print("🔑 Default login credentials:")
            print("  - Admin: username=admin, password=admin")
            print("  - Agent: username=agent, password=agent")
            print("  - User:  username=user,  password=user")
            print("=" * 50)
            
        except Exception as e:
            conn.rollback()
            safe_print(f"❌ Database operation failed: {e}")
            raise
        finally:
            conn.close()
            
    except Exception as e:
        safe_print(f"❌ Setup failed: {e}")
        print()
        print("💡 Troubleshooting tips:")
        print("  - Ensure MySQL server is running")
        print("  - Check your credentials are correct")
        print("  - Verify the user has database creation permissions")
        print("  - Check network connectivity to MySQL server")
        raise

if __name__ == '__main__':
    main()
