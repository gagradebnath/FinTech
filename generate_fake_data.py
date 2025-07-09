
import os
import sys
import uuid
import random
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
import hashlib

# Configuration
NUM_USERS = 500          # Number of regular users to create
NUM_AGENTS = 50          # Number of agents to create
NUM_ADMINS = 5           # Number of admins to create
NUM_TRANSACTIONS_PER_USER = 50  # Average transactions per user
NUM_BUDGETS_PER_USER = 3        # Average budgets per user

def safe_print(message):
    """Safely print messages with ASCII fallback"""
    message = message.replace('[OK]', '[OK]').replace('[ERROR]', '[ERROR]').replace('[WARNING]', '[WARNING]').replace('[INFO]', '[INFO]')
    print(message)

def get_mysql_config():
    """Get MySQL configuration from environment variables"""
    pwd = str(input("Enter MySQL password: "))
    config = {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'port': int(os.environ.get('MYSQL_PORT', 3306)),
        'user': os.environ.get('MYSQL_USER', 'root'),

        'password': os.environ.get('MYSQL_PASSWORD', pwd),
        'database': os.environ.get('MYSQL_DATABASE', 'fin_guard'),
        'charset': 'utf8mb4'
    }
    return config

# Fake data generators
class FakeDataGenerator:
    def __init__(self):
        # Names data
        self.first_names_male = [
            'James', 'Robert', 'John', 'Michael', 'David', 'William', 'Richard', 'Charles', 'Joseph', 'Thomas',
            'Christopher', 'Daniel', 'Paul', 'Mark', 'Donald', 'Steven', 'Andrew', 'Kenneth', 'Joshua', 'Kevin',
            'Brian', 'George', 'Timothy', 'Ronald', 'Jason', 'Edward', 'Jeffrey', 'Ryan', 'Jacob', 'Gary',
            'Nicholas', 'Eric', 'Jonathan', 'Stephen', 'Larry', 'Justin', 'Scott', 'Brandon', 'Benjamin', 'Samuel',
            'Frank', 'Gregory', 'Raymond', 'Alexander', 'Patrick', 'Jack', 'Dennis', 'Jerry', 'Tyler', 'Aaron'
        ]
        
        self.first_names_female = [
            'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen',
            'Nancy', 'Lisa', 'Betty', 'Helen', 'Sandra', 'Donna', 'Carol', 'Ruth', 'Sharon', 'Michelle',
            'Laura', 'Sarah', 'Kimberly', 'Deborah', 'Dorothy', 'Lisa', 'Nancy', 'Karen', 'Betty', 'Helen',
            'Sandra', 'Donna', 'Carol', 'Ruth', 'Sharon', 'Michelle', 'Laura', 'Emily', 'Ashley', 'Emma',
            'Olivia', 'Sophia', 'Abigail', 'Isabella', 'Madison', 'Mia', 'Charlotte', 'Harper', 'Sofia', 'Avery'
        ]
        
        self.last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
            'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
            'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
            'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts'
        ]
        
        # Address data
        self.countries = [
            'United States', 'Canada', 'United Kingdom', 'Australia', 'Germany', 'France', 'Japan', 'Italy',
            'Spain', 'Netherlands', 'Sweden', 'Norway', 'Denmark', 'Finland', 'Switzerland', 'Austria',
            'Belgium', 'Portugal', 'Ireland', 'New Zealand'
        ]
        
        self.divisions = {
            'United States': ['California', 'Texas', 'Florida', 'New York', 'Pennsylvania', 'Illinois'],
            'Canada': ['Ontario', 'Quebec', 'British Columbia', 'Alberta', 'Manitoba', 'Saskatchewan'],
            'United Kingdom': ['England', 'Scotland', 'Wales', 'Northern Ireland'],
            'Australia': ['New South Wales', 'Victoria', 'Queensland', 'Western Australia', 'South Australia']
        }
        
        self.districts = [
            'Downtown', 'Midtown', 'Uptown', 'Westside', 'Eastside', 'Northside', 'Southside',
            'Central District', 'Business District', 'Financial District', 'Tech District', 'Arts District'
        ]
        
        self.areas = [
            'Maple Street', 'Oak Avenue', 'Pine Road', 'Cedar Lane', 'Elm Drive', 'Main Street',
            'First Avenue', 'Second Street', 'Park Boulevard', 'River Road', 'Hill Street', 'Valley View'
        ]
        
        # Financial data
        self.currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'SEK', 'NOK', 'DKK']
        
        self.income_sources = [
            'Full-time Employment', 'Part-time Employment', 'Freelancing', 'Consulting',
            'Business Ownership', 'Investment Income', 'Rental Income', 'Retirement Benefits',
            'Government Benefits', 'Scholarship/Grant', 'Side Hustle', 'Contract Work'
        ]
        
        self.payment_methods = [
            'Bank Transfer', 'Credit Card', 'Debit Card', 'Mobile Wallet', 'Cash',
            'PayPal', 'Venmo', 'Zelle', 'Wire Transfer', 'Check', 'Cryptocurrency'
        ]
        
        self.transaction_types = ['Transfer', 'Deposit', 'Withdrawal', 'Payment', 'Refund']
        
        self.locations = [
            'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX', 'Phoenix, AZ',
            'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA', 'Dallas, TX', 'San Jose, CA',
            'London, UK', 'Paris, France', 'Tokyo, Japan', 'Sydney, Australia', 'Toronto, Canada',
            'Berlin, Germany', 'Madrid, Spain', 'Rome, Italy', 'Amsterdam, Netherlands', 'Stockholm, Sweden'
        ]
        
        # Expense categories from budget.js
        self.expense_categories = [
            'Housing', 'Utilities', 'Groceries', 'Transportation', 'Healthcare',
            'Insurance', 'Education', 'Savings', 'Debt Payments', 'Personal Care',
            'Entertainment', 'Dining Out', 'Clothing', 'Gifts & Donations', 'Travel',
            'Childcare', 'Pets', 'Other'
        ]
        
        # Expense items for each category
        self.expense_items = {
            'Housing': ['Rent', 'Mortgage', 'Property Tax', 'HOA Fees', 'Home Insurance', 'Maintenance'],
            'Utilities': ['Electricity', 'Gas', 'Water', 'Internet', 'Cable TV', 'Trash Service'],
            'Groceries': ['Supermarket', 'Farmers Market', 'Bulk Store', 'Organic Foods'],
            'Transportation': ['Gas', 'Public Transit', 'Car Payment', 'Car Insurance', 'Parking', 'Uber/Lyft'],
            'Healthcare': ['Doctor Visits', 'Prescription Drugs', 'Dental Care', 'Vision Care', 'Health Insurance'],
            'Insurance': ['Life Insurance', 'Disability Insurance', 'Home Insurance', 'Car Insurance'],
            'Education': ['Tuition', 'Books', 'Supplies', 'Online Courses', 'Certification'],
            'Savings': ['Emergency Fund', 'Retirement', 'Investment Account', 'Vacation Fund'],
            'Debt Payments': ['Credit Card', 'Student Loan', 'Personal Loan', 'Car Loan'],
            'Personal Care': ['Haircut', 'Skincare', 'Gym Membership', 'Clothing', 'Shoes'],
            'Entertainment': ['Movies', 'Concerts', 'Gaming', 'Streaming Services', 'Books'],
            'Dining Out': ['Restaurants', 'Fast Food', 'Coffee Shop', 'Food Delivery'],
            'Clothing': ['Work Clothes', 'Casual Wear', 'Shoes', 'Accessories'],
            'Gifts & Donations': ['Birthday Gifts', 'Holiday Gifts', 'Charity', 'Religious Donations'],
            'Travel': ['Flights', 'Hotels', 'Car Rental', 'Travel Insurance', 'Vacation Activities'],
            'Childcare': ['Daycare', 'Babysitter', 'School Fees', 'Extracurricular Activities'],
            'Pets': ['Pet Food', 'Veterinary Care', 'Pet Insurance', 'Pet Supplies', 'Grooming'],
            'Other': ['Miscellaneous', 'Unexpected Expenses', 'Bank Fees', 'Subscriptions']
        }
        
        # Demographics
        self.genders = ['Male', 'Female', 'Other']
        self.marital_statuses = ['Single', 'Married', 'Divorced', 'Widowed', 'Separated']
        self.blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        # Financial habits
        self.monthly_incomes = ['Under $2,000', '$2,000-$3,999', '$4,000-$5,999', '$6,000-$7,999', '$8,000+']
        self.living_situations = ['Own Home', 'Rent Apartment', 'Rent House', 'Live with Family', 'Student Housing']
        self.transport_modes = ['Own Car', 'Public Transport', 'Bicycle', 'Walking', 'Rideshare', 'Motorcycle']
        self.eating_frequencies = ['Daily', '3-4 times a week', '1-2 times a week', 'Weekly', 'Rarely', 'Never']
        self.savings_types = ['High-yield Savings', 'Investment Account', 'Retirement Fund', 'Emergency Fund', 'No Savings']
        self.financial_goals = ['Buy a House', 'Retirement', 'Emergency Fund', 'Vacation', 'Education', 'Start Business', 'Pay off Debt']
    
    def generate_user_id(self):
        """Generate a unique user ID"""
        return str(uuid.uuid4())
    
    def generate_name(self, gender=None):
        """Generate a random name"""
        if gender is None:
            gender = random.choice(['Male', 'Female'])
        
        if gender == 'Male':
            first_name = random.choice(self.first_names_male)
        else:
            first_name = random.choice(self.first_names_female)
        
        last_name = random.choice(self.last_names)
        return first_name, last_name
    
    def generate_email(self, first_name, last_name, user_id=None):
        """Generate unique email address"""
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'example.com']
        
        # Use user_id to ensure uniqueness if provided
        if user_id:
            email_base = f"{user_id}"
        else:
            # Various email formats with random numbers for uniqueness
            formats = [
                f"{first_name.lower()}.{last_name.lower()}.{random.randint(1000, 9999)}",
                f"{first_name.lower()}{last_name.lower()}{random.randint(100, 999)}",
                f"{first_name[0].lower()}{last_name.lower()}{random.randint(10, 99)}",
                f"{first_name.lower()}{random.randint(1000, 9999)}"
            ]
            email_base = random.choice(formats)
        
        domain = random.choice(domains)
        return f"{email_base}@{domain}"
    
    def generate_phone(self, user_id=None):
        """Generate unique phone number"""
        if user_id:
            # Use hash of user_id to generate a consistent but unique number
            hash_obj = hashlib.md5(user_id.encode())
            hash_num = int(hash_obj.hexdigest()[:8], 16)
            area_code = 200 + (hash_num % 800)  # 200-999
            exchange = 200 + ((hash_num >> 8) % 800)  # 200-999
            number = 1000 + ((hash_num >> 16) % 9000)  # 1000-9999
            return f"+1-{area_code}-{exchange}-{number}"
        else:
            return f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
    
    def generate_date_of_birth(self, min_age=18, max_age=80):
        """Generate date of birth"""
        today = date.today()
        age = random.randint(min_age, max_age)
        birth_year = today.year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Safe day for all months
        return date(birth_year, birth_month, birth_day), age
    
    def generate_address(self):
        """Generate address"""
        country = random.choice(self.countries)
        
        if country in self.divisions:
            division = random.choice(self.divisions[country])
        else:
            division = f"Province {random.randint(1, 10)}"
        
        district = random.choice(self.districts)
        area = f"{random.randint(100, 9999)} {random.choice(self.areas)}"
        
        return country, division, district, area
    
    def generate_balance(self, user_type='user'):
        """Generate account balance based on user type"""
        if user_type == 'admin':
            return round(random.uniform(50000, 200000), 2)
        elif user_type == 'agent':
            return round(random.uniform(10000, 100000), 2)
        else:  # regular user
            return round(random.uniform(100, 50000), 2)

