from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.utils.permissions_utils import has_permission

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
            try:
                conn = current_app.get_db_connection()
                # Look up user by id, email, or phone
                user = conn.execute('''
                    SELECT u.id FROM users u
                    LEFT JOIN contact_info c ON u.id = c.user_id
                    WHERE LOWER(u.id) = ? OR LOWER(c.email) = ? OR c.phone = ?
                ''', (identifier.lower(), identifier.lower(), identifier)).fetchone()
                if not user:
                    error = 'No user found with that ID, email, or phone.'
                else:
                    import uuid
                    conn.execute('INSERT INTO fraud_list (id, user_id, reported_user_id, reason) VALUES (?, ?, ?, ?)',
                                 (str(uuid.uuid4()), user_id, user['id'], reason))
                    conn.commit()
                    success = 'Fraud report submitted.'
                conn.close()
            except Exception as e:
                error = 'Failed to submit report: ' + str(e)
    return render_template('report_fraud.html', error=error, success=success)
