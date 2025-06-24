from flask import Blueprint, render_template, request, current_app, jsonify, session, redirect, url_for
import uuid
from .user import get_current_user
from app.utils.budget_utils import get_user_budget, save_or_update_budget, insert_full_budget, get_all_user_budgets, get_budget_by_id

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budget', methods=['GET'])
def get_budget():
    return {'message': 'Budget endpoint'}

@budget_bp.route('/plan-budget', methods=['GET', 'POST'])
def plan_budget():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    
    # Get the budget ID from query parameters if provided
    budget_id = request.args.get('budget_id')
    
    # Get all budgets for the dropdown
    from app.utils.budget_utils import get_all_user_budgets, get_budget_by_id
    user_budgets = get_all_user_budgets(user['id'])
    
    # If a specific budget ID is provided, load that budget
    budget = None
    if budget_id:
        budget = get_budget_by_id(budget_id, user['id'])
        print(f"Loaded specific budget by ID {budget_id}:", budget)
    else:
        # Otherwise, get the default budget (if any)
        default_budget = get_user_budget(user['id'])
        print("Loaded default budget:", default_budget)
        
        # Convert budget to dict if it's a SQLite Row object
        if default_budget:
            if hasattr(default_budget, 'keys'):
                budget = dict(default_budget)
            else:
                budget = default_budget
    
    error = None
    success = None
    
    if request.method == 'POST':
        name = request.form.get('name')
        currency = request.form.get('currency')
        income_source = request.form.get('income_source')
        amount = request.form.get('amount')
        try:
            saved_budget = save_or_update_budget(user['id'], name, currency, income_source, amount)
            if saved_budget:
                if hasattr(saved_budget, 'keys'):
                    budget = dict(saved_budget)
                else:
                    budget = saved_budget
            success = 'Budget saved successfully.'
        except Exception as e:
            error = 'Failed to save budget: ' + str(e)
    
    # Convert user_budgets to list of dicts if they are SQLite Row objects
    serializable_user_budgets = []
    for b in user_budgets:
        if hasattr(b, 'keys'):
            serializable_user_budgets.append(dict(b))
        else:
            serializable_user_budgets.append(b)
    
    # Add debug information
    print("Budget data being sent to template:", budget)
    if budget and isinstance(budget, dict) and 'categories' in budget:
        print("Categories in budget:", budget['categories'])
    
    return render_template('plan_budget.html', budget=budget, user_budgets=serializable_user_budgets, error=error, success=success)

@budget_bp.route('/save_budget', methods=['POST'])
def save_budget():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    user_id = session['user_id']
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    budget_name = data.get('budgetName')
    currency = data.get('currency')
    income = data.get('income', [])
    expenses = data.get('expenses', [])
    if not budget_name or not currency or not income or not expenses:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    success, err = insert_full_budget(user_id, budget_name, currency, income, expenses)
    if success:
        return jsonify({'success': True, 'message': 'Budget saved', 'budget': data})
    else:
        return jsonify({'success': False, 'message': err}), 500

@budget_bp.route('/get_budget/<budget_id>', methods=['GET'])
def get_budget_by_id_route(budget_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    budget = get_budget_by_id(budget_id, user['id'])
    if not budget:
        return jsonify({'success': False, 'message': 'Budget not found'}), 404
    
    # Ensure budget is serializable
    if hasattr(budget, 'keys') and not isinstance(budget, dict):
        budget = dict(budget)
    
    # Add debugging information to help diagnose any issues
    print(f"Retrieved budget data: {budget}")
    
    # Ensure categories are properly structured
    if 'categories' in budget and budget['categories']:
        # Log category data for debugging
        for cat_id, category in budget['categories'].items():
            print(f"Category: {category['name']} with {len(category['items'])} items")
            for item in category['items']:
                print(f"  - Item: {item['name']}, Amount: {item['amount']}")
    
    return jsonify({'success': True, 'budget': budget})

# Function to handle JSON serialization of SQLite row objects
def serialize_budget(budget):
    if not budget:
        return None
    
    # Convert SQLite row object to regular object if needed
    if hasattr(budget, 'toJSON') and callable(budget.toJSON):
        return budget.toJSON()
    
    return budget
