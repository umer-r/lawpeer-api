"""
    Util file; Contains helper functions utilized accross api.

    External Libraries:
        - flask: A micro web framework for Python.
        - datetime: A module in Python that supplies classes for manipulating dates and times.
        - os: A module in Python that provides functions for interacting with the operating system.
        - sqlalchemy: A SQL toolkit and Object-Relational Mapping (ORM) for Python.

    Function Names:
        - allowed_file
        - allowed_documents
        - get_upload_folder
        - omit_user_sensitive_fields
        - rename_profile_image
        - rename_document
        - to_dict
"""

# Lib Imports:
from flask import current_app
from datetime import datetime
import os
from sqlalchemy import inspect

# ----------------------------------------------- #

## --- CONTS --- ##

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_DOCS = {'png', 'jpg', 'jpeg', 'pdf', 'docx', 'doc', 'xls', 'xlsx', 'zip'}

## --- METHODS --- ##

def allowed_file(filename):
    """
    Checks if the file extension is allowed for upload.

    Parameters:
        - filename (str): The name of the file to be checked.

    Returns:
        - bool: True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_documents(filename):
    """
    Checks if the document extension is allowed for upload.

    Parameters:
        - filename (str): The name of the document file to be checked.

    Returns:
        - bool: True if the document extension is allowed, False otherwise.
    """
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOCS

def get_upload_folder():
    """
    Get the upload folder path.

    Returns:
        - str: The path to the upload folder.
    """
    
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
    current_time = datetime.now().strftime("Lawpeer_Profile_%Y%m%d%H%M%S")
    new_filename = f"{current_time}{extension}"
    return new_filename

def rename_document(file):
    """
    Rename a document file with a timestamp prefix.

    Parameters:
        - file (FileStorage): The file to be renamed.

    Returns:
        - str: The new filename with a timestamp prefix.
    """
    
    filename, extension = os.path.splitext(file.filename)
    current_time = datetime.now().strftime("Lawpeer_Uploaded_Doc_%Y%m%d%H%M%S")
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
