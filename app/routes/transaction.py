from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
import uuid
from .user import get_current_user
from app.utils.transaction_utils import get_user_by_id, send_money, lookup_user_by_identifier, is_user_flagged_fraud
from app.utils.permissions_utils import has_permission
from app.utils.overspending_detector import detect_overspending
transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/transaction', methods=['GET', 'POST'])
def save_transaction():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    error = None
    success = None
    if not has_permission(user['id'], 'perm_send_money'):
        return render_template('send_money.html', error='Permission denied.', success=None)
    if request.method == 'POST':
        recipient_identifier = request.form.get('recipient_identifier')
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method')
        note = request.form.get('note')
        location = request.form.get('location')
        recipient = lookup_user_by_identifier(recipient_identifier)
        if not recipient:
            error = 'Recipient not found.'
        elif recipient['id'] == user['id']:
            error = 'Cannot send money to yourself.'
        elif is_user_flagged_fraud(recipient['id']):
            error = 'Cannot send money: recipient is flagged for fraud.'
        else:
            ok, msg, updated_user = send_money(
                user['id'], recipient['id'], amount, payment_method, note, location, 'Transfer')
            if ok:
                success = msg
                user = updated_user
            else:
                error = msg
    return render_template('send_money.html', error=error, success=success)

@transaction_bp.route('/send-money', methods=['GET', 'POST'])
def send_money_route():
    user = get_current_user()
    if not user:
        return redirect(url_for('user.login'))
    error = None
    success = None
    overspending_warning = None
    
    if not has_permission(user['id'], 'perm_send_money'):
        return render_template('send_money.html', error='Permission denied.', success=None)
    
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
        
        recipient = lookup_user_by_identifier(recipient_identifier)

        # Basic validation first
        if not recipient:
            error = 'Recipient not found.'
        elif recipient['id'] == user['id']:
            error = 'Cannot send money to yourself.'
        elif is_user_flagged_fraud(recipient['id']):
            error = 'Cannot send money: recipient is flagged for fraud.'
        else:
            # Check for overspending
            try:
                amount_float = float(amount)
                overspending = detect_overspending(user['id'], note or 'Money transfer', amount_float)
                
                # If overspending detected and user hasn't confirmed yet
                if overspending['is_overspending'] and not confirm_overspending:
                    overspending_warning = {
                        'category': overspending['category'],
                        'budget': overspending['budget'],
                        'expense_amount': overspending['expense_amount'],
                        'overspending_amount': overspending['overspending_amount'],
                        'percentage_over': overspending['percentage_over'],
                        'message': overspending['message'],
                        'recipient_identifier': recipient_identifier,
                        'amount': amount,
                        'payment_method': payment_method,
                        'note': note,
                        'location': location
                    }
                    # Don't process transaction, show warning instead
                    return render_template('send_money.html', 
                                        error=error, 
                                        success=success, 
                                        overspending_warning=overspending_warning)
                
                # If no overspending or user confirmed, proceed with transaction
                category_note = f"{overspending.get('category', 'Other')} : {note}" if note else overspending.get('category', 'Money transfer')
                ok, msg, updated_user = send_money(
                    user['id'], recipient['id'], amount, payment_method, category_note, location, 'Transfer')
                
                if ok:
                    success = msg
                    user = updated_user
                    # Add overspending acknowledgment to success message if applicable
                    if overspending['is_overspending'] and confirm_overspending:
                        success += f" (Note: This transaction exceeded your {overspending['category']} budget by ${overspending['overspending_amount']:.2f})"
                else:
                    error = msg
                    
            except ValueError:
                error = 'Invalid amount specified.'
            except Exception as e:
                error = f'Error processing transaction: {str(e)}'
    
    return render_template('send_money.html', 
                          error=error, 
                          success=success, 
                          overspending_warning=overspending_warning)
