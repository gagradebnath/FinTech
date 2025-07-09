"""
Hot reload endpoint for Solidity blockchain accounts
"""

from flask import Blueprint, jsonify
from app.utils.hybrid_blockchain import hybrid_blockchain

reload_bp = Blueprint('reload', __name__)

@reload_bp.route('/reload-blockchain-accounts', methods=['POST'])
def reload_blockchain_accounts():
    """Reload Solidity blockchain accounts from deployment-info.json"""
    try:
        if not hybrid_blockchain.solidity_available:
            return jsonify({
                'success': False,
                'error': 'Solidity blockchain not available'
            }), 400
        
        # Reload accounts
        success = hybrid_blockchain.solidity_blockchain.reload_accounts()
        
        if success:
            # Test specific users
            test_results = {}
            test_users = ['user', 'user15', 'admin']
            
            for user_id in test_users:
                balance_info = hybrid_blockchain.solidity_blockchain.get_account_balance(user_id)
                test_results[user_id] = 'found' if 'error' not in balance_info else balance_info['error']
            
            return jsonify({
                'success': True,
                'message': f'Reloaded {len(hybrid_blockchain.solidity_blockchain.accounts)} accounts',
                'test_results': test_results
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to reload accounts'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
