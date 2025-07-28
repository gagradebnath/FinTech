from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash, jsonify
from app.utils.user_utils import get_current_user
from app.utils.permissions_utils import get_all_roles, get_all_permissions, get_permissions_for_role, add_permission_to_role, remove_permission_from_role, has_permission
from app.utils.dashboard import get_user_budgets, get_recent_transactions
from app.utils.admin_utils import (
    get_role_name_by_id, get_agents, get_all_users, get_all_transactions, get_all_frauds, get_admin_logs,
    update_user_balance, insert_transaction_admin, insert_admin_log, insert_fraud_list, delete_fraud_list, update_user_role, get_role_id_by_name
)
from app.utils.money_request_utils import get_agent_money_requests_for_admin, update_agent_money_request_status, get_pending_agent_money_request_count, approve_agent_money_request, get_agent_money_request_by_id
from app.utils.notification_utils import get_unread_notifications, create_notification, get_recent_notifications
from app.utils.advanced_sql_utils import AdvancedSQLUtils, AdvancedReportingUtils
import uuid
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET'])
def get_admin():
    return {'message': 'Admin endpoint'}

@admin_bp.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    role_name = get_role_name_by_id(user['role_id'])
    if not role_name or role_name.lower() != 'admin':
        return render_template('login.html', error='Access denied: Admins only.')
    agents = get_agents()
    users = get_all_users()
    budgets = get_user_budgets(user['id'])
    my_transactions = get_recent_transactions(user['id'])
    transactions = get_all_transactions()
    frauds = get_all_frauds()
    try:
        admin_logs = get_admin_logs()
    except Exception:
        admin_logs = []
    add_money_success = None
    add_money_error = None
    fraud_action_success = None
    fraud_action_error = None
    role_action_success = None
    role_action_error = None
    perm_action_success = None
    perm_action_error = None
    roles = get_all_roles()
    permissions = get_all_permissions()
    role_permissions_map = {}
    for role in roles:
        role_permissions_map[role['id']] = [p['id'] for p in get_permissions_for_role(role['id'])]
    if request.method == 'POST':
        if 'agent_id' in request.form and 'amount' in request.form:
            if not has_permission(user['id'], 'perm_manage_agents'):
                add_money_error = 'Permission denied.'
            else:
                agent_id = request.form.get('agent_id')
                amount = request.form.get('amount')
                if not agent_id or not amount:
                    add_money_error = 'All fields are required.'
                else:
                    try:
                        amount_val = float(amount)
                        update_user_balance(agent_id, amount_val)
                        tx_id = str(uuid.uuid4())
                        insert_transaction_admin(tx_id, amount_val, user['id'], agent_id, f'Admin {user["id"]} added money to agent', 'Deposit')
                        log_id = str(uuid.uuid4())
                        insert_admin_log(log_id, user['id'], request.remote_addr or 'localhost', f"Added {amount} to agent (ID: {agent_id})")
                        add_money_success = f"Added {amount} to agent (ID: {agent_id})"
                    except Exception as e:
                        add_money_error = 'Failed to process: ' + str(e)
        elif 'fraud_action' in request.form:
            if not has_permission(user['id'], 'perm_manage_fraud'):
                fraud_action_error = 'Permission denied.'
            else:
                fraud_action = request.form.get('fraud_action')
                fraud_user_id = request.form.get('fraud_user_id')
                reason = request.form.get('fraud_reason')
                try:
                    if fraud_action == 'add' and fraud_user_id and reason:
                        fraud_id = str(uuid.uuid4())
                        insert_fraud_list(fraud_id, user['id'], fraud_user_id, reason)
                        log_id = str(uuid.uuid4())
                        insert_admin_log(log_id, user['id'], request.remote_addr or 'localhost', f"Added user {fraud_user_id} to fraud list. Reason: {reason}")
                        fraud_action_success = f"Added user {fraud_user_id} to fraud list."
                    elif fraud_action == 'remove' and fraud_user_id:
                        delete_fraud_list(fraud_user_id)
                        log_id = str(uuid.uuid4())
                        insert_admin_log(log_id, user['id'], request.remote_addr or 'localhost', f"Removed user {fraud_user_id} from fraud list.")
                        fraud_action_success = f"Removed user {fraud_user_id} from fraud list."
                    else:
                        fraud_action_error = 'Invalid fraud action or missing fields.'
                except Exception as e:
                    fraud_action_error = 'Failed to process fraud action: ' + str(e)
        elif 'role_action' in request.form and request.form.get('role_action') == 'change':
            if not has_permission(user['id'], 'perm_manage_users'):
                role_action_error = 'Permission denied.'
            else:
                role_user_id = request.form.get('role_user_id')
                new_role = request.form.get('new_role')
                if not role_user_id or not new_role:
                    role_action_error = 'All fields are required.'
                else:
                    try:
                        new_role_id = get_role_id_by_name(new_role)
                        if not new_role_id:
                            role_action_error = 'Invalid role selected.'
                        else:
                            update_user_role(role_user_id, new_role_id)
                            log_id = str(uuid.uuid4())
                            insert_admin_log(log_id, user['id'], request.remote_addr or 'localhost', f"Changed role of user {role_user_id} to {new_role}")
                            role_action_success = f"Changed role of user {role_user_id} to {new_role}."
                    except Exception as e:
                        role_action_error = 'Failed to change role: ' + str(e)
        elif 'perm_action' in request.form:
            if not has_permission(user['id'], 'perm_manage_permissions'):
                perm_action_error = 'Permission denied.'
            else:
                perm_action = request.form.get('perm_action')
                perm_role_id = request.form.get('perm_role_id')
                perm_permission_id = request.form.get('perm_permission_id')
                if not perm_role_id or not perm_permission_id:
                    perm_action_error = 'All fields are required.'
                else:
                    try:
                        if perm_action == 'add':
                            add_permission_to_role(perm_role_id, perm_permission_id)
                            log_id = str(uuid.uuid4())
                            insert_admin_log(log_id, user['id'], request.remote_addr or 'localhost', f"Added permission {perm_permission_id} to role {perm_role_id}")
                            perm_action_success = 'Permission added to role.'
                        elif perm_action == 'remove':
                            remove_permission_from_role(perm_role_id, perm_permission_id)
                            log_id = str(uuid.uuid4())
                            insert_admin_log(log_id, user['id'], request.remote_addr or 'localhost', f"Removed permission {perm_permission_id} from role {perm_role_id}")
                            perm_action_success = 'Permission removed from role.'
                        else:
                            perm_action_error = 'Invalid permission action.'
                    except Exception as e:
                        perm_action_error = 'Failed to update permissions: ' + str(e)
        # Handle agent money request approval/rejection
        if request.method == 'POST':
            if 'request_id' in request.form and 'action' in request.form:
                request_id = request.form.get('request_id')
                action = request.form.get('action')  # 'approved' or 'rejected'
                note = request.form.get('note')
                if action == 'approved':
                    success = approve_agent_money_request(request_id, user['id'])
                    if success:
                        req = get_agent_money_request_by_id(request_id)
                        if req:
                            create_notification(req['agent_id'], f"Your money request for ${req['amount']} has been approved and added to your balance.")
                        flash('Request approved and agent balance updated!', 'success')
                    else:
                        flash('Request not found or already processed.', 'danger')
                elif action == 'rejected':
                    update_agent_money_request_status(request_id, user['id'], 'rejected', note)
                    req = get_agent_money_request_by_id(request_id)
                    if req:
                        create_notification(req['agent_id'], f"Your money request for ${req['amount']} was rejected. Reason: {note or 'No reason provided.'}")
                    flash('Request rejected.', 'warning')

    admin_id = user['id']
    pending_money_request_count = get_pending_agent_money_request_count(admin_id)
    agent_money_requests = get_agent_money_requests_for_admin(admin_id)
    notifications = get_recent_notifications(user['id'], limit=10)
    notification_count = sum(1 for n in notifications if not n['is_read'])
    # Fetch analytics data for the analytics section
    analytics_results = {
        'user_summary': AdvancedReportingUtils.get_user_transaction_summary()[:5],
        'daily_analytics': AdvancedReportingUtils.get_daily_analytics()[:3],
        'high_risk_users': AdvancedReportingUtils.get_high_risk_users()[:3],
        'fraud_insights': AdvancedReportingUtils.get_fraud_detection_insights(),
        'monthly_report': AdvancedReportingUtils.get_monthly_transaction_report()
    }
    return render_template(
        'admin_dashboard.html',
        user=user,
        agents=agents,
        users=users,
        budgets=budgets,
        my_transactions=my_transactions,
        transactions=transactions,
        frauds=frauds,
        admin_logs=admin_logs,
        add_money_success=add_money_success,
        add_money_error=add_money_error,
        fraud_action_success=fraud_action_success,
        fraud_action_error=fraud_action_error,
        role_action_success=role_action_success,
        role_action_error=role_action_error,
        roles=roles,
        permissions=permissions,
        role_permissions_map=role_permissions_map,
        perm_action_success=perm_action_success,
        perm_action_error=perm_action_error,
        pending_money_request_count=pending_money_request_count,
        agent_money_requests=agent_money_requests,
        notifications=notifications,
        notification_count=notification_count,
        results=analytics_results
    )

