from flask import Blueprint
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['GET'])
def get_chat():
    return {'message': 'Chat endpoint'}
