# Lib Imports
from flask_jwt_extended import create_access_token

# Module Imports
from api.models.user import User
from api.utils.hasher import verify_password

# ----------------------------------------------- #

def generate_access_token(email, password):
    """ Generate Access token with id & role """
    
    # Authenticate user based on email and password
    user = User.query.filter_by(email=email).first()

    if user and verify_password(password, user.password):
        # Generate JWT token for the authenticated user
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        return True, access_token
    else:
        return False, ""

def check_user_or_admin(user, id):
    """ Checks if the current user is the requested user OR if user is an admin """
    
    # Check if the user is either the original user or an admin
    if str(id) != str(user['id']) and user['role'] != 'admin':
        return False
    return True

def check_user(user, id):
    """ Checks if user is the (same as) requested user """
    
    if str(id) != str(user['id']):
        return False
    return True

def check_admin(user):
    """ Checks if user is admin """
    
    if user['role'] != 'admin':
        return False
    return True