# Main database seeding functions
def create_connection():
    """Create database connection"""
    try:
        import pymysql
    except ImportError:
        safe_print("[ERROR] PyMySQL not installed. Please install it: pip install PyMySQL")
        sys.exit(1)
    
    config = get_mysql_config()
    
    if not config['password']:
        safe_print("[ERROR] MySQL password is required. Set MYSQL_PASSWORD environment variable.")
        sys.exit(1)
    
    try:
        connection = pymysql.connect(**config)
        safe_print(f"[OK] Connected to MySQL database: {config['database']}")
        return connection
    except Exception as e:
        safe_print(f"[ERROR] Failed to connect to database: {e}")
        sys.exit(1)

def clear_existing_data(cursor):
    """Clear existing data from all tables"""
    safe_print("[INFO] Clearing existing data...")
    
    # Disable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    tables = [
        'user_passwords', 'user_expense_habit', 'budget_expense_items',
        'admin_logs', 'blockchain_transactions', 'blockchain', 'transactions',
        'contact_info', 'fraud_list', 'budget_expense_categories', 'budgets',
        'addresses', 'role_permissions', 'permissions', 'users', 'roles'
    ]
    
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            safe_print(f"[OK] Cleared table: {table}")
        except Exception as e:
            safe_print(f"[WARNING] Could not clear table {table}: {e}")
    
    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

