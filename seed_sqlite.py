import sqlite3
from datetime import date
import uuid

# Path to your SQLite database
DB_PATH = 'fin_guard.db'
# Path to your schema file
SCHEMA_PATH = 'DatabaseSchema.sql'

def run_schema(cursor):
    with open(SCHEMA_PATH, 'r') as f:
        sql = f.read()
    # Remove ALTER TABLE lines for now to avoid errors if tables are empty
    statements = [s for s in sql.split(';') if s.strip() and not s.strip().lower().startswith('alter table')]
    for stmt in statements:
        cursor.execute(stmt)

def insert_dummy_data(cursor):
    # Insert roles
    admin_role_id = str(uuid.uuid4())
    agent_role_id = str(uuid.uuid4())
    user_role_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO roles (id, name, description) VALUES (?, ?, ?)", (admin_role_id, 'admin', 'Administrator'))
    cursor.execute("INSERT INTO roles (id, name, description) VALUES (?, ?, ?)", (agent_role_id, 'agent', 'Agent'))
    cursor.execute("INSERT INTO roles (id, name, description) VALUES (?, ?, ?)", (user_role_id, 'user', 'Regular User'))

    # Insert users with fixed IDs and passwords
    today = date.today().isoformat()
    cursor.execute("INSERT INTO users (id, first_name, last_name, dob, age, gender, marital_status, blood_group, balance, joining_date, role_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ('admin', 'Admin', 'User', '1990-01-01', 35, 'M', 'Single', 'O+', 10000, today, admin_role_id))
    cursor.execute("INSERT INTO users (id, first_name, last_name, dob, age, gender, marital_status, blood_group, balance, joining_date, role_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ('agent', 'Agent', 'Smith', '1992-02-02', 33, 'M', 'Married', 'A+', 10000, today, agent_role_id))
    cursor.execute("INSERT INTO users (id, first_name, last_name, dob, age, gender, marital_status, blood_group, balance, joining_date, role_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ('user', 'John', 'Doe', '1995-03-03', 30, 'M', 'Single', 'B+', 10000, today, user_role_id))

    # Insert passwords (ensure table exists)
    cursor.execute('CREATE TABLE IF NOT EXISTS user_passwords (user_id TEXT PRIMARY KEY, password TEXT)')
    cursor.execute('INSERT OR REPLACE INTO user_passwords (user_id, password) VALUES (?, ?)', ('admin', 'admin'))
    cursor.execute('INSERT OR REPLACE INTO user_passwords (user_id, password) VALUES (?, ?)', ('agent', 'agent'))
    cursor.execute('INSERT OR REPLACE INTO user_passwords (user_id, password) VALUES (?, ?)', ('user', 'user'))

    print('Dummy data inserted!')
    print('--- LOGIN DETAILS ---')
    print('Admin:   id=admin   password=admin')
    print('Agent:   id=agent   password=agent')
    print('User:    id=user    password=user')
    print('---------------------')

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    run_schema(cursor)
    insert_dummy_data(cursor)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
