# Utility functions for user profile fetch/update
from flask import current_app

def get_user_and_contact(user_id):
    conn = current_app.get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    contact = conn.execute('SELECT * FROM contact_info WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return user, contact

def update_user_and_contact(user_id, user_data, contact_data):
    conn = current_app.get_db_connection()
    conn.execute('UPDATE users SET first_name=?, last_name=?, dob=?, gender=?, marital_status=?, blood_group=? WHERE id=?',
        (user_data['first_name'], user_data['last_name'], user_data['dob'], user_data['gender'], user_data['marital_status'], user_data['blood_group'], user_id))
    conn.execute('UPDATE contact_info SET email=?, phone=? WHERE user_id=?', (contact_data['email'], contact_data['phone'], user_id))
    conn.commit()
    user = conn.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
    contact = conn.execute('SELECT * FROM contact_info WHERE user_id=?', (user_id,)).fetchone()
    conn.close()
    return user, contact