def seed_roles_and_permissions(cursor, generator):
    """Seed roles and permissions"""
    safe_print("[INFO] Seeding roles and permissions...")
    
    # Create roles
    admin_role_id = str(uuid.uuid4())
    agent_role_id = str(uuid.uuid4())
    user_role_id = str(uuid.uuid4())
    
    roles = [
        (admin_role_id, 'admin', 'System Administrator with full access'),
        (agent_role_id, 'agent', 'Financial Agent with limited admin access'),
        (user_role_id, 'user', 'Regular User with basic access')
    ]
    
    for role_data in roles:
        cursor.execute(
            "INSERT INTO roles (id, name, description) VALUES (%s, %s, %s)",
            role_data
        )
    
    # Create permissions
    permissions = [
        ('perm_manage_users', 'Manage user accounts'),
        ('perm_manage_agents', 'Manage agent accounts'),
        ('perm_manage_fraud', 'Manage fraud reports'),
        ('perm_manage_permissions', 'Manage role permissions'),
        ('perm_view_admin_logs', 'View administrative logs'),
        ('perm_add_money', 'Add money to accounts'),
        ('perm_cash_out', 'Process cash out requests'),
        ('perm_send_money', 'Send money transfers'),
        ('perm_view_dashboard', 'View dashboard'),
        ('perm_report_fraud', 'Report fraud'),
        ('perm_edit_profile', 'Edit user profile'),
        ('perm_view_transactions', 'View transaction history'),
        ('perm_create_budget', 'Create and manage budgets'),
        ('perm_view_expense_habits', 'View expense habit analysis')
    ]
    
    permission_ids = {}
    for perm_name, perm_desc in permissions:
        perm_id = str(uuid.uuid4())
        permission_ids[perm_name] = perm_id
        cursor.execute(
            "INSERT INTO permissions (id, name, description) VALUES (%s, %s, %s)",
            (perm_id, perm_name, perm_desc)
        )
    
    # Assign permissions to roles
    def assign_permissions(role_id, perm_names):
        for perm_name in perm_names:
            rp_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO role_permissions (id, role_id, permission_id) VALUES (%s, %s, %s)",
                (rp_id, role_id, permission_ids[perm_name])
            )
    
    # Admin: all permissions
    assign_permissions(admin_role_id, [p[0] for p in permissions])
    
    # Agent: specific permissions
    agent_perms = [
        'perm_add_money', 'perm_cash_out', 'perm_view_dashboard',
        'perm_edit_profile', 'perm_view_transactions', 'perm_manage_fraud'
    ]
    assign_permissions(agent_role_id, agent_perms)
    
    # User: basic permissions
    user_perms = [
        'perm_send_money', 'perm_view_dashboard', 'perm_report_fraud',
        'perm_edit_profile', 'perm_view_transactions', 'perm_create_budget',
        'perm_view_expense_habits'
    ]
    assign_permissions(user_role_id, user_perms)
    
    safe_print(f"[OK] Created {len(roles)} roles and {len(permissions)} permissions")
    return {'admin': admin_role_id, 'agent': agent_role_id, 'user': user_role_id}

