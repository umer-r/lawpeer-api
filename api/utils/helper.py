"""
    Helper module
"""

# Lib Imports
from flask import current_app
from datetime import datetime
import os
from sqlalchemy import inspect

# ----------------------------------------------- #

# CONSTS:
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# METHODS:
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_mandatory(keys, data):
    """
        OBSELETE: Moved to decorator
    """
    missing_keys = [key for key in keys if key not in data]
    if missing_keys:
        return True, missing_keys
    return False, []

def get_upload_folder():
    with current_app.app_context():
        return os.path.join(current_app.root_path, 'assets/uploaded')
    
def omit_user_sensitive_fields(user):
    """
        Omit sensitive fields from the user object.

        Args:
            user (User): The user object to process.

        Returns:
            dict: A dictionary containing the user data with sensitive fields omitted.
    """
    
    sensitive_fields = ['password']  # Add any additional sensitive fields here
    return {key: value for key, value in user.to_dict().items() if key not in sensitive_fields}

def rename_profile_image(profile_image):
    """
        Rename the profile image with the current date and time.

        Args:
            profile_image (FileStorage): The profile image file.

        Returns:
            str: The new filename with the current date and time.
    """
    
    filename, extension = os.path.splitext(profile_image.filename)
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename = f"{current_time}{extension}"
    return new_filename

def to_dict(instance):
    """
        Convert SQLAlchemy model instance to a dictionary representation.

        Args:
            instance: SQLAlchemy model instance to be converted.

        Returns:
            dict: Dictionary representation of the SQLAlchemy model instance.
            
        Reference:
            How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
    """
    return {c.key: getattr(instance, c.key) for c in inspect(instance).mapper.column_attrs}
