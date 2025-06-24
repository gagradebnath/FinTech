from flask import Flask
import sqlite3
import json
from .routes import register_blueprints

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'keys') and hasattr(obj, 'values'):
            return dict(obj)
        return super(CustomJSONEncoder, self).default(obj)

def get_db_connection():
    conn = sqlite3.connect('fin_guard.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_app():
    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder
    app.config.from_object('app.config.Config')
    app.get_db_connection = staticmethod(get_db_connection)
    
    # Add custom filter to handle SQLite Row objects in templates
    @app.template_filter('tojson_safe')
    def tojson_safe(obj):
        if hasattr(obj, 'keys') and hasattr(obj, 'values'):
            obj = dict(obj)
        return json.dumps(obj)
    
    register_blueprints(app)
    return app
