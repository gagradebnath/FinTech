import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    
    # MySQL Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '6251wnwnwn')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'fin_guard')
    
    # SQLAlchemy Database URI for MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
