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
    """Create user and contact using stored procedure"""
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get role name from role_id
            cursor.execute('SELECT name FROM roles WHERE id = %s', (role_id,))
            role_row = cursor.fetchone()
            
            if not role_row:
                return None, 'Invalid role ID'
                
            role_name = role_row['name']
            
            # Hash the password
            hashed_password = hash_password(password)
            
            # Call the stored procedure
            cursor.callproc('RegisterUser', [
                role_name, first_name, last_name, dob, age, gender, 
                marital_status, blood_group, email, phone, hashed_password,
                None, None, None  # OUT parameters
            ])
            
            # Fetch the OUT parameters
            cursor.execute("SELECT @_RegisterUser_11 as user_id, @_RegisterUser_12 as success, @_RegisterUser_13 as message")
            result = cursor.fetchone()
            
            if result and result['success']:
                return result['user_id'], None
            else:
                return None, result['message'] if result else 'Registration failed'
                
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()
