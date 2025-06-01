from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, jsonify
import uuid
import sqlite3
from datetime import date
import random
import string
from urllib.parse import urlencode

user_bp = Blueprint('user', __name__)

@user_bp.route('/user', methods=['GET'])
def get_user():
    return {'message': 'User endpoint'}

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    from flask import request
    success = request.args.get('success')
    if request.method == 'POST':
        role = request.form.get('role')
        login_id = request.form.get('login_id')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        conn = current_app.get_db_connection()
        # Try to find user by user_id (case-insensitive), email, or phone
        user = conn.execute('''
            SELECT u.* FROM users u
            LEFT JOIN contact_info c ON u.id = c.user_id
            WHERE LOWER(u.id) = ? OR LOWER(c.email) = ? OR c.phone = ?
        ''', (login_id.lower(), login_id.lower(), login_id)).fetchone()
        if user:
            # Check password
            pw_row = conn.execute('SELECT password FROM user_passwords WHERE user_id = ?', (user['id'],)).fetchone()
            conn.close()
            if pw_row and pw_row[0] == password:
                # Optionally set a cookie/session for 'remember me' here
                return redirect(url_for('user.dashboard'))
            else:
                return render_template('login.html', error='Invalid password', success=success)
        else:
            conn.close()
            return render_template('login.html', error='User not found', success=success)
    return render_template('login.html', success=success)

def generate_user_id():
    # Generate an 8-character alphanumeric (uppercase) code
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        marital_status = request.form.get('marital_status')
        blood_group = request.form.get('blood_group')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        # Calculate age
        try:
            birth_year = int(dob.split('-')[0])
            age = date.today().year - birth_year
        except Exception:
            age = None
        # Find role_id
        conn = sqlite3.connect('fin_guard.db')
        cur = conn.cursor()
        cur.execute('SELECT id FROM roles WHERE name = ?', (role,))
        role_row = cur.fetchone()
        if not role_row:
            conn.close()
            return render_template('register.html', error='Role not found')
        role_id = role_row[0]
        # Check for unique email and phone
        cur.execute('SELECT 1 FROM contact_info WHERE LOWER(email) = ?', (email.lower(),))
        if cur.fetchone():
            conn.close()
            return render_template('register.html', error='Email address already in use')
        cur.execute('SELECT 1 FROM contact_info WHERE phone = ?', (phone,))
        if cur.fetchone():
            conn.close()
            return render_template('register.html', error='Phone number already in use')
        # Generate unique 8-char user_id (case-insensitive)
        while True:
            user_id = generate_user_id()
            cur.execute('SELECT 1 FROM users WHERE LOWER(id) = ?', (user_id.lower(),))
            if not cur.fetchone():
                break
        try:
            cur.execute('INSERT INTO users (id, first_name, last_name, dob, age, gender, marital_status, blood_group, balance, joining_date, role_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (user_id, first_name, last_name, dob, age, gender, marital_status, blood_group, 0, date.today().isoformat(), role_id))
            # Insert contact info
            contact_id = str(uuid.uuid4())
            cur.execute('INSERT INTO contact_info (id, user_id, email, phone, address_id) VALUES (?, ?, ?, ?, ?)',
                (contact_id, user_id, email, phone, None))
            # Store password in a simple way (not secure, for demo only)
            cur.execute('CREATE TABLE IF NOT EXISTS user_passwords (user_id TEXT PRIMARY KEY, password TEXT)')
            cur.execute('INSERT INTO user_passwords (user_id, password) VALUES (?, ?)', (user_id, password))
            conn.commit()
        except Exception as e:
            conn.rollback()
            conn.close()
            return render_template('register.html', error='Registration failed: ' + str(e))
        conn.close()
        # Redirect to login page after successful registration, with success message
        params = urlencode({'success': 'Registration successful! Please log in.'})
        return redirect(url_for('user.login') + '?' + params)
    return render_template('register.html')

@user_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@user_bp.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

@user_bp.route('/log', methods=['POST'])
def log_js_message():
    data = request.get_json()
    message = data.get('message', '')
    print(f'[JS LOG] {message}')
    return jsonify({'status': 'ok'})
