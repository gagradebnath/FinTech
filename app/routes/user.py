from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, jsonify, session
from urllib.parse import urlencode
import uuid
import sqlite3
from datetime import date
import random
import string
import json
from app.utils.auth import get_user_by_login_id, check_password
from app.utils.register import is_email_unique, is_phone_unique, get_role_id, create_user_and_contact

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
        user = get_user_by_login_id(login_id)
        if user:
            if check_password(user['id'], password):
                session['user_id'] = user['id']
                return redirect(url_for('user.dashboard'))
            else:
                return render_template('login.html', error='Invalid password', success=success)
        else:
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
        role_id = get_role_id(role)
        if not role_id:
            return render_template('register.html', error='Role not found')
        if not is_email_unique(email):
            return render_template('register.html', error='Email address already in use')
        if not is_phone_unique(phone):
            return render_template('register.html', error='Phone number already in use')
        user_id, err = create_user_and_contact(role_id, first_name, last_name, dob, age, gender, marital_status, blood_group, email, phone, password)
        if err:
            return render_template('register.html', error='Registration failed: ' + err)
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
