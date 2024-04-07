"""
    DESC: 
        Module for Authorization checking controllers for Admins

    Module Imports:
        - Admin: Model representing the administrator entity
        - verify_password: Function for verifying passwords
        - create_access_token: Function for creating JWT access tokens

    Library Imports:
        - Flask-JWT-Extended: Used for JWT token generation

    Functions:
        - generate_access_token()        
        - check_super_admin()
        - check_super_and_current_admin()        
        - check_current_admin()
        - check_admin()
"""

# Lib Imports:
from flask_jwt_extended import create_access_token

# Module Imports:
from api.models.admin import Admin
from api.utils.hasher import verify_password

# ----------------------------------------------- #

def generate_access_token(email, password):
    """
    Generate Access token with id & role based on email and password.

    Args:
        email (str): Email address of the admin.
        password (str): Password of the admin.

    Returns:
        tuple: A tuple containing a boolean indicating whether authentication was successful
               and the generated access token.
    """
    
    # Authenticate admin based on email and password
    admin = Admin.query.filter_by(email=email).first()

    if admin and verify_password(password, admin.password):
        # Generate JWT token for the authenticated user
        access_token = create_access_token(identity={'id': admin.id, 'role': admin.role})
        return True, access_token
    else:
        return False, ""

def check_super_admin(admin):
    """
    Checks if the user is the super admin.

    Args:
        admin (dict): Dictionary containing admin information.

    Returns:
        bool: True if the user is the super admin, False otherwise.
    """
    
    if admin['role'] != 'super-admin':
        return False
    return True

def check_super_and_current_admin(admin, id):
    """
    Checks if the user is the super admin or the current admin.

    Args:
        admin (dict): Dictionary containing admin information.
        id (int): ID of the admin.

    Returns:
        bool: True if the user is the super admin or the current admin, False otherwise.
    """
    
    if admin['role'] != 'super-admin' and str(id) != str(admin['id']):
        return False
    return True

def check_current_admin(admin, id):
    """
    Checks if the admin is the same as the requested admin.

    Args:
        admin (dict): Dictionary containing admin information.
        id (int): ID of the admin.

    Returns:
        bool: True if the admin is the same as the requested admin, False otherwise.
    """
    
    if str(id) != str(admin['id']):
        return False
    return True

def check_admin(admin):
    """
    Checks if the user is an admin (any).

    Args:
        admin (dict): Dictionary containing admin information.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    
    if admin['role'] not in ['admin', 'super-admin']:
        return False
    return True
