from flask import Blueprint
fraud_bp = Blueprint('fraud', __name__)

@fraud_bp.route('/fraud', methods=['GET'])
def get_fraud():
    return {'message': 'Fraud endpoint'}
