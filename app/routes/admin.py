from flask import Blueprint
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET'])
def get_admin():
    return {'message': 'Admin endpoint'}
