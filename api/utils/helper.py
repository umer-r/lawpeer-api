"""
    Helper module
"""

# Lib Imports
from flask import current_app
import os

# ----------------------------------------------- #

# CONSTS:
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# METHODS:
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_mandatory(keys, data):
    missing_keys = [key for key in keys if key not in data]
    if missing_keys:
        return True, missing_keys
    return False, []

def get_upload_folder():
    with current_app.app_context():
        return os.path.join(current_app.root_path, 'assets/uploaded')
