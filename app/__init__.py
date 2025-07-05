from flask import Flask
import pymysql
import json
from .routes import register_blueprints

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'keys') and hasattr(obj, 'values'):
            return dict(obj)
        return super(CustomJSONEncoder, self).default(obj)

def get_db_connection():
    """Get MySQL database connection"""
    from flask import current_app
    
    connection = pymysql.connect(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        database=current_app.config['MYSQL_DATABASE'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,  # We'll handle commits manually
        use_unicode=True,
        sql_mode='TRADITIONAL'
    )
    return connection

def create_app():
    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder
    app.config.from_object('app.config.Config')
    app.get_db_connection = staticmethod(get_db_connection)
    
    # Add custom filter to handle MySQL result objects in templates
    @app.template_filter('tojson_safe')
    def tojson_safe(obj):
        if hasattr(obj, 'keys') and hasattr(obj, 'values'):
            obj = dict(obj)
        return json.dumps(obj)
    
    # Add datetime formatting filters for MySQL datetime objects
    @app.template_filter('format_date')
    def format_date(datetime_obj):
        """Format datetime object to date string (YYYY-MM-DD)"""
        if datetime_obj is None:
            return 'N/A'
        
        # Handle datetime objects
        if hasattr(datetime_obj, 'strftime'):
            return datetime_obj.strftime('%Y-%m-%d')
        
        # Handle string datetime
        try:
            from datetime import datetime
            if isinstance(datetime_obj, str):
                # Try parsing common datetime formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                    try:
                        parsed_dt = datetime.strptime(datetime_obj, fmt)
                        return parsed_dt.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
                # If all parsing fails, try split as fallback
                if ' ' in datetime_obj:
                    return datetime_obj.split(' ')[0]
                else:
                    return datetime_obj
        except Exception:
            pass
        
        return str(datetime_obj)
    
    @app.template_filter('format_time')
    def format_time(datetime_obj):
        """Format datetime object to time string (HH:MM:SS)"""
        if datetime_obj is None:
            return 'N/A'
        
        # Handle datetime objects
        if hasattr(datetime_obj, 'strftime'):
            return datetime_obj.strftime('%H:%M:%S')
        
        # Handle string datetime
        try:
            from datetime import datetime
            if isinstance(datetime_obj, str):
                # Try parsing common datetime formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%H:%M:%S']:
                    try:
                        parsed_dt = datetime.strptime(datetime_obj, fmt)
                        return parsed_dt.strftime('%H:%M:%S')
                    except ValueError:
                        continue
                # If all parsing fails, try split as fallback
                if ' ' in datetime_obj:
                    parts = datetime_obj.split(' ')
                    if len(parts) > 1:
                        return parts[1]
                return 'N/A'
        except Exception:
            pass
        
        return str(datetime_obj)
    
    @app.template_filter('format_datetime')
    def format_datetime(datetime_obj):
        """Format datetime object to full datetime string"""
        if datetime_obj is None:
            return 'N/A'
        
        # Handle datetime objects
        if hasattr(datetime_obj, 'strftime'):
            return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        
        # Handle string datetime
        try:
            from datetime import datetime
            if isinstance(datetime_obj, str):
                # Try parsing common datetime formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S']:
                    try:
                        parsed_dt = datetime.strptime(datetime_obj, fmt)
                        return parsed_dt.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        continue
        except Exception:
            pass
        
        return str(datetime_obj)
    
    register_blueprints(app)
    return app