@admin_bp.route('/admin/agent-money-requests', methods=['GET', 'POST'])
def admin_agent_money_requests():
    admin_id = session.get('user_id')
    user = get_current_user()
    agents = get_agents()
    users = get_all_users()
    budgets = get_user_budgets(user['id'])
    my_transactions = get_recent_transactions(user['id'])
    transactions = get_all_transactions()
    frauds = get_all_frauds()
    try:
        admin_logs = get_admin_logs()
    except Exception:
        admin_logs = []
    add_money_success = None
    add_money_error = None
    fraud_action_success = None
    fraud_action_error = None
    role_action_success = None
    role_action_error = None
    perm_action_success = None
    perm_action_error = None
    roles = get_all_roles()
    permissions = get_all_permissions()
    role_permissions_map = {}
    for role in roles:
        role_permissions_map[role['id']] = [p['id'] for p in get_permissions_for_role(role['id'])]
    pending_money_request_count = get_pending_agent_money_request_count(admin_id)
    agent_money_requests = get_agent_money_requests_for_admin(admin_id)
    notifications = get_recent_notifications(user['id'], limit=10)
    notification_count = sum(1 for n in notifications if not n['is_read'])

    return render_template(
        'admin_dashboard.html',
        user=user,
        agents=agents,
        users=users,
        budgets=budgets,
        my_transactions=my_transactions,
        transactions=transactions,
        frauds=frauds,
        admin_logs=admin_logs,
        add_money_success=add_money_success,
        add_money_error=add_money_error,
        fraud_action_success=fraud_action_success,
        fraud_action_error=fraud_action_error,
        role_action_success=role_action_success,
        role_action_error=role_action_error,
        roles=roles,
        permissions=permissions,
        role_permissions_map=role_permissions_map,
        perm_action_success=perm_action_success,
        perm_action_error=perm_action_error,
        pending_money_request_count=pending_money_request_count,
        agent_money_requests=agent_money_requests,
        notifications=notifications,
        notification_count=notification_count
    )

