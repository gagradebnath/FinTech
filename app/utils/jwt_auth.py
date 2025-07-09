import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify, session
from app.utils.user_utils import get_current_user

def generate_jwt_token(user_id, role_id=None):
    """Generate JWT token for user authentication."""
    try:
        payload = {
            'user_id': user_id,
            'role_id': role_id,
            'exp': datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
            'iat': datetime.utcnow(),  # Issued at
        }
        
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return token
    except Exception as e:
        print(f"Error generating JWT token: {e}")
        return None

def verify_jwt_token(token):
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}
    except Exception as e:
        print(f"Error verifying JWT token: {e}")
        return {'error': 'Token verification failed'}

def get_token_from_request():
    """Extract JWT token from request headers or query params."""
    # Check Authorization header first (Bearer token)
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    
    # Check query parameters as fallback
    token = request.args.get('token')
    if token:
        return token
    
    # Check form data for API endpoints
    if request.is_json:
        data = request.get_json(silent=True)
        if data and 'token' in data:
            return data['token']
    
    return None

def token_required(f):
    """Decorator to require valid JWT token for route access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check if user is authenticated via session (backward compatibility)
        if session.get('user_id'):
            return f(*args, **kwargs)
        
        # Then check for JWT token
        token = get_token_from_request()
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = verify_jwt_token(token)
        if 'error' in payload:
            return jsonify({'error': payload['error']}), 401
        
        # Store user info in request context for use in route
        request.jwt_user_id = payload['user_id']
        request.jwt_role_id = payload.get('role_id')
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user_from_jwt():
    """Get current user from JWT token or session (backward compatibility)."""
    # First try to get from session (existing behavior)
    if session.get('user_id'):
        return get_current_user()
    
    # Then try to get from JWT token
    token = get_token_from_request()
    if not token:
        return None
    
    payload = verify_jwt_token(token)
    if 'error' in payload:
        return None
    
    # Get user from database using JWT payload
    from flask import current_app
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (payload['user_id'],))
            user = cursor.fetchone()
        return user
    finally:
        conn.close()