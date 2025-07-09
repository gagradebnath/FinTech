from flask import Blueprint, render_template, request, redirect, url_for
from .user import get_current_user
from app.utils.transaction_utils import process_send_money_with_overspending
transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/transaction', methods=['GET', 'POST'])
def save_transaction():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    error = None
    success = None
    
    if request.method == 'POST':
        recipient_identifier = request.form.get('recipient_identifier')
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method')
        note = request.form.get('note')
        location = request.form.get('location')
        
        # Process transaction using utility function (without overspending warnings for this route)
        try:
            result = process_send_money_with_overspending(
                user['id'], 
                recipient_identifier, 
                amount, 
                payment_method, 
                note, 
                location, 
                confirm_overspending=True  # Skip overspending warnings for this simple route
            )
            
            if result['success']:
                success = result['message']
                user = result['updated_user']
            else:
                error = result['error']
                
        except Exception as e:
            error = f'Error processing transaction: {str(e)}'
    
    return render_template('send_money.html', error=error, success=success)

@transaction_bp.route('/send-money', methods=['GET', 'POST'])
def send_money_route():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    error = None
    success = None
    overspending_warning = None
    
    # Get user balance info for display
    from app.utils.transaction_utils import get_user_balance_info
    balance_info = get_user_balance_info(user['id'])
    user_balance = balance_info['balance'] if balance_info else 0.0
    
    if request.method == 'POST':
        recipient_identifier = request.form.get('recipient_identifier')
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method')
        note = request.form.get('note')
        location = request.form.get('location')
        confirm_overspending = request.form.get('confirm_overspending')
        cancel_transaction = request.form.get('cancel_transaction')
        
        # Handle cancellation
        if cancel_transaction:
            return redirect(url_for('user.dashboard'))
        
        # Process transaction using utility function
        try:
            result = process_send_money_with_overspending(
                user['id'], 
                recipient_identifier, 
                amount, 
                payment_method, 
                note, 
                location, 
                bool(confirm_overspending)
            )
            
            if result['success']:
                success = result['message']
                user = result['updated_user']
                # Update balance info after successful transaction
                balance_info = get_user_balance_info(user['id'])
                user_balance = balance_info['balance'] if balance_info else 0.0
            elif result['overspending_warning']:
                overspending_warning = result['overspending_warning']
            else:
                error = result['error']
                
        except Exception as e:
            error = f'Error processing transaction: {str(e)}'
    
    return render_template('send_money.html', 
                          error=error, 
                          success=success, 
                          overspending_warning=overspending_warning,
                          user_balance=user_balance)
