from flask import Blueprint, jsonify, request, render_template
from app.utils.blockchain import (
    finguard_blockchain, 
    verify_transaction, 
    get_blockchain_stats,
    process_blockchain_transaction
)
from .user import get_current_user
from app.utils.permissions_utils import has_permission

blockchain_bp = Blueprint('blockchain', __name__)

@blockchain_bp.route('/blockchain/stats')
def blockchain_stats():
    """Get blockchain statistics"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    stats = get_blockchain_stats()
    return jsonify(stats)

@blockchain_bp.route('/blockchain/verify/<transaction_id>')
def verify_transaction_endpoint(transaction_id):
    """Verify a specific transaction"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    verification = verify_transaction(transaction_id)
    return jsonify(verification)

@blockchain_bp.route('/blockchain/explorer')
def blockchain_explorer():
    """Blockchain explorer page"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get recent blocks
    recent_blocks = []
    for block in finguard_blockchain.chain[-10:]:  # Last 10 blocks
        block_info = {
            'index': block.index,
            'hash': block.hash,
            'previous_hash': block.previous_hash,
            'timestamp': block.timestamp.isoformat(),
            'transaction_count': len(block.transactions),
            'transactions': [tx.to_dict() for tx in block.transactions]
        }
        recent_blocks.append(block_info)
    
    stats = get_blockchain_stats()
    
    return render_template('blockchain_explorer.html', 
                         blocks=recent_blocks, 
                         stats=stats)

@blockchain_bp.route('/blockchain/user-history')
def user_blockchain_history():
    """Get user's blockchain transaction history"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    history = finguard_blockchain.get_transaction_history(user['id'])
    return jsonify({'transactions': history})

@blockchain_bp.route('/blockchain/validate')
def validate_blockchain():
    """Validate entire blockchain integrity"""
    user = get_current_user()
    if not user or not has_permission(user['id'], 'perm_admin_access'):
        return jsonify({'error': 'Admin access required'}), 403
    
    is_valid = finguard_blockchain.is_chain_valid()
    return jsonify({'valid': is_valid})

@blockchain_bp.route('/api/blockchain/balance/<user_id>')
def get_blockchain_balance(user_id):
    """Get user balance from blockchain"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Users can only check their own balance, admins can check any
    if user['id'] != user_id and not has_permission(user['id'], 'perm_admin_access'):
        return jsonify({'error': 'Permission denied'}), 403
    
    balance = finguard_blockchain.get_balance(user_id)
    return jsonify({'user_id': user_id, 'blockchain_balance': balance})
