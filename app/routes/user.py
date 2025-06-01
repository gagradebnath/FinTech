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
from app.utils.user_utils import get_current_user
from app.utils.dashboard import get_user_budgets, get_recent_expenses
from app.utils.expense_habit import get_expense_habit, upsert_expense_habit
from app.utils.profile import get_user_and_contact, update_user_and_contact

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

@user_bp.route('/dashboard', methods=['GET'])
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    budgets = get_user_budgets(user['id'])
    expenses = get_recent_expenses(user['id'])
    return render_template('dashboard.html', user=user, budgets=budgets, expenses=expenses)

@user_bp.route('/expense-habit', methods=['GET', 'POST'])
def expense_habit():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    habit = get_expense_habit(user['id'])
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
        habit = upsert_expense_habit(user['id'], data)
    return render_template('expense_habit.html', habit=habit)

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    from flask import session
    user_id = session.get('user_id')
    user, contact = get_user_and_contact(user_id) if user_id else (None, None)
    if request.method == 'POST' and user:
        user_data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'dob': request.form.get('dob'),
            'gender': request.form.get('gender'),
            'marital_status': request.form.get('marital_status'),
            'blood_group': request.form.get('blood_group'),
        }
        contact_data = {
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
        }
        user, contact = update_user_and_contact(user['id'], user_data, contact_data)
    return render_template('profile.html', user=user, contact=contact)

@user_bp.route('/log', methods=['POST'])
def log_js_message():
    data = request.get_json()
    message = data.get('message', '')
    print(f'[JS LOG] {message}')
    return jsonify({'status': 'ok'})
