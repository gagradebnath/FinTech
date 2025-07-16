"""
Blockchain management routes for FinGuard application.
Provides endpoints for blockchain validation, fraud detection, and analytics.
"""

from flask import Blueprint, jsonify, request, render_template, redirect, url_for, session
from app.utils.blockchain_utils import (
    verify_entire_blockchain, 
    get_blockchain_analytics,
    get_user_blockchain_summary,
    flag_user_as_fraud
)
from app.utils.user_utils import get_current_user
from app.utils.jwt_auth import token_required, get_current_user_from_jwt
from app.utils.permissions_utils import has_permission
from app.utils.fraud_utils import get_fraud_reports
import json

blockchain_bp = Blueprint('blockchain', __name__)

@blockchain_bp.route('/api/blockchain/verify', methods=['POST'])
@token_required
def verify_blockchain_api():
    """API endpoint to verify entire blockchain integrity"""
    user = get_current_user_from_jwt()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Check if user has admin permissions
    if not has_permission(user['id'], 'perm_admin_access'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        is_valid, errors = verify_entire_blockchain()
        
        return jsonify({
            'success': True,
            'blockchain_valid': is_valid,
            'errors': errors,
            'message': 'Blockchain verification complete'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/api/blockchain/analytics', methods=['GET'])
@token_required
def blockchain_analytics_api():
    """API endpoint to get blockchain analytics"""
    user = get_current_user_from_jwt()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Check if user has admin permissions
    if not has_permission(user['id'], 'perm_admin_access'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        analytics = get_blockchain_analytics()
        
        return jsonify({
            'success': True,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/api/blockchain/user/<user_id>', methods=['GET'])
@token_required
def user_blockchain_summary_api(user_id):
    """API endpoint to get user's blockchain summary"""
    current_user = get_current_user_from_jwt()
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Users can only view their own blockchain summary unless they're admin
    if current_user['id'] != user_id and not has_permission(current_user['id'], 'perm_admin_access'):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        summary = get_user_blockchain_summary(user_id)
        
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/api/blockchain/flag-fraud', methods=['POST'])
@token_required
def flag_fraud_api():
    """API endpoint to manually flag user as fraud"""
    user = get_current_user_from_jwt()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Check if user has admin permissions
    if not has_permission(user['id'], 'perm_admin_access'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        target_user_id = data.get('user_id')
        reason = data.get('reason', 'Manual fraud flag by admin')
        
        if not target_user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        success = flag_user_as_fraud(target_user_id, f"Admin Flag: {reason}")
        
        if success:
            return jsonify({
                'success': True,
                'message': f'User {target_user_id} flagged for fraud'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'User already flagged or error occurred'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/blockchain-dashboard')
def blockchain_dashboard():
    """Web interface for blockchain management"""
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    
    # Check if user has admin permissions
    if not has_permission(user['id'], 'perm_admin_access'):
        return render_template('error.html', error='Admin access required'), 403
    
    try:
        # Get blockchain analytics
        analytics = get_blockchain_analytics()
        
        # Get recent fraud reports
        fraud_reports = get_fraud_reports(limit=20)
        
        # Verify blockchain integrity
        is_valid, errors = verify_entire_blockchain()
        
        return render_template(
            'blockchain_dashboard.html',
            user=user,
            analytics=analytics,
            fraud_reports=fraud_reports,
            blockchain_valid=is_valid,
            blockchain_errors=errors
        )
        
    except Exception as e:
        return render_template(
            'error.html',
            error=f'Error loading blockchain dashboard: {str(e)}'
        )

@blockchain_bp.route('/blockchain-user/<user_id>')
def blockchain_user_detail(user_id):
    """Web interface for user blockchain details"""
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('user.login'))
    
    # Users can only view their own blockchain details unless they're admin
    if current_user['id'] != user_id and not has_permission(current_user['id'], 'perm_admin_access'):
        return render_template('error.html', error='Permission denied'), 403
    
    try:
        # Get user's blockchain summary
        summary = get_user_blockchain_summary(user_id)
        
        # Get user's basic info
        from app.utils.transaction_utils import get_user_by_id
        user_info = get_user_by_id(user_id)
        
        return render_template(
            'blockchain_user_detail.html',
            user=current_user,
            target_user=user_info,
            blockchain_summary=summary
        )
        
    except Exception as e:
        return render_template(
            'error.html',
            error=f'Error loading user blockchain details: {str(e)}'
        )

@blockchain_bp.route('/api/blockchain/detect-fraud', methods=['POST'])
@token_required
def detect_fraud_api():
    """API endpoint to run fraud detection across all users"""
    user = get_current_user_from_jwt()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Check if user has admin permissions
    if not has_permission(user['id'], 'perm_admin_access'):
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        from app.utils.blockchain_utils import get_blockchain_connection
        connection = get_blockchain_connection()
        
        fraud_detected = []
        
        with connection.cursor() as cursor:
            # Get all users with blockchain transactions
            cursor.execute("""
                SELECT DISTINCT bt.user_id, u.first_name, u.last_name
                FROM blockchain_transactions bt
                JOIN users u ON bt.user_id = u.id
                ORDER BY bt.user_id
            """)
            
            users = cursor.fetchall()
            
            for user_data in users:
                user_id = user_data['user_id']
                
                # Check blockchain integrity for this user
                summary = get_user_blockchain_summary(user_id)
                
                # Look for suspicious patterns
                if summary.get('total_blocks', 0) == 0:
                    continue
                
                # Check for impossible balance changes
                cursor.execute("""
                    SELECT bt.amount, bt.current_balance, bt.timestamp
                    FROM blockchain_transactions bt
                    WHERE bt.user_id = %s
                    ORDER BY bt.timestamp ASC
                """, (user_id,))
                
                transactions = cursor.fetchall()
                
                if len(transactions) > 1:
                    for i in range(1, len(transactions)):
                        prev_balance = transactions[i-1]['current_balance']
                        current_amount = transactions[i]['amount']
                        current_balance = transactions[i]['current_balance']
                        
                        expected_balance = prev_balance + current_amount
                        
                        # Allow for small rounding errors
                        if abs(expected_balance - current_balance) > 0.01:
                            fraud_detected.append({
                                'user_id': user_id,
                                'user_name': f"{user_data['first_name']} {user_data['last_name']}",
                                'reason': f'Balance inconsistency: Expected {expected_balance}, Got {current_balance}',
                                'timestamp': transactions[i]['timestamp']
                            })
                            
                            # Flag user as fraud
                            flag_user_as_fraud(user_id, f"Automated Detection: Balance inconsistency detected")
                            break
        
        return jsonify({
            'success': True,
            'fraud_detected': fraud_detected,
            'total_users_checked': len(users),
            'total_fraud_detected': len(fraud_detected)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if 'connection' in locals():
            connection.close()
