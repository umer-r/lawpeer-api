from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from api.utils.status_codes import Status

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
        # Authorization logic to check if user is an admin
        admin = get_jwt_identity()
        if admin['role'] not in ['admin', 'super-admin']:
            return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
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
        # Authorization logic to check if user is a super admin
        admin = get_jwt_identity()
        if admin['role'] != 'super-admin':
            return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
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
        # Authorization logic to check if user is the super admin or the current admin
        admin = get_jwt_identity()
        id = kwargs.get('id')  # Assuming the ID is passed as a keyword argument
        if admin['role'] != 'super-admin' and str(id) != str(admin['id']):
            return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
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
        # Authorization logic to check if user is the same as the requested admin
        admin = get_jwt_identity()
        id = kwargs.get('id')  # Assuming the ID is passed as a keyword argument
        if str(id) != str(admin['id']):
            return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
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
        # Authorization logic to check if user is either the original user or an admin
        user = get_jwt_identity()
        id = kwargs.get('id')  # Assuming the ID is passed as a keyword argument
        if str(id) != str(user['id']) and user['role'] not in ['admin', 'super-admin']:
            print(id)
            return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
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
        # Authorization logic to check if user is the same as the requested user
        user = get_jwt_identity()
        id = kwargs.get('id')  # Assuming the ID is passed as a keyword argument
        if str(id) != str(user['id']):
            return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
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
        # Authorization logic to check if user is a super admin
        client = get_jwt_identity()
        if client['role'] != 'client':
            return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
        return func(*args, **kwargs)
    return decorated_function

def lawyer_required(func):
    """
    -- AC: Only Lawyer Can Access --
    
    Decorator to enforce that the user accessing the endpoint is a client.

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
            return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
        return func(*args, **kwargs)
    return decorated_function
