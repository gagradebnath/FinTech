from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash
from app.utils.user_utils import get_current_user
from app.utils.dashboard import get_user_budgets, get_recent_transactions
from app.utils.permissions_utils import has_permission
from app.utils.transaction_utils import get_user_by_id, agent_add_money, agent_cash_out
import uuid

agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/agent', methods=['GET'])
def get_agent():
    return {'message': 'Agent endpoint'}

@agent_bp.route('/agent/dashboard', methods=['GET', 'POST'])
def agent_dashboard():
    user = get_current_user()
    if not has_permission(user['id'], 'view_dashboard'):
        return render_template('agent_dashboard.html', user=user, budgets=[], transactions=[], add_money_success=None, add_money_error='Permission denied.')
    budgets = get_user_budgets(user['id'])
    transactions = get_recent_transactions(user['id'])
    add_money_success = None
    add_money_error = None
    if request.method == 'POST':
        target_identifier = request.form.get('target_identifier')
        amount = request.form.get('amount')
        operation = request.form.get('operation')  # 'add' or 'cashout'
        if not target_identifier or not amount or not operation:
            add_money_error = 'All fields are required.'
        else:
            try:
                # Use transaction_utils for user lookup
                target = get_user_by_id(target_identifier)
                if not target:
                    add_money_error = 'User not found.'
                elif target['id'] == user['id']:
                    add_money_error = 'You cannot add or cash out money to your own account.'
                else:
                    amount_val = float(amount)
                    agent_bal = get_user_by_id(user['id'])['balance']
                    if operation == 'add':
                        if not has_permission(user['id'], 'add_money'):
                            add_money_error = 'Permission denied.'
                        elif agent_bal < amount_val:
                            add_money_error = 'Insufficient agent balance.'
                        else:
                            # Use transaction_utils for balance update and transaction insert
                            add_money_success, add_money_error = agent_add_money(user['id'], target['id'], amount_val)
                    elif operation == 'cashout':
                        if not has_permission(user['id'], 'cash_out'):
                            add_money_error = 'Permission denied.'
                        elif target['balance'] < amount_val:
                            add_money_error = 'Insufficient user balance for cash out.'
                        else:
                            from app.utils.transaction_utils import agent_cash_out
                            add_money_success, add_money_error = agent_cash_out(user['id'], target['id'], amount_val)
            except Exception as e:
                add_money_error = 'Failed to process: ' + str(e)
    return render_template('agent_dashboard.html', user=user, budgets=budgets, transactions=transactions, add_money_success=add_money_success, add_money_error=add_money_error)
