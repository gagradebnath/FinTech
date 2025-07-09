import bcrypt

def hash_password(password):
    """
    Hash a password using bcrypt.
    
    Args:
        password (str): Plain text password to hash
        
    Returns:
        str: Hashed password
    """
    if not password:
        return None
    
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string for database storage
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """
    Verify a password against its hash.
    
    Args:
        password (str): Plain text password to verify
        hashed_password (str): Stored hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    if not password or not hashed_password:
        return False
    
    try:
        # Convert to bytes
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Verify password
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        # If there's any error (e.g., invalid hash format), return False
        return False

def is_password_hashed(password):
    """
    Check if a password is already hashed (starts with bcrypt prefix).
    
    Args:
        password (str): Password to check
        
    Returns:
        bool: True if password appears to be hashed, False otherwise
    """
    if not password:
        return False
    
    # bcrypt hashes start with $2a$, $2b$, $2x$, or $2y$
    return password.startswith(('$2a$', '$2b$', '$2x$', '$2y$'))