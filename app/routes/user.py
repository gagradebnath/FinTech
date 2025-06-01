from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, jsonify, session
from urllib.parse import urlencode
import uuid
import sqlite3
from datetime import date
import random
import string
import json

user_bp = Blueprint('user', __name__)

@user_bp.route('/user', methods=['GET'])
def get_user():
    return {'message': 'User endpoint'}

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
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
            WHERE (LOWER(u.id) = ? OR LOWER(c.email) = ? OR c.phone = ?)''', (login_id.lower(), login_id.lower(), login_id)).fetchone()
        if user:
            # Check password
            pw_row = conn.execute('SELECT password FROM user_passwords WHERE user_id = ?', (user['id'],)).fetchone()
            if pw_row and pw_row[0] == password:
                # Set session user_id for correct user context
                session['user_id'] = user['id']
                conn.close()
                return redirect(url_for('user.dashboard'))
            else:
                conn.close()
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
        # Find role_id (case-insensitive match)
        conn = sqlite3.connect('fin_guard.db')
        cur = conn.cursor()
        cur.execute('SELECT id FROM roles WHERE LOWER(name) = ?', (role.lower(),))
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

def get_current_user():
    # For demo: get user by session or first user
    user_id = session.get('user_id')
    conn = current_app.get_db_connection()
    user = None
    if user_id:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        user = conn.execute('SELECT * FROM users LIMIT 1').fetchone()
    conn.close()
    return user

@user_bp.route('/dashboard', methods=['GET'])
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    conn = current_app.get_db_connection()
    budgets = conn.execute('SELECT * FROM budgets WHERE user_id = ?', (user['id'],)).fetchall()
    # Get recent expenses from transactions table (type='expense')
    expenses = conn.execute('''
        SELECT t.amount, t.timestamp, t.note, t.location FROM transactions t
        WHERE t.sender_id = ? AND t.type = 'expense'
        ORDER BY t.timestamp DESC LIMIT 5
    ''', (user['id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', user=user, budgets=budgets, expenses=expenses)

@user_bp.route('/expense-habit', methods=['GET', 'POST'])
def expense_habit():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    conn = current_app.get_db_connection()
    habit = conn.execute('SELECT * FROM user_expense_habit WHERE user_id = ?', (user['id'],)).fetchone()
    if request.method == 'POST':
        data = {
            'monthly_income': request.form.get('monthly_income'),
            'earning_member': request.form.get('earning_member') == 'on',
            'dependents': request.form.get('dependents'),
            'living_situation': request.form.get('living_situation'),
            'rent': request.form.get('rent'),
            'transport_mode': request.form.get('transport_mode'),
            'transport_cost': request.form.get('transport_cost'),
            'eating_out_frequency': request.form.get('eating_out_frequency'),
            'grocery_cost': request.form.get('grocery_cost'),
            'utilities_cost': request.form.get('utilities_cost'),
            'mobile_internet_cost': request.form.get('mobile_internet_cost'),
            'subscriptions': request.form.get('subscriptions'),
            'savings': request.form.get('savings'),
            'investments': request.form.get('investments'),
            'loans': request.form.get('loans') == 'on',
            'loan_payment': request.form.get('loan_payment'),
            'financial_goal': request.form.get('financial_goal'),
        }
        if habit:
            conn.execute('''UPDATE user_expense_habit SET monthly_income=?, earning_member=?, dependents=?, living_situation=?, rent=?, transport_mode=?, transport_cost=?, eating_out_frequency=?, grocery_cost=?, utilities_cost=?, mobile_internet_cost=?, subscriptions=?, savings=?, investments=?, loans=?, loan_payment=?, financial_goal=? WHERE id=?''',
                (data['monthly_income'], data['earning_member'], data['dependents'], data['living_situation'], data['rent'], data['transport_mode'], data['transport_cost'], data['eating_out_frequency'], data['grocery_cost'], data['utilities_cost'], data['mobile_internet_cost'], data['subscriptions'], data['savings'], data['investments'], data['loans'], data['loan_payment'], data['financial_goal'], habit['id']))
        else:
            conn.execute('''INSERT INTO user_expense_habit (id, user_id, timestamp, monthly_income, earning_member, dependents, living_situation, rent, transport_mode, transport_cost, eating_out_frequency, grocery_cost, utilities_cost, mobile_internet_cost, subscriptions, savings, investments, loans, loan_payment, financial_goal) VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (str(uuid.uuid4()), user['id'], data['monthly_income'], data['earning_member'], data['dependents'], data['living_situation'], data['rent'], data['transport_mode'], data['transport_cost'], data['eating_out_frequency'], data['grocery_cost'], data['utilities_cost'], data['mobile_internet_cost'], data['subscriptions'], data['savings'], data['investments'], data['loans'], data['loan_payment'], data['financial_goal']))
        conn.commit()
        habit = conn.execute('SELECT * FROM user_expense_habit WHERE user_id = ?', (user['id'],)).fetchone()
    conn.close()
    return render_template('expense_habit.html', habit=habit)

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    from flask import session
    user_id = session.get('user_id')
    conn = current_app.get_db_connection()
    user = None
    contact = None
    if user_id:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        contact = conn.execute('SELECT * FROM contact_info WHERE user_id = ?', (user_id,)).fetchone()
    if request.method == 'POST' and user:
        # Update user info
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        marital_status = request.form.get('marital_status')
        blood_group = request.form.get('blood_group')
        email = request.form.get('email')
        phone = request.form.get('phone')
        conn.execute('UPDATE users SET first_name=?, last_name=?, dob=?, gender=?, marital_status=?, blood_group=? WHERE id=?',
            (first_name, last_name, dob, gender, marital_status, blood_group, user['id']))
        conn.execute('UPDATE contact_info SET email=?, phone=? WHERE user_id=?', (email, phone, user['id']))
        conn.commit()
        # Refresh user/contact
        user = conn.execute('SELECT * FROM users WHERE id=?', (user['id'],)).fetchone()
        contact = conn.execute('SELECT * FROM contact_info WHERE user_id=?', (user['id'],)).fetchone()
    conn.close()
    return render_template('profile.html', user=user, contact=contact)

@user_bp.route('/log', methods=['POST'])
def log_js_message():
    data = request.get_json()
    message = data.get('message', '')
    print(f'[JS LOG] {message}')
    return jsonify({'status': 'ok'})
