import pymysql
import uuid
from datetime import date
from flask import current_app
from .password_utils import hash_password

def is_email_unique(email):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1 FROM contact_info WHERE LOWER(email) = %s', (email.lower(),))
            exists = cursor.fetchone()
        return not exists
    finally:
        conn.close()

def is_phone_unique(phone):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1 FROM contact_info WHERE phone = %s', (phone,))
            exists = cursor.fetchone()
        return not exists
    finally:
        conn.close()

def get_role_id(role):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id FROM roles WHERE LOWER(name) = %s', (role.lower(),))
            row = cursor.fetchone()
        return row['id'] if row else None
    finally:
        conn.close()

def generate_user_id():
    import random, string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def create_user_and_contact(role_id, first_name, last_name, dob, age, gender, marital_status, blood_group, email, phone, password):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Generate unique user_id
            while True:
                user_id = generate_user_id()
                cursor.execute('SELECT 1 FROM users WHERE LOWER(id) = %s', (user_id.lower(),))
                if not cursor.fetchone():
                    break
            
            # Insert user
            cursor.execute('''INSERT INTO users (id, first_name, last_name, dob, age, gender, marital_status, blood_group, balance, joining_date, role_id) 
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (user_id, first_name, last_name, dob, age, gender, marital_status, blood_group, 0, date.today().isoformat(), role_id))
            
            # Insert contact info
            contact_id = str(uuid.uuid4())
            cursor.execute('INSERT INTO contact_info (id, user_id, email, phone, address_id) VALUES (%s, %s, %s, %s, %s)',
                (contact_id, user_id, email, phone, None))
            
            # Hash the password before storing
            hashed_password = hash_password(password)
            cursor.execute('INSERT INTO user_passwords (user_id, password) VALUES (%s, %s)', (user_id, hashed_password))
            
        conn.commit()
        return user_id, None
    except Exception as e:
        conn.rollback()
        return None, str(e)
    finally:
        conn.close()
