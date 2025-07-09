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
from app.utils.user_utils import get_current_user, get_role_name_by_id
from app.utils.dashboard import get_user_budgets, get_recent_transactions
from app.utils.expense_habit import get_expense_habit, upsert_expense_habit
from app.utils.profile import get_user_and_contact, update_user_and_contact
from app.utils.permissions_utils import has_permission
from app.utils.jwt_auth import generate_jwt_token, token_required, get_current_user_from_jwt

user_bp = Blueprint('user', __name__)

@user_bp.route('/user', methods=['GET'])
def get_user():
    return {'message': 'User endpoint'}

@user_bp.route('/api/user', methods=['GET'])
@token_required
def get_user_api():
    """Protected API endpoint to get current user information."""
    user = get_current_user_from_jwt()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Return user information (excluding sensitive data)
    user_data = {
        'id': user['id'],
        'first_name': user['first_name'],
        'last_name': user['last_name'],
        'role_id': user['role_id'],
        'balance': user.get('balance', 0),
        'created_at': user.get('created_at')
    }
    
    return jsonify({'user': user_data}), 200

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    success = request.args.get('success')
    if request.method == 'POST':
        # Check if request is JSON (API call) or form data (web form)
        is_api_request = request.is_json or request.headers.get('Content-Type') == 'application/json'
        
        if is_api_request:
            data = request.get_json()
            role = data.get('role')
            login_id = data.get('login_id')
            password = data.get('password')
        else:
            role = request.form.get('role')
            login_id = request.form.get('login_id')
            password = request.form.get('password')
            remember_me = request.form.get('remember_me')
        
        user = get_user_by_login_id(login_id)
        if user:
            if check_password(user['id'], password):
                # Fetch user's actual role name
                user_role = get_role_name_by_id(user['role_id'])
                if not user_role:
                    if is_api_request:
                        return jsonify({'error': 'User role not found'}), 400
                    return render_template('login.html', error='User role not found', success=success)
                
                user_role = user_role.lower()
                selected_role = role.lower() if role else ''
                if user_role != selected_role:
                    error_msg = 'Selected role does not match your account role.'
                    if is_api_request:
                        return jsonify({'error': error_msg}), 400
                    return render_template('login.html', error=error_msg, success=success)
                
                # For API requests, return JWT token
                if is_api_request:
                    token = generate_jwt_token(user['id'], user['role_id'])
                    if token:
                        return jsonify({
                            'success': True,
                            'token': token,
                            'user': {
                                'id': user['id'],
                                'name': f"{user['first_name']} {user['last_name']}",
                                'role': user_role
                            }
                        }), 200
                    else:
                        return jsonify({'error': 'Failed to generate authentication token'}), 500
                
                # For web requests, use traditional session-based authentication
                session['user_id'] = user['id']
                session['user_fullname'] = f"{user['first_name']} {user['last_name']}"
                if user_role == 'agent':
                    return redirect(url_for('agent.agent_dashboard'))
                elif user_role == 'admin':
                    return redirect(url_for('admin.admin_dashboard'))
                else:
                    return redirect(url_for('user.dashboard'))
            else:
                if is_api_request:
                    return jsonify({'error': 'Invalid password'}), 401
                return render_template('login.html', error='Invalid password', success=success)
        else:
            if is_api_request:
                return jsonify({'error': 'User not found'}), 404
            return render_template('login.html', error='User not found', success=success)
    
    return render_template('login.html', success=success)

