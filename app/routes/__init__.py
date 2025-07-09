from .user import user_bp
from .admin import admin_bp
from .agent import agent_bp
from .transaction import transaction_bp
from .budget import budget_bp
from .fraud import fraud_bp
from .chat import chat_bp
from .blockchain import blockchain_bp
from .blockchain_mgmt import blockchain_mgmt_bp
from .debug import debug_bp
from .reload import reload_bp

def register_blueprints(app):
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(fraud_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(blockchain_bp)
    app.register_blueprint(blockchain_mgmt_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(reload_bp)