def seed_users(cursor, generator, role_ids):
    """Seed users with fake data"""
    safe_print("[INFO] Generating users...")
    
    all_users = []
    today = date.today()
    
    # Create admin users
    for i in range(NUM_ADMINS):
        user_id = f"admin{i+1}" if i > 0 else "admin"
        first_name, last_name = generator.generate_name()
        dob, age = generator.generate_date_of_birth(25, 60)
        
        user_data = (
            user_id, first_name, last_name, dob, age,
            random.choice(generator.genders),
            random.choice(generator.marital_statuses),
            random.choice(generator.blood_groups),
            generator.generate_balance('admin'),
            today, role_ids['admin']
        )
        
        cursor.execute("""
            INSERT INTO users (id, first_name, last_name, dob, age, gender, 
                             marital_status, blood_group, balance, joining_date, role_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, user_data)
        
        # Create password (same as user_id for simplicity)
        cursor.execute(
            "INSERT INTO user_passwords (user_id, password) VALUES (%s, %s)",
            (user_id, user_id)
        )
        
        all_users.append((user_id, 'admin', first_name, last_name))
    
    # Create agent users
    for i in range(NUM_AGENTS):
        user_id = f"agent{i+1}" if i > 0 else "agent"
        first_name, last_name = generator.generate_name()
        dob, age = generator.generate_date_of_birth(22, 55)
        
        user_data = (
            user_id, first_name, last_name, dob, age,
            random.choice(generator.genders),
            random.choice(generator.marital_statuses),
            random.choice(generator.blood_groups),
            generator.generate_balance('agent'),
            today, role_ids['agent']
        )
        
        cursor.execute("""
            INSERT INTO users (id, first_name, last_name, dob, age, gender, 
                             marital_status, blood_group, balance, joining_date, role_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, user_data)
        
        cursor.execute(
            "INSERT INTO user_passwords (user_id, password) VALUES (%s, %s)",
            (user_id, user_id)
        )
        
        all_users.append((user_id, 'agent', first_name, last_name))
    
    # Create regular users
    for i in range(NUM_USERS):
        user_id = f"user{i+1}" if i > 0 else "user"
        first_name, last_name = generator.generate_name()
        dob, age = generator.generate_date_of_birth(18, 70)
        
        user_data = (
            user_id, first_name, last_name, dob, age,
            random.choice(generator.genders),
            random.choice(generator.marital_statuses),
            random.choice(generator.blood_groups),
            generator.generate_balance('user'),
            today, role_ids['user']
        )
        
        cursor.execute("""
            INSERT INTO users (id, first_name, last_name, dob, age, gender, 
                             marital_status, blood_group, balance, joining_date, role_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, user_data)
        
        cursor.execute(
            "INSERT INTO user_passwords (user_id, password) VALUES (%s, %s)",
            (user_id, user_id)
        )
        
        all_users.append((user_id, 'user', first_name, last_name))
    
    safe_print(f"[OK] Created {len(all_users)} users ({NUM_ADMINS} admins, {NUM_AGENTS} agents, {NUM_USERS} regular users)")
    return all_users

def seed_addresses_and_contacts(cursor, generator, users):
    """Seed addresses and contact information"""
    safe_print("[INFO] Generating addresses and contact information...")
    
    for user_id, user_type, first_name, last_name in users:
        # Create address
        country, division, district, area = generator.generate_address()
        address_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO addresses (id, country, division, district, area)
            VALUES (%s, %s, %s, %s, %s)
        """, (address_id, country, division, district, area))
        
        # Create contact info
        email = generator.generate_email(first_name, last_name, user_id)
        phone = generator.generate_phone(user_id)
        contact_id = str(uuid.uuid4())
        
        try:
            cursor.execute("""
                INSERT INTO contact_info (id, user_id, email, phone, address_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (contact_id, user_id, email, phone, address_id))
        except Exception as e:
            # If there's still a duplicate, add a timestamp to make it unique
            if "Duplicate entry" in str(e):
                timestamp_suffix = str(int(datetime.now().timestamp()))
                email = f"{email.split('@')[0]}.{timestamp_suffix}@{email.split('@')[1]}"
                cursor.execute("""
                    INSERT INTO contact_info (id, user_id, email, phone, address_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (contact_id, user_id, email, phone, address_id))
            else:
                raise e
    
    safe_print(f"[OK] Created addresses and contact info for {len(users)} users")

def seed_transactions(cursor, generator, users):
    """Seed realistic transactions"""
    safe_print("[INFO] Generating transactions...")
    
    user_ids = [user[0] for user in users]
    total_transactions = 0
    
    for user_id, user_type, _, _ in users:
        # Number of transactions varies by user type
        if user_type == 'admin':
            num_transactions = random.randint(100, 200)
        elif user_type == 'agent':
            num_transactions = random.randint(50, 150)
        else:
            num_transactions = random.randint(10, NUM_TRANSACTIONS_PER_USER)
        
        # Generate transactions over the past year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        for _ in range(num_transactions):
            # Random timestamp
            random_days = random.randint(0, 365)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            timestamp = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
            
            # Transaction details
            transaction_type = random.choice(generator.transaction_types)
            payment_method = random.choice(generator.payment_methods)
            location = random.choice(generator.locations)
            
            # Amount and participants based on transaction type
            if transaction_type == 'Deposit':
                amount = round(random.uniform(50, 5000), 2)
                sender_id = None  # External deposit
                receiver_id = user_id
                note = f"Deposit via {payment_method}"
            elif transaction_type == 'Withdrawal':
                amount = round(random.uniform(20, 1000), 2)
                sender_id = user_id
                receiver_id = None  # External withdrawal
                note = f"Withdrawal via {payment_method}"
            else:  # Transfer, Payment, Refund
                amount = round(random.uniform(10, 2000), 2)
                # Choose random other user
                other_users = [uid for uid in user_ids if uid != user_id]
                other_user = random.choice(other_users)
                
                if random.choice([True, False]):  # User is sender
                    sender_id = user_id
                    receiver_id = other_user
                    note = f"{transaction_type} to {other_user}"
                else:  # User is receiver
                    sender_id = other_user
                    receiver_id = user_id
                    note = f"{transaction_type} from {other_user}"
            
            # Insert transaction
            transaction_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO transactions (id, amount, payment_method, timestamp, 
                                        sender_id, receiver_id, note, type, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (transaction_id, amount, payment_method, timestamp, 
                  sender_id, receiver_id, note, transaction_type, location))
            
            total_transactions += 1
    
    safe_print(f"[OK] Created {total_transactions} transactions")

def seed_budgets(cursor, generator, users):
    """Seed budgets with categories and items"""
    safe_print("[INFO] Generating budgets...")
    
    total_budgets = 0
    total_categories = 0
    total_items = 0
    
    for user_id, user_type, _, _ in users:
        # Number of budgets per user
        num_budgets = random.randint(1, NUM_BUDGETS_PER_USER)
        
        for budget_num in range(num_budgets):
            budget_id = str(uuid.uuid4())
            budget_name = f"Budget {budget_num + 1}" if num_budgets > 1 else "My Budget"
            currency = random.choice(generator.currencies)
            income_source = random.choice(generator.income_sources)
            
            # Total budget amount
            if user_type == 'admin':
                total_amount = round(random.uniform(8000, 20000), 2)
            elif user_type == 'agent':
                total_amount = round(random.uniform(4000, 12000), 2)
            else:
                total_amount = round(random.uniform(2000, 8000), 2)
            
            # Budget date range
            start_date = date.today() - timedelta(days=random.randint(0, 90))
            end_date = start_date + timedelta(days=random.randint(30, 365))
            
            cursor.execute("""
                INSERT INTO budgets (id, user_id, name, currency, income_source, 
                                   amount, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (budget_id, user_id, budget_name, currency, income_source, 
                  total_amount, start_date, end_date))
            
            total_budgets += 1
            
            # Create expense categories
            num_categories = random.randint(3, 8)
            selected_categories = random.sample(generator.expense_categories, num_categories)
            
            remaining_amount = total_amount
            
            for i, category_name in enumerate(selected_categories):
                category_id = str(uuid.uuid4())
                
                # Allocate amount to category
                if i == len(selected_categories) - 1:  # Last category gets remaining amount
                    category_amount = remaining_amount
                else:
                    # Random percentage of remaining amount
                    percentage = random.uniform(0.1, 0.4)
                    category_amount = round(remaining_amount * percentage, 2)
                    remaining_amount -= category_amount
                
                cursor.execute("""
                    INSERT INTO budget_expense_categories (id, budget_id, category_name, amount)
                    VALUES (%s, %s, %s, %s)
                """, (category_id, budget_id, category_name, category_amount))
                
                total_categories += 1
                
                # Create expense items for this category
                available_items = generator.expense_items.get(category_name, ['General Expense'])
                num_items = random.randint(1, min(4, len(available_items)))
                selected_items = random.sample(available_items, num_items)
                
                item_remaining = category_amount
                
                for j, item_name in enumerate(selected_items):
                    item_id = str(uuid.uuid4())
                    
                    # Allocate amount to item
                    if j == len(selected_items) - 1:  # Last item gets remaining amount
                        item_amount = item_remaining
                    else:
                        item_percentage = random.uniform(0.2, 0.6)
                        item_amount = round(item_remaining * item_percentage, 2)
                        item_remaining -= item_amount
                    
                    details = f"{item_name} for {category_name} category"
                    
                    cursor.execute("""
                        INSERT INTO budget_expense_items (id, category_id, name, amount, details)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (item_id, category_id, item_name, item_amount, details))
                    
                    total_items += 1
    
    safe_print(f"[OK] Created {total_budgets} budgets with {total_categories} categories and {total_items} items")

def seed_expense_habits(cursor, generator, users):
    """Seed user expense habits"""
    safe_print("[INFO] Generating expense habits...")
    
    for user_id, user_type, _, _ in users:
        # Generate expense habit data
        habit_id = str(uuid.uuid4())
        timestamp = datetime.now() - timedelta(days=random.randint(1, 30))
        
        monthly_income = random.choice(generator.monthly_incomes)
        earning_member = random.choice([True, False])
        dependents = random.randint(0, 5) if earning_member else 0
        living_situation = random.choice(generator.living_situations)
        
        # Rent based on income level
        income_multiplier = {
            'Under $2,000': 0.4,
            '$2,000-$3,999': 0.3,
            '$4,000-$5,999': 0.25,
            '$6,000-$7,999': 0.2,
            '$8,000+': 0.15
        }
        base_rent = 1500 * income_multiplier.get(monthly_income, 0.3)
        rent = round(random.uniform(base_rent * 0.7, base_rent * 1.3), 2)
        
        transport_mode = random.choice(generator.transport_modes)
        transport_cost = round(random.uniform(50, 500), 2)
        eating_out_frequency = random.choice(generator.eating_frequencies)
        grocery_cost = round(random.uniform(200, 800), 2)
        utilities_cost = round(random.uniform(100, 400), 2)
        mobile_internet_cost = round(random.uniform(30, 150), 2)
        
        # Subscriptions (JSON format)
        possible_subscriptions = [
            'Netflix', 'Spotify', 'Amazon Prime', 'Disney+', 'YouTube Premium',
            'Adobe Creative', 'Microsoft Office', 'Gym Membership', 'News Subscription'
        ]
        num_subscriptions = random.randint(0, 5)
        subscriptions = random.sample(possible_subscriptions, num_subscriptions)
        subscriptions_json = json.dumps(subscriptions)
        
        savings = random.choice(generator.savings_types)
        
        # Investments (text format)
        investments_options = [
            'Stocks and ETFs', '401k/Retirement Account', 'Real Estate', 'Bonds',
            'Cryptocurrency', 'Mutual Funds', 'Savings Account', 'No Investments'
        ]
        investments = ', '.join(random.sample(investments_options, random.randint(1, 3)))
        
        loans = random.choice([True, False])
        loan_payment = round(random.uniform(200, 1500), 2) if loans else 0
        
        financial_goal = random.choice(generator.financial_goals)
        
        cursor.execute("""
            INSERT INTO user_expense_habit (
                id, user_id, timestamp, monthly_income, earning_member, dependents,
                living_situation, rent, transport_mode, transport_cost, eating_out_frequency,
                grocery_cost, utilities_cost, mobile_internet_cost, subscriptions,
                savings, investments, loans, loan_payment, financial_goal
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            habit_id, user_id, timestamp, monthly_income, earning_member, dependents,
            living_situation, rent, transport_mode, transport_cost, eating_out_frequency,
            grocery_cost, utilities_cost, mobile_internet_cost, subscriptions_json,
            savings, investments, loans, loan_payment, financial_goal
        ))
    
    safe_print(f"[OK] Created expense habits for {len(users)} users")

def seed_fraud_reports(cursor, generator, users):
    """Seed fraud reports"""
    safe_print("[INFO] Generating fraud reports...")
    
    user_ids = [user[0] for user in users]
    
    # Generate some fraud reports (small percentage)
    num_reports = max(1, len(users) // 20)  # About 5% of users report fraud
    
    for _ in range(num_reports):
        report_id = str(uuid.uuid4())
        reporter_id = random.choice(user_ids)
        
        # Don't let users report themselves
        potential_reported = [uid for uid in user_ids if uid != reporter_id]
        reported_user_id = random.choice(potential_reported)
        
        reasons = [
            'Suspicious transaction activity',
            'Unauthorized account access',
            'Phishing attempt',
            'Identity theft',
            'Fraudulent payment request',
            'Suspicious money transfer',
            'Account takeover attempt',
            'Fake profile detected'
        ]
        
        reason = random.choice(reasons)
        created_at = datetime.now() - timedelta(days=random.randint(1, 90))
        
        cursor.execute("""
            INSERT INTO fraud_list (id, user_id, reported_user_id, reason, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (report_id, reporter_id, reported_user_id, reason, created_at))
    
    safe_print(f"[OK] Created {num_reports} fraud reports")

def seed_admin_logs(cursor, generator, users):
    """Seed admin logs"""
    safe_print("[INFO] Generating admin logs...")
    
    # Get admin users
    admin_users = [user for user in users if user[1] == 'admin']
    
    if not admin_users:
        safe_print("[WARNING] No admin users found, skipping admin logs")
        return
    
    total_logs = 0
    
    for admin_id, _, _, _ in admin_users:
        # Generate logs for the past 30 days
        num_logs = random.randint(20, 100)
        
        for _ in range(num_logs):
            log_id = str(uuid.uuid4())
            
            # Random IP address
            ip_address = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            
            timestamp = datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Admin activities
            activities = [
                'User account created',
                'User account modified',
                'User account deleted',
                'Fraud report reviewed',
                'Transaction flagged for review',
                'System backup performed',
                'Security settings updated',
                'Role permissions modified',
                'Agent account approved',
                'Dashboard accessed',
                'Report generated',
                'Database maintenance performed'
            ]
            
            details = random.choice(activities)
            
            cursor.execute("""
                INSERT INTO admin_logs (id, admin_id, ip_address, timestamp, details)
                VALUES (%s, %s, %s, %s, %s)
            """, (log_id, admin_id, ip_address, timestamp, details))
            
            total_logs += 1
    
    safe_print(f"[OK] Created {total_logs} admin log entries")

def main():
    """Main function to generate fake data"""
    print("=" * 60)
    print("FinGuard Database Fake Data Generator")
    print("=" * 60)
    
    # Configuration display
    config = get_mysql_config()
    safe_print(f"[INFO] Target database: {config['host']}:{config['port']}/{config['database']}")
    safe_print(f"[INFO] Data to generate:")
    safe_print(f"  - {NUM_USERS} regular users")
    safe_print(f"  - {NUM_AGENTS} agents")
    safe_print(f"  - {NUM_ADMINS} admins")
    safe_print(f"  - ~{NUM_TRANSACTIONS_PER_USER} transactions per user")
    safe_print(f"  - ~{NUM_BUDGETS_PER_USER} budgets per user")
    print()
    
    # Initialize generator
    generator = FakeDataGenerator()
    
    # Create database connection
    connection = create_connection()
    
    try:
        with connection.cursor() as cursor:
            # Clear existing data
            clear_existing_data(cursor)
            
            # Seed data in order (respecting foreign key constraints)
            safe_print("[INFO] Starting data generation...")
            
            # 1. Roles and permissions
            role_ids = seed_roles_and_permissions(cursor, generator)
            
            # 2. Users
            users = seed_users(cursor, generator, role_ids)
            
            # 3. Addresses and contact info
            seed_addresses_and_contacts(cursor, generator, users)
            
            # 4. Transactions
            seed_transactions(cursor, generator, users)
            
            # 5. Budgets
            seed_budgets(cursor, generator, users)
            
            # 6. Expense habits
            seed_expense_habits(cursor, generator, users)
            
            # 7. Fraud reports
            seed_fraud_reports(cursor, generator, users)
            
            # 8. Admin logs
            seed_admin_logs(cursor, generator, users)
            
            # Commit all changes
            connection.commit()
            
            print()
            print("=" * 60)
            safe_print("[OK] Fake data generation completed successfully!")
            print("=" * 60)
            
            # Summary
            safe_print(f"[INFO] Database '{config['database']}' has been populated with:")
            safe_print(f"  ✓ {len(users)} users ({NUM_ADMINS} admins, {NUM_AGENTS} agents, {NUM_USERS} regular)")
            safe_print(f"  ✓ Addresses and contact information for all users")
            safe_print(f"  ✓ Thousands of realistic transactions")
            safe_print(f"  ✓ Budgets with expense categories and items")
            safe_print(f"  ✓ User expense habit profiles")
            safe_print(f"  ✓ Fraud reports and admin activity logs")
            
            print()
            safe_print("[INFO] Default login credentials:")
            safe_print("  Admin:  username=admin,  password=admin")
            safe_print("  Agent:  username=agent,  password=agent") 
            safe_print("  User:   username=user,   password=user")
            safe_print("  (Additional users: user2/user2, user3/user3, etc.)")
            
            print("=" * 60)
            
    except Exception as e:
        connection.rollback()
        safe_print(f"[ERROR] Data generation failed: {e}")
        raise
    finally:
        connection.close()

if __name__ == '__main__':
    main()
