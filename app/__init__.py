from flask import Flask
import sqlite3
from .routes import register_blueprints

def get_db_connection():
    conn = sqlite3.connect('fin_guard.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    app.get_db_connection = staticmethod(get_db_connection)
    register_blueprints(app)
    return app
