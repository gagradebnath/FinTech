"""
Blockchain management routes for FinGuard
Handles both Python and Solidity blockchain operations
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.utils.hybrid_blockchain import hybrid_blockchain
from app.utils.permissions_utils import has_permission
from app.routes.user import get_current_user

blockchain_mgmt_bp = Blueprint('blockchain_mgmt', __name__)

@blockchain_mgmt_bp.route('/blockchain/status')
def blockchain_status():
    """Get blockchain status information"""
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    
    # Check admin permissions for detailed status
    is_admin = has_permission(user['id'], 'perm_admin_access')
    
    status = hybrid_blockchain.get_blockchain_status()
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify(status)
    
    return render_template('blockchain_status.html', 
                         status=status, 
                         is_admin=is_admin,
                         user=user)

@blockchain_mgmt_bp.route('/blockchain/balance/<user_id>')
def get_blockchain_balance(user_id):
    """Get user's blockchain balance"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Authentication required"}), 401
    
    # Only allow users to view their own balance or admins to view any
    if user['id'] != user_id and not has_permission(user['id'], 'perm_admin_access'):
        return jsonify({"error": "Permission denied"}), 403
    
    balance = hybrid_blockchain.get_user_balance(user_id)
    return jsonify(balance)

@blockchain_mgmt_bp.route('/blockchain/budget-check', methods=['POST'])
def check_budget():
    """Check budget limits before transaction"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json()
    user_id = data.get('user_id', user['id'])
    category = data.get('category')
    amount = data.get('amount')
    
    # Only allow users to check their own budget or admins
    if user['id'] != user_id and not has_permission(user['id'], 'perm_admin_access'):
        return jsonify({"error": "Permission denied"}), 403
    
    if not category or amount is None:
        return jsonify({"error": "Category and amount required"}), 400
    
    try:
        amount = float(amount)
        result = hybrid_blockchain.check_budget_limits(user_id, category, amount)
        return jsonify(result)
    except ValueError:
        return jsonify({"error": "Invalid amount"}), 400

@blockchain_mgmt_bp.route('/blockchain/reinitialize', methods=['POST'])
def reinitialize_blockchain():
    """Reinitialize blockchain connections (admin only)"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Authentication required"}), 401
    
    if not has_permission(user['id'], 'perm_admin_access'):
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        # Reinitialize the hybrid blockchain
        global hybrid_blockchain
        hybrid_blockchain = hybrid_blockchain.__class__()
        
        status = hybrid_blockchain.get_blockchain_status()
        return jsonify({
            "success": True,
            "message": "Blockchain reinitialized",
            "status": status
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
