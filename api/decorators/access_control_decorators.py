"""
    This file contains decorators for access control.
    
    External Libraries:
        - functools: Provides tools for working with functions and other callable objects.
        - flask: A micro web framework for Python.
        - flask_jwt_extended: An extension for Flask that adds JWT support.

    Function Names:
        - admin_required
        - super_admin_required
        - super_or_current_admin_required
        - current_admin_required
        - user_or_admin_required
        - user_required
        - client_required
        - lawyer_required

    TODO:   
        1 - re-write the return message to show more details about unauthorization      - [DONE]
"""

# Lib Imports:
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity

# Modules Imports:
from api.utils.status_codes import Status

# ----------------------------------------------- #

## -- Admin Access control -- ##

def admin_required(func):
    """
    -- AC: Only Admin Can Access --
    
    Decorator to enforce that the user accessing the endpoint is an admin.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.
    """
    
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Get identity from JWT as dict:
        admin = get_jwt_identity()
        # Preform authorization check:
        if admin['role'] not in ['admin', 'super-admin']:
            return jsonify({'error': 'Unauthorized access. User is not admin.'}), Status.HTTP_401_UNAUTHORIZED
        return func(*args, **kwargs)
    return decorated_function

def super_admin_required(func):
    """
    -- AC: Only Super Admin Can Access --
    
    Decorator to enforce that the user accessing the endpoint is a super admin.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.
    """
    
    @wraps(func)
    def decorated_function(*args, **kwargs):
        admin = get_jwt_identity()
        if admin['role'] != 'super-admin':
            return jsonify({'error': 'Unauthorized access. User is not super admin.'}), Status.HTTP_401_UNAUTHORIZED
        return func(*args, **kwargs)
    return decorated_function

def super_or_current_admin_required(func):
    """
    -- AC: Super Admin Or Current Admin can access (no other admin can access) --
    
    Decorator to enforce that the user accessing the endpoint is either the super admin or the current admin.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.
    """
    
    @wraps(func)
    def decorated_function(*args, **kwargs):
        admin = get_jwt_identity()
        id = kwargs.get('id')           # ID passed from request.params
        if admin['role'] != 'super-admin' and str(id) != str(admin['id']):
            return jsonify({'error': 'Unauthorized access. Admin is not current or super admin.'}), Status.HTTP_401_UNAUTHORIZED
        return func(*args, **kwargs)
    return decorated_function

def current_admin_required(func):
    """
    -- AC: Only Admin who requested Can Access --
    
    Decorator to enforce that the user accessing the endpoint is the same as the requested admin.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.
    """
    
    @wraps(func)
    def decorated_function(*args, **kwargs):
        admin = get_jwt_identity()
        id = kwargs.get('id')
        if str(id) != str(admin['id']):
            return jsonify({'error': 'Unauthorized access. Admin is not same as the requested admin.'}), Status.HTTP_401_UNAUTHORIZED
        return func(*args, **kwargs)
    return decorated_function

## -- User Access control -- ##

def user_or_admin_required(func):
    """
    -- AC: Only Current User who requested or Admin Can Access --
    
    Decorator to enforce that the user accessing the endpoint is either the requested user or an admin.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.
    """
    
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user = get_jwt_identity()
        id = kwargs.get('id')
        if str(id) != str(user['id']) and user['role'] not in ['admin', 'super-admin']:
            print(id)
            return jsonify({'error': 'Unauthorized access. User is not current user or admin.'}), Status.HTTP_401_UNAUTHORIZED
        return func(*args, **kwargs)
    return decorated_function

def user_required(func):
    """
    -- AC: Only Current User Can Access --
    
    Decorator to enforce that the user accessing the endpoint is the same as the requested user.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.
    """
    
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user = get_jwt_identity()
        id = kwargs.get('id')
        if str(id) != str(user['id']):
            return jsonify({'error': 'Unauthorized access. User is not same as the requested user.'}), Status.HTTP_401_UNAUTHORIZED
        return func(*args, **kwargs)
    return decorated_function

def client_required(func):
    """
    -- AC: Only Client Can Access --
    
    Decorator to enforce that the user accessing the endpoint is a client.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.
    """
    
    @wraps(func)
    def decorated_function(*args, **kwargs):
        client = get_jwt_identity()
        if client['role'] != 'client':
            return jsonify({'error': 'Unauthorized access. User is not a Client.'}), Status.HTTP_401_UNAUTHORIZED
        return func(*args, **kwargs)
    return decorated_function

def lawyer_required(func):
    """
    -- AC: Only Lawyer Can Access --
    
    Decorator to enforce that the user accessing the endpoint is a lawyer.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.
    """
    
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Authorization logic to check if user is a super admin
        lawyer = get_jwt_identity()
        if lawyer['role'] != 'lawyer':
            return jsonify({'error': 'Unauthorized access. User is not a Lawyer.'}), Status.HTTP_401_UNAUTHORIZED
        return func(*args, **kwargs)
    return decorated_function
