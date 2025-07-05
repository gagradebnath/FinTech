# Utility functions for user profile fetch/update
from flask import current_app

def get_user_and_contact(user_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            cursor.execute('SELECT * FROM contact_info WHERE user_id = %s', (user_id,))
            contact = cursor.fetchone()
        return user, contact
    finally:
        conn.close()

def update_user_and_contact(user_id, user_data, contact_data):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE users SET first_name=%s, last_name=%s, dob=%s, gender=%s, marital_status=%s, blood_group=%s WHERE id=%s',
                (user_data['first_name'], user_data['last_name'], user_data['dob'], user_data['gender'], user_data['marital_status'], user_data['blood_group'], user_id))
            cursor.execute('UPDATE contact_info SET email=%s, phone=%s WHERE user_id=%s', 
                (contact_data['email'], contact_data['phone'], user_id))
            
            conn.commit()
            
            cursor.execute('SELECT * FROM users WHERE id=%s', (user_id,))
            user = cursor.fetchone()
            cursor.execute('SELECT * FROM contact_info WHERE user_id=%s', (user_id,))
            contact = cursor.fetchone()
        return user, contact
    finally:
        conn.close()