@user_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Handle logout for both web and API clients."""
    is_api_request = request.is_json or request.headers.get('Content-Type') == 'application/json'
    
    # Clear session for web clients
    session.clear()
    
    if is_api_request:
        # For API clients, return success message
        # Note: JWT tokens are stateless, so client should discard the token
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    else:
        # For web clients, redirect to login page
        return redirect(url_for('user.login'))

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
            from datetime import datetime
            birth_date = datetime.strptime(dob, '%Y-%m-%d').date()
            age = date.today().year - birth_date.year
            # Adjust age if birthday hasn't occurred this year
            if date.today() < birth_date.replace(year=date.today().year):
                age -= 1
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
    # Support both session-based and JWT-based authentication
    user = get_current_user_from_jwt()
    if not user:
        # Check if it's an API request
        is_api_request = request.headers.get('Authorization') or request.args.get('token')
        if is_api_request:
            return jsonify({'error': 'Authentication required'}), 401
        return redirect(url_for('user.login'))
    
    if not has_permission(user['id'], 'perm_view_dashboard'):
        error_msg = 'Permission denied.'
        is_api_request = request.headers.get('Authorization') or request.args.get('token')
        if is_api_request:
            return jsonify({'error': error_msg}), 403
        return render_template('dashboard.html', user=user, budgets=[], transactions=[], error=error_msg)
    
    budgets = get_user_budgets(user['id'])
    transactions = get_recent_transactions(user['id'])
    
    # Check if this is an API request
    is_api_request = request.headers.get('Authorization') or request.args.get('token')
    if is_api_request:
        # Return JSON response for API clients
        return jsonify({
            'user': {
                'id': user['id'],
                'name': f"{user['first_name']} {user['last_name']}",
                'balance': user.get('balance', 0)
            },
            'budgets': budgets,
            'transactions': transactions
        }), 200
    
    # Debug: Ensure all transaction timestamps are proper datetime objects
    for tx in transactions:
        if tx.get('timestamp'):
            print(f"DEBUG: Transaction timestamp type: {type(tx['timestamp'])}, value: {tx['timestamp']}")
    
    return render_template('dashboard.html', user=user, budgets=budgets, transactions=transactions)

@user_bp.route('/expense-habit', methods=['GET', 'POST'])
def expense_habit():
    user = get_current_user()
    if not user:
        return
        return render_template('expense_habit.html', habit=None, error='Permission denied.')
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
    # Support both session-based and JWT-based authentication
    user = get_current_user_from_jwt()
    
    if not user:
        # Check if it's an API request
        is_api_request = request.headers.get('Authorization') or request.args.get('token') or request.is_json
        if is_api_request:
            return jsonify({'error': 'Authentication required'}), 401
        return redirect(url_for('user.login'))
    
    # Get user contact information
    from app.utils.profile import get_user_and_contact, update_user_and_contact
    user, contact = get_user_and_contact(user['id'])
    
    if request.method == 'POST' and user:
        if not has_permission(user['id'], 'edit_profile'):
            is_api_request = request.headers.get('Authorization') or request.args.get('token') or request.is_json
            if is_api_request:
                return jsonify({'error': 'Permission denied'}), 403
            return render_template('profile.html', user=user, contact=contact, error='Permission denied.')
        
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            user_data = {
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'dob': data.get('dob'),
                'gender': data.get('gender'),
                'marital_status': data.get('marital_status'),
                'blood_group': data.get('blood_group'),
            }
            contact_data = {
                'email': data.get('email'),
                'phone': data.get('phone'),
            }
        else:
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
        
        # Return JSON response for API requests
        if request.is_json:
            return jsonify({
                'success': True,
                'user': dict(user) if user else None,
                'contact': dict(contact) if contact else None
            }), 200
    
    # Return JSON response for API GET requests
    is_api_request = request.headers.get('Authorization') or request.args.get('token')
    if is_api_request and request.method == 'GET':
        return jsonify({
            'user': dict(user) if user else None,
            'contact': dict(contact) if contact else None
        }), 200
    
    return render_template('profile.html', user=user, contact=contact)

@user_bp.route('/log', methods=['POST'])
def log_js_message():
    data = request.get_json()
    message = data.get('message', '')
    print(f'[JS LOG] {message}')
    return jsonify({'status': 'ok'})
