# Lib Imports:
from flask_jwt_extended import create_access_token

# Module Imports:
from api.models.admin import Admin
from api.models.user import User
from api.utils.hasher import verify_password

def generate_admin_access_token(email, password):
    """
    Generate Access token For Admin with id & role based on email and password.

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
    
def generate_user_access_token(email, password):
    """ 
    Generate Access token for User (Client | lawyer) with id & role 
    
    Args:
        email (str): Email address of user.
        password (str): Password of user.

    Returns:
        tuple: A tuple containing a boolean indicating whether authentication was successful
               and the generated access token.
    """
    
    # Authenticate user based on email and password
    user = User.query.filter_by(email=email).first()

    if user and verify_password(password, user.password):
        # Generate JWT token for the authenticated user
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        return True, access_token
    else:
        return False, ""
