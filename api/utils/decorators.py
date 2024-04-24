from functools import wraps
from flask import jsonify, request

def check_mandatory(keys):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            missing_keys = [key for key in keys if key not in data]
            if missing_keys:
                return jsonify(error=f'Missing mandatory key(s): {", ".join(missing_keys)}'), 422
            return func(*args, **kwargs)
        return wrapper
    return decorator
