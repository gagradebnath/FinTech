from flask import Blueprint, render_template, request, current_app, jsonify, session, redirect, url_for
import uuid
from .user import get_current_user
from app.utils.budget_utils import get_user_budget, save_or_update_budget, insert_full_budget

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budget', methods=['GET'])
def get_budget():
    return {'message': 'Budget endpoint'}

@budget_bp.route('/plan-budget', methods=['GET', 'POST'])
def plan_budget():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    budget = get_user_budget(user['id'])
    error = None
    success = None
    if request.method == 'POST':
        name = request.form.get('name')
        currency = request.form.get('currency')
        income_source = request.form.get('income_source')
        amount = request.form.get('amount')
        try:
            budget = save_or_update_budget(user['id'], name, currency, income_source, amount)
            success = 'Budget saved successfully.'
        except Exception as e:
            error = 'Failed to save budget: ' + str(e)
    return render_template('plan_budget.html', budget=budget, error=error, success=success)

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
