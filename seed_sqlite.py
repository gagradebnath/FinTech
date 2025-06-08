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
        cursor.execute("INSERT INTO permissions (id, name, description) VALUES (?, ?, ?)", (perm_id, perm_name, perm_desc))

    # Assign permissions to roles
    def assign_perms(role_id, perm_names):
        for perm_name in perm_names:
            rp_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO role_permissions (id, role_id, permission_id) VALUES (?, ?, ?)", (rp_id, role_id, permission_ids[perm_name]))

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

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    run_schema(cursor)
    insert_dummy_data(cursor)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
