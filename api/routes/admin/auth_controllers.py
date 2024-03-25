from flask_jwt_extended import create_access_token

from api.models.admin import Admin
from api.utils.hasher import verify_password

def generate_access_token(email, password):
    """ Generate Access token with id & role """
    
    # Authenticate admin based on email and password
    admin = Admin.query.filter_by(email=email).first()

    if admin and verify_password(password, admin.password):
        # Generate JWT token for the authenticated user
        access_token = create_access_token(identity={'id': admin.id, 'role': admin.role})
        return True, access_token
    else:
        return False, ""

def check_current_admin(admin, id):
    """ Checks if admin is the (same as) requested admin """
    
    if str(id) != str(admin['id']):
        return False
    return True

def check_admin(admin):
    """ Checks if user is admin """
    
    if admin['role'] != 'admin':
        return False
    return True