@admin_bp.route('/admin/api/daily-analytics')
def admin_daily_analytics_api():
    try:
        analytics = AdvancedReportingUtils.get_daily_analytics()
        return jsonify({'success': True, 'data': analytics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/admin/api/high-risk-users')
def admin_high_risk_users_api():
    try:
        users = AdvancedReportingUtils.get_high_risk_users()
        return jsonify({'success': True, 'data': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/admin/api/fraud-insights')
def admin_fraud_insights_api():
    try:
        insights = AdvancedReportingUtils.get_fraud_detection_insights()
        return jsonify({'success': True, 'data': insights})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/admin/api/monthly-report')
def admin_monthly_report_api():
    try:
        report = AdvancedReportingUtils.get_monthly_transaction_report()
        return jsonify({'success': True, 'data': report})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/admin/api/user-stats/<user_id>')
def admin_user_statistics_api(user_id):
    try:
        stats = AdvancedSQLUtils.calculate_user_statistics(user_id)
        risk_score = AdvancedSQLUtils.get_user_risk_score(user_id)
        account_age = AdvancedSQLUtils.calculate_account_age(user_id)
        velocity = AdvancedSQLUtils.calculate_transaction_velocity(user_id, 30)
        return jsonify({
            'success': True,
            'data': {
                'statistics': stats,
                'risk_score': risk_score,
                'account_age_days': account_age,
                'monthly_velocity': velocity
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/admin/api/transaction-history/<user_id>')
def admin_transaction_history_api(user_id):
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        history = AdvancedSQLUtils.get_user_transaction_history(user_id, limit, offset)
        return jsonify({
            'success': True,
            'data': history,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'returned': len(history)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
