"""
    Util file; for hashing and verification of passwords.

    External Libraries:
        - bcrypt: A password-hashing library for Python, which uses the OpenBSD Blowfish hashing algorithm.

    Function Names:
        - hash_password
        - verify_password
"""

# Lib Imports:
import bcrypt

# ----------------------------------------------- #

def hash_password(password):
    """
    Hashes the provided password using bcrypt.

    Parameters:
        - password (str): The password to be hashed.

    Returns:
        - hashed_password (str): The hashed password.
    """
    
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(password, hashed_password):
    """
    Verifies the provided password against the hashed password using bcrypt.
    Returns True if the passwords match, False otherwise.
    
    Parameters:
        - password (str): The password to be verified.
        - hashed_password (str): The hashed password to be compared with.

    Returns:
        - bool: True if the passwords match, False otherwise.
    """
    
    # Check if the provided password matches the hashed password
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
