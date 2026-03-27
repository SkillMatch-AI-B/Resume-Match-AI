import hashlib
import database.db_queries as db

def hash_password(password):
    """
    Encrypts the password using SHA-256 hashing.
    (Note: For a fully production-ready app, you would upgrade this to bcrypt, 
    but SHA-256 is perfect for our current scope without needing extra pip installs.)
    """
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password, role):
    """
    Hashes the password and attempts to save the new user to the database.
    Returns True if successful, False if the email is already registered.
    """
    hashed_password = hash_password(password)
    return db.create_user(email, hashed_password, role)

def authenticate_user(email, password):
    """
    Checks if the email exists and if the hashed password matches.
    Returns the user data dictionary if successful, or None if it fails.
    """
    user = db.get_user_by_email(email)
    
    if user:
        # Check if the provided password (once hashed) matches the database hash
        if user['password'] == hash_password(password):
            return user  # Login successful! Returns {'id': 1, 'email': '...', 'role': '...'}
            
    return None  # Login failed (wrong email or wrong password)