from flask import Blueprint, jsonify, request
from app.utils.transaction_utils import send_money, lookup_user_by_identifier, get_user_by_id
from app.utils.user_utils import get_current_user

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug/send-money-test', methods=['GET', 'POST'])
def debug_send_money():
    """Debug route to test send money functionality"""
    try:
        if request.method == 'GET':
            # Test basic functionality
            results = {
                "status": "testing",
                "tests": []
            }
            
            # Test 1: Get current user
            try:
                user = get_current_user()
                if user:
                    results["tests"].append({
                        "test": "get_current_user",
                        "status": "success",
                        "data": {
                            "user_id": user['id'],
                            "name": f"{user['first_name']} {user['last_name']}",
                            "balance": str(user['balance'])
                        }
                    })
                else:
                    results["tests"].append({
                        "test": "get_current_user",
                        "status": "failed",
                        "error": "No user found"
                    })
            except Exception as e:
                results["tests"].append({
                    "test": "get_current_user",
                    "status": "error",
                    "error": str(e)
                })
            
            # Test 2: User lookup
            try:
                test_user = lookup_user_by_identifier('user2')
                if test_user:
                    results["tests"].append({
                        "test": "lookup_user_by_identifier",
                        "status": "success",
                        "data": {
                            "found_user": test_user['id']
                        }
                    })
                else:
                    results["tests"].append({
                        "test": "lookup_user_by_identifier",
                        "status": "failed",
                        "error": "User not found"
                    })
            except Exception as e:
                results["tests"].append({
                    "test": "lookup_user_by_identifier",
                    "status": "error",
                    "error": str(e)
                })
            
            return jsonify(results)
        
        elif request.method == 'POST':
            # Test actual send money
            data = request.get_json() or {}
            sender_id = data.get('sender_id', 'user')
            recipient_id = data.get('recipient_id', 'user2')
            amount = data.get('amount', 1.0)
            
            try:
                success, message, updated_user = send_money(
                    sender_id, recipient_id, amount, 
                    'bank', 'Debug test transaction', 
                    'Debug Location', 'Transfer'
                )
                
                return jsonify({
                    "status": "completed",
                    "success": success,
                    "message": message,
                    "updated_user": {
                        "id": updated_user['id'] if updated_user else None,
                        "balance": str(updated_user['balance']) if updated_user else None
                    } if updated_user else None
                })
                
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": str(e)
                })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Debug route error: {str(e)}"
        })

@debug_bp.route('/debug/simple-test')
def simple_test():
    """Very simple test route"""
    return jsonify({
        "status": "ok",
        "message": "Debug route is working"
    })
