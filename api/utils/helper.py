"""
    Helper module
"""

def check_mandatory(keys, data):
    missing_keys = [key for key in keys if key not in data]
    if missing_keys:
        return True, missing_keys
    return False, []