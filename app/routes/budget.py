from flask import Blueprint
budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budget', methods=['GET'])
def get_budget():
    return {'message': 'Budget endpoint'}
