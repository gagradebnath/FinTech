from flask import Blueprint
agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/agent', methods=['GET'])
def get_agent():
    return {'message': 'Agent endpoint'}
