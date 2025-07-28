from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash
from app.utils.user_utils import get_current_user
from app.utils.dashboard import get_user_budgets, get_recent_transactions
from app.utils.permissions_utils import has_permission
from app.utils.transaction_utils import get_user_by_id, agent_add_money, agent_cash_out
from app.utils.user_utils import get_all_users
from app.utils.money_request_utils import create_agent_money_request, get_cashout_requests_for_agent, approve_user_cashout_request, update_user_cashout_request_status, get_user_cashout_request_by_id
from app.utils.user_utils import get_all_admins
from app.utils.notification_utils import get_unread_notifications, create_notification, get_recent_notifications

agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/agent', methods=['GET'])
def get_agent():
    return {'message': 'Agent endpoint'}

@agent_bp.route('/agent/dashboard', methods=['GET', 'POST'])
def agent_dashboard():
    user = get_current_user()
    admins = get_all_admins()
    budgets = get_user_budgets(user['id'])
    transactions = get_recent_transactions(user['id'])
    add_money_success = None
    add_money_error = None
    users = get_all_users()  # Fetch all users for the agent dashboard
    request_success = None
    request_error = None
    cashout_success = None
    cashout_error = None
    cashout_requests = get_cashout_requests_for_agent(user['id'])
    notifications = get_recent_notifications(user['id'], limit=10)
    notification_count = sum(1 for n in notifications if not n['is_read'])

    if request.method == 'POST' and 'cashout_request_id' in request.form:
        request_id = request.form.get('cashout_request_id')
        action = request.form.get('action')  # 'approved' or 'rejected'
        note = request.form.get('note')
        if action == 'approved':
            success = approve_user_cashout_request(request_id, user['id'])
            if success:
                # Fetch user_id and amount for this request
                req = get_user_cashout_request_by_id(request_id)
                if req:
                    create_notification(req['user_id'], f"Cash out request approved, ${req['amount']} deducted from your account.")
                cashout_success = 'Cash out request approved and balances updated!'
            else:
                cashout_error = 'Request not found or already processed.'
        else:
            update_user_cashout_request_status(request_id, user['id'], action, note)
            cashout_success = f'Request {action}!'
    cashout_requests = get_cashout_requests_for_agent(user['id'])

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
                        if not has_permission(user['id'], 'perm_add_money'):
                            add_money_error = 'Permission denied.'
                        elif agent_bal < amount_val:
                            add_money_error = 'Insufficient agent balance.'
                        else:
                            # Use transaction_utils for balance update and transaction insert
                            add_money_success, add_money_error = agent_add_money(user['id'], target['id'], amount_val)
                    elif operation == 'cashout':
                        if not has_permission(user['id'], 'perm_cash_out'):
                            add_money_error = 'Permission denied.'
                        elif target['balance'] < amount_val:
                            add_money_error = 'Insufficient user balance for cash out.'
                        else:
                            from app.utils.transaction_utils import agent_cash_out
                            add_money_success, add_money_error = agent_cash_out(user['id'], target['id'], amount_val)
            except Exception as e:
                add_money_error = 'Failed to process: ' + str(e)
    return render_template(
        'agent_dashboard.html',
        user=user,
        budgets=budgets,
        transactions=transactions,
        add_money_success=add_money_success,
        add_money_error=add_money_error,
        users=users,
        admins=admins,
        request_success=request_success,
        request_error=request_error,
        cashout_requests=cashout_requests,
        cashout_success=cashout_success,
        cashout_error=cashout_error,
        notifications=notifications,
        notification_count=notification_count
    )

@agent_bp.route('/agent/request-money', methods=['GET', 'POST'])
def agent_request_money():
    user = get_current_user()
    admins = get_all_admins()
    budgets = get_user_budgets(user['id'])
    transactions = get_recent_transactions(user['id'])
    add_money_success = None
    add_money_error = None
    users = get_all_users()
    request_success = None
    request_error = None
    cashout_success = None
    cashout_error = None
    cashout_requests = get_cashout_requests_for_agent(user['id'])
    notifications = get_recent_notifications(user['id'], limit=10)
    notification_count = sum(1 for n in notifications if not n['is_read'])

    if request.method == 'POST':
        agent_id = session.get('user_id')
        admin_id = request.form.get('admin_id')
        amount = request.form.get('amount')
        note = request.form.get('note')
        if not agent_id or not admin_id or not amount:
            flash('Agent, admin, and amount are required.', 'danger')
            return redirect(url_for('agent.agent_request_money'))
        create_agent_money_request(agent_id, admin_id, amount, note)
        # Send notification to admin
        from app.utils.notification_utils import create_notification
        create_notification(
            admin_id,
            f"Agent {agent_id} requested ${amount}. Click to view requests.",
            url_for('admin.admin_dashboard', _anchor='agent-money-requests')
        )
        flash('Money request sent to admin!', 'success')
        return redirect(url_for('agent.agent_request_money'))

    return render_template(
        'agent_dashboard.html',
        user=user,
        budgets=budgets,
        transactions=transactions,
        add_money_success=add_money_success,
        add_money_error=add_money_error,
        users=users,
        admins=admins,
        request_success=request_success,
        request_error=request_error,
        cashout_requests=cashout_requests,
        cashout_success=cashout_success,
        cashout_error=cashout_error,
        notifications=notifications,
        notification_count=notification_count
    )
