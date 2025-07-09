import sqlite3
import uuid
from datetime import date
from .password_utils import hash_password

def is_email_unique(email):
    conn = sqlite3.connect('fin_guard.db')
    cur = conn.cursor()
    cur.execute('SELECT 1 FROM contact_info WHERE LOWER(email) = ?', (email.lower(),))
    exists = cur.fetchone()
    conn.close()
    return not exists

def is_phone_unique(phone):
    conn = sqlite3.connect('fin_guard.db')
    cur = conn.cursor()
    cur.execute('SELECT 1 FROM contact_info WHERE phone = ?', (phone,))
    exists = cur.fetchone()
    conn.close()
    return not exists

def get_role_id(role):
    conn = sqlite3.connect('fin_guard.db')
    cur = conn.cursor()
    cur.execute('SELECT id FROM roles WHERE LOWER(name) = ?', (role.lower(),))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def generate_user_id():
    import random, string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def create_user_and_contact(role_id, first_name, last_name, dob, age, gender, marital_status, blood_group, email, phone, password):
    conn = sqlite3.connect('fin_guard.db')
    cur = conn.cursor()
    # Generate unique user_id
    while True:
        user_id = generate_user_id()
        cur.execute('SELECT 1 FROM users WHERE LOWER(id) = ?', (user_id.lower(),))
        if not cur.fetchone():
            break
    try:
        cur.execute('INSERT INTO users (id, first_name, last_name, dob, age, gender, marital_status, blood_group, balance, joining_date, role_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, first_name, last_name, dob, age, gender, marital_status, blood_group, 0, date.today().isoformat(), role_id))
        contact_id = str(uuid.uuid4())
        cur.execute('INSERT INTO contact_info (id, user_id, email, phone, address_id) VALUES (?, ?, ?, ?, ?)',
            (contact_id, user_id, email, phone, None))
        cur.execute('CREATE TABLE IF NOT EXISTS user_passwords (user_id TEXT PRIMARY KEY, password TEXT)')
        # Hash the password before storing
        hashed_password = hash_password(password)
        cur.execute('INSERT INTO user_passwords (user_id, password) VALUES (?, ?)', (user_id, hashed_password))
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return None, str(e)
    conn.close()
    return user_id, None
