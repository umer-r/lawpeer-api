# Lib Imports:
from functools import wraps
from flask import jsonify, request

# Module Imports:
from api.utils.status_codes import Status

# ----------------------------------------------- #

def check_mandatory(keys):
    """
    A decorator function to check for missing mandatory keys in the request data.

    Args:
        keys (list): A list of strings representing the mandatory keys.

    Returns:
        function: A decorator function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            missing_keys = [key for key in keys if key not in data]
            if missing_keys:
                return jsonify(error=f'Missing mandatory key(s): {", ".join(missing_keys)}'), Status.HTTP_422_UNPROCESSABLE_ENTITY
            return func(*args, **kwargs)
        return wrapper
    return decorator
