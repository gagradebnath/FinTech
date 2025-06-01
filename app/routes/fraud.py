from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.utils.permissions_utils import has_permission
from app.utils.fraud_utils import lookup_user_by_identifier, add_fraud_report

fraud_bp = Blueprint('fraud', __name__)

@fraud_bp.route('/fraud', methods=['GET'])
def get_fraud():
    return {'message': 'Fraud endpoint'}

@fraud_bp.route('/report-fraud', methods=['GET', 'POST'])
def report_fraud():
    user_id = session.get('user_id')
    error = None
    success = None
    if user_id and not has_permission(user_id, 'report_fraud'):
        return render_template('report_fraud.html', error='Permission denied.', success=None)
    if request.method == 'POST':
        identifier = request.form.get('reported_user_identifier')
        reason = request.form.get('reason')
        if not identifier or not reason:
            error = 'All fields are required.'
        else:
            user = lookup_user_by_identifier(identifier)
            if not user:
                error = 'No user found with that ID, email, or phone.'
            else:
                ok, err = add_fraud_report(user_id, user['id'], reason)
                if ok:
                    success = 'Fraud report submitted.'
                else:
                    error = 'Failed to submit report: ' + str(err)
    return render_template('report_fraud.html', error=error, success=success)
