"""
    TODO:   1 - Add a Suspended account & Reason controller.                                -
            2 - If admin is de activating an account change the 'status' field in model.    - [HALT]
            3 - Modify create_user to store profile images as paths.                        - [DONE]
            4 - Add a check if ATTRIBUTE/FIELD is already changed (e.g. user already deactivated), send appropriate status code back.
            5 - In create_user(), Split in two by Email & Username.                         - 
"""

# Lib Imports:
from werkzeug.utils import secure_filename
import os

# Module Imports:
from api.database import db
from api.models.user import User, Lawyer, Client
from api.utils.hasher import hash_password
from api.utils.helper import allowed_file, get_upload_folder, rename_profile_image

# ----------------------------------------------- #

# -- General User Controller -- #

def create_user(email, username, password, first_name, last_name, dob, country, phone_number, profile_image=None, role=None, **kwargs):
    
    # Check for duplicate email or username.
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        # If user with same email or username already exists, return 409 Conflict
        return None

    hashed_password = hash_password(password=password)
    
    if role == 'lawyer':
        new_user = Lawyer(email=email, username=username, password=hashed_password, first_name=first_name, last_name=last_name, dob=dob, country=country, phone_number=phone_number, **kwargs)
    elif role == 'client':
        new_user = Client(email=email, username=username, password=hashed_password, first_name=first_name, last_name=last_name, dob=dob, country=country, phone_number=phone_number, **kwargs)
    else:
        new_user = User(email=email, username=username, password=hashed_password, first_name=first_name, last_name=last_name, dob=dob, country=country, phone_number=phone_number, **kwargs)
    
    UPLOAD_FOLDER = get_upload_folder()
    if profile_image:
        filename = secure_filename(rename_profile_image(profile_image))
        if allowed_file(filename):
            profile_image_path = os.path.join(UPLOAD_FOLDER, filename)
            profile_image.save(profile_image_path)
            
            # Refactor if gives a bug:
            new_user.profile_image = os.path.join('/static', filename).replace('\\', '/')
    
    db.session.add(new_user)
    db.session.commit()
    
    return new_user

def get_user_by_id(user_id):
    """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User: The user object if found, otherwise None.
    """
    
    user = User.query.get(user_id)
    return user if user else None

def get_all_users():
    return User.query.all()

def update_user(user_id, email=None, username=None, dob=None, country=None, phone_number=None, **kwargs):
    user = User.query.get(user_id)
    if user:
        if email:
            user.email = email
        if username:
            user.username = username
        if dob:
            user.dob = dob
        if country:
            user.country = country
        if phone_number:
            user.phone_number = phone_number
            
        # If the user has a role-specific attributes, update them
        for key, value in kwargs.items():
            setattr(user, key, value)
        db.session.commit()
        return user
    return None

def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return user
    return None

def self_deactivate_user_account(user_id, reason=None):
    user = User.query.get(user_id)
    if user:
        user.is_active = False
        user.reason = reason
        db.session.commit()
        return user
    return None
    
def self_activate_user_account(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_active = True
        db.session.commit()
        return user
    return None
    
# -- Lawyers Specific -- #

def get_all_lawyers():
    return User.query.filter_by(role='lawyer').all()

# -- Clients Specific -- #

def get_all_clients():
    return User.query.filter_by(role='client').all()
