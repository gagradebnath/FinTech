from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, jsonify, session
from urllib.parse import urlencode
import uuid
from datetime import date
import random
import string
import json
from app.utils.auth import get_user_by_login_id, check_password
from app.utils.register import is_email_unique, is_phone_unique, get_role_id, create_user_and_contact
from app.utils.user_utils import get_current_user, get_role_name_by_id, get_all_agents
from app.utils.dashboard import get_user_budgets, get_recent_transactions
from app.utils.expense_habit import get_expense_habit, upsert_expense_habit
from app.utils.profile import get_user_and_contact, update_user_and_contact
from app.utils.permissions_utils import has_permission
from app.utils.budget_utils import get_all_user_budgets_with_categories
from app.utils.jwt_auth import generate_jwt_token, token_required, get_current_user_from_jwt
from app.utils.money_request_utils import create_user_cashout_request
from app.utils.notification_utils import get_unread_notifications, get_recent_notifications, mark_notifications_read


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
    
    budgets = get_all_user_budgets_with_categories(user['id'])

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
    
    notifications = get_unread_notifications(user['id'])
    recent_notifications = get_recent_notifications(user['id'], limit=10)
    notification_count = sum(1 for n in recent_notifications if not n['is_read'])
    
    return render_template('dashboard.html', user=user, budgets=budgets, transactions=transactions, notifications=notifications, notification_count=notification_count)

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

@user_bp.route('/upload-profile-picture', methods=['POST'])
def upload_profile_picture():
    import os
    from werkzeug.utils import secure_filename
    
    # Support both session-based and JWT-based authentication
    user = get_current_user_from_jwt()
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    # Check if the post request has the file part
    if 'profile_picture' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    file = request.files['profile_picture']
    
    # If user does not select file, browser also submits an empty part without filename
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    # Check file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WebP files only.'}), 400
    
    # Get file extension
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    
    # Generate filename based on username
    username = user.get('login_id', str(user['id']))  # Use login_id or fallback to user id
    filename = f"{secure_filename(username)}.{file_extension}"
    
    # Ensure uploads/profile directory exists
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile')
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, filename)
    
    try:
        # Save the file
        file.save(file_path)
        
        # Return success response with the file path for frontend to use
        return jsonify({
            'success': True, 
            'message': 'Profile picture uploaded successfully',
            'filename': filename,
            'file_path': f'/static/uploads/profile/{filename}'
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to save file: {str(e)}'}), 500

@user_bp.route('/log', methods=['POST'])
def log_js_message():
    data = request.get_json()
    message = data.get('message', '')
    print(f'[JS LOG] {message}')
    return jsonify({'status': 'ok'})

@user_bp.route('/api/category-summary', methods=['GET'])
@token_required
def category_summary_api():
    user = get_current_user_from_jwt()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    user_id = user['id']
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get all categories from budget_expense_categories for this user
            cursor.execute('''
                SELECT DISTINCT category_name
                FROM budget_expense_categories
                WHERE budget_id IN (SELECT id FROM budgets WHERE user_id = %s)
            ''', (user_id,))
            categories = [row['category_name'] for row in cursor.fetchall()]
            summary = []
            for cat in categories:
                # Sum budget for this category (all budgets ever created by user)
                cursor.execute('''
                    SELECT COALESCE(SUM(amount),0) as total_budget
                    FROM budget_expense_categories
                    WHERE category_name = %s AND budget_id IN (SELECT id FROM budgets WHERE user_id = %s)
                ''', (cat, user_id))
                budget = cursor.fetchone()['total_budget']
                # Sum expenditure for this category (only sent transactions)
                cursor.execute('''
                    SELECT COALESCE(SUM(amount),0) as total_expense
                    FROM transactions
                    WHERE sender_id = %s AND note = %s
                ''', (user_id, cat))
                expense = cursor.fetchone()['total_expense']
                # Condition
                diff = budget - expense
                if diff >= 0:
                    condition = f"${diff:.2f} remaining"
                else:
                    condition = f"${-diff:.2f} overspent"
                summary.append({
                    'category': cat,
                    'budget': float(budget),
                    'expenditure': float(expense),
                    'condition': condition
                })
        return jsonify(summary)
    finally:
        conn.close()

@user_bp.route('/user/cashout-request', methods=['POST'])
def cashout_request():
    user_id = session.get('user_id')
    agent_id = request.form.get('agent_id')
    amount = request.form.get('amount')
    note = request.form.get('note')
    cashout_success = None
    cashout_error = None
    if not agent_id or not amount:
        cashout_error = 'Agent and amount are required.'
    elif int(amount) > 30000:
        cashout_error = 'Maximum cash out amount is 30000.'
    else:
        try:
            create_user_cashout_request(user_id, agent_id, amount, note)
            cashout_success = 'Cash out request sent to agent!'
        except Exception as e:
            cashout_error = 'Failed to send request: ' + str(e)
    # Re-render the send_money.html with agents and messages
        agents = get_all_agents()
    return render_template('send_money.html', agents=agents, cashout_success=cashout_success, cashout_error=cashout_error)

@user_bp.route('/notifications/mark-read', methods=['POST'])
def mark_notifications_read_route():
    user_id = session.get('user_id')
    mark_notifications_read(user_id)
    return redirect(request.referrer or url_for('user.dashboard'))

def get_recent_notifications(user_id, limit=10):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT %s"
            cursor.execute(sql, (user_id, limit))
            return cursor.fetchall()
    finally:
        conn.close()

@user_bp.route('/send-money', methods=['GET'])
def send_money_page():
    agents = get_all_agents()
    # You can also pass other context variables if needed
    return render_template('send_money.html', agents=agents)
