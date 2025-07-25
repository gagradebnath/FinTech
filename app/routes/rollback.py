from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.utils.transaction_utils import (
    rollback_transaction, get_transaction_status, backup_user_balance,
    restore_user_balance, auto_rollback_failed_transactions,
    get_transaction_history_with_status, get_failed_transactions,
    get_system_audit_log
)
from app.utils.auth import login_required
import logging

rollback_bp = Blueprint('rollback', __name__)
logger = logging.getLogger(__name__)

@rollback_bp.route('/rollback/dashboard')
@login_required
def rollback_dashboard():
    """Rollback management dashboard for admins"""
    # Check if user is admin
    if session.get('role') != 'admin':
        return redirect(url_for('user.dashboard'))
    
    # Get failed transactions
    failed_transactions = get_failed_transactions(limit=20)
    
    # Get recent audit logs
    audit_logs = get_system_audit_log(limit=50, operation_type='ROLLBACK')
    
    return render_template('rollback_dashboard.html', 
                         failed_transactions=failed_transactions,
                         audit_logs=audit_logs)

@rollback_bp.route('/rollback/transaction', methods=['POST'])
@login_required
def rollback_transaction_route():
    """Rollback a specific transaction"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        reason = data.get('reason', 'Admin rollback')
        
        if not transaction_id:
            return jsonify({'success': False, 'message': 'Transaction ID required'}), 400
        
        # Check transaction status first
        status, can_rollback, status_message = get_transaction_status(transaction_id)
        
        if not can_rollback:
            return jsonify({'success': False, 'message': status_message}), 400
        
        # Perform rollback
        success, message = rollback_transaction(transaction_id, reason, session.get('user_id'))
        
        if success:
            logger.info(f"Admin {session['user_id']} rolled back transaction {transaction_id}")
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 500
            
    except Exception as e:
        logger.error(f"Rollback error: {e}")
        return jsonify({'success': False, 'message': f'Rollback failed: {str(e)}'}), 500

@rollback_bp.route('/rollback/status/<transaction_id>')
@login_required
def check_transaction_status(transaction_id):
    """Check if a transaction can be rolled back"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        status, can_rollback, message = get_transaction_status(transaction_id)
        
        return jsonify({
            'success': True,
            'status': status,
            'can_rollback': can_rollback,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({'success': False, 'message': f'Status check failed: {str(e)}'}), 500

@rollback_bp.route('/rollback/backup/user', methods=['POST'])
@login_required
def backup_user_balance_route():
    """Create a backup of user balance"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        operation_type = data.get('operation_type', 'Manual admin backup')
        
        if not user_id:
            return jsonify({'success': False, 'message': 'User ID required'}), 400
        
        success, message, backup_id = backup_user_balance(user_id, operation_type, session.get('user_id'))
        
        if success:
            logger.info(f"Admin {session['user_id']} created backup for user {user_id}: {backup_id}")
            return jsonify({'success': True, 'message': message, 'backup_id': backup_id})
        else:
            return jsonify({'success': False, 'message': message}), 500
            
    except Exception as e:
        logger.error(f"Backup error: {e}")
        return jsonify({'success': False, 'message': f'Backup failed: {str(e)}'}), 500

@rollback_bp.route('/rollback/restore/user', methods=['POST'])
@login_required
def restore_user_balance_route():
    """Restore user balance from backup"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        backup_id = data.get('backup_id')
        reason = data.get('reason', 'Manual admin restore')
        
        if not backup_id:
            return jsonify({'success': False, 'message': 'Backup ID required'}), 400
        
        success, message = restore_user_balance(backup_id, reason, session.get('user_id'))
        
        if success:
            logger.info(f"Admin {session['user_id']} restored balance from backup {backup_id}")
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 500
            
    except Exception as e:
        logger.error(f"Restore error: {e}")
        return jsonify({'success': False, 'message': f'Restore failed: {str(e)}'}), 500

@rollback_bp.route('/rollback/auto', methods=['POST'])
@login_required
def auto_rollback_route():
    """Auto-rollback failed transactions"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        hours_threshold = data.get('hours_threshold', 24)
        
        success, message, rolled_back_count = auto_rollback_failed_transactions(hours_threshold, session.get('user_id'))
        
        if success:
            logger.info(f"Admin {session['user_id']} performed auto-rollback: {rolled_back_count} transactions")
            return jsonify({
                'success': True, 
                'message': message, 
                'rolled_back_count': rolled_back_count
            })
        else:
            return jsonify({'success': False, 'message': message}), 500
            
    except Exception as e:
        logger.error(f"Auto-rollback error: {e}")
        return jsonify({'success': False, 'message': f'Auto-rollback failed: {str(e)}'}), 500

@rollback_bp.route('/rollback/history/<user_id>')
@login_required
def transaction_history_with_status(user_id):
    """Get transaction history with rollback status"""
    if session.get('role') != 'admin' and session.get('user_id') != user_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        transactions = get_transaction_history_with_status(user_id, limit, offset)
        
        return jsonify({
            'success': True,
            'transactions': transactions,
            'total_count': len(transactions)
        })
        
    except Exception as e:
        logger.error(f"Transaction history error: {e}")
        return jsonify({'success': False, 'message': f'Failed to get history: {str(e)}'}), 500

@rollback_bp.route('/rollback/failed')
@login_required
def get_failed_transactions_route():
    """Get failed transactions for admin review"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        limit = request.args.get('limit', 50, type=int)
        failed_transactions = get_failed_transactions(limit)
        
        return jsonify({
            'success': True,
            'failed_transactions': failed_transactions,
            'total_count': len(failed_transactions)
        })
        
    except Exception as e:
        logger.error(f"Failed transactions error: {e}")
        return jsonify({'success': False, 'message': f'Failed to get failed transactions: {str(e)}'}), 500

@rollback_bp.route('/rollback/audit')
@login_required
def get_audit_log_route():
    """Get system audit log"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        limit = request.args.get('limit', 100, type=int)
        operation_type = request.args.get('operation_type')
        
        audit_logs = get_system_audit_log(limit, operation_type)
        
        return jsonify({
            'success': True,
            'audit_logs': audit_logs,
            'total_count': len(audit_logs)
        })
        
    except Exception as e:
        logger.error(f"Audit log error: {e}")
        return jsonify({'success': False, 'message': f'Failed to get audit log: {str(e)}'}), 500
