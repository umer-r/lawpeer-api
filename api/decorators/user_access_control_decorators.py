from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from api.utils.status_codes import Status

def admin_required(func):
    """
    Decorator to enforce that the user accessing the endpoint is an admin.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.
    """
    
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Authorization logic to check if user is an admin
        user = get_jwt_identity()
        if user['role'] != 'admin':
            return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
        return func(*args, **kwargs)
    return decorated_function
