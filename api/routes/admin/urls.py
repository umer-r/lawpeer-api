"""
    DESC:
        Blueprint for Admin related routes.
        
    TODO:   1 - Add JWT logic secure on all routes (Only admins can access these routes).   - [DONE]
            2 - Add DOC strings on each func.                                               -
            3 - Implement Super admin logic.                                                - [DONE]
            4 - Test each of the following routes.                                          - [DONE]
            5 - Omit sensitive fields.                                                      - []
"""

# Lib Imports
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

# Module Imports
from api.routes.admin.controllers import create_admin, update_admin, delete_admin, get_admin_by_id, get_all_admin
from api.routes.admin.auth_controllers import generate_access_token, check_admin, check_current_admin, check_super_and_current_admin, check_super_admin
from api.utils.status_codes import Status
from api.utils.helper import check_mandatory

# ----------------------------------------------- #

admin_routes = Blueprint('admin', __name__)

@admin_routes.route('/', methods=['POST'])
@jwt_required()
def create_new_admin():
    
    # Only (super) Admin can access:
    is_super_admin = check_super_admin(get_jwt_identity())
    if not is_super_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    data = request.get_json()
    
    is_missing, missing_keys = check_mandatory(['email', 'password'], data)
    if is_missing:
        return jsonify(error=f'Missing mandatory key(s): {", ".join(missing_keys)}'), Status.HTTP_422_UNPROCESSABLE_ENTITY
    
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')
    
    new_admin = create_admin(email, password, phone_number, role='admin')
    if new_admin is None:
        return jsonify({'message': 'Admin with the same email already exists'}), Status.HTTP_409_CONFLICT
    
    return jsonify(new_admin.toDict()), Status.HTTP_200_OK

@admin_routes.route('/', methods=['GET'])
@jwt_required()
def all_admins():
    
    # Only (all) Admins can access
    is_admin = check_admin(get_jwt_identity())
    if not is_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    admins = get_all_admin()
    if admins:
        return jsonify([admin.toDict() for admin in admins]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No admin found'}), Status.HTTP_404_NOT_FOUND

@admin_routes.route('/<id>', methods=['GET'])
@jwt_required()
def get_admin(id):
    
    # Only (all) Admins can access
    is_admin = check_admin(get_jwt_identity())
    if not is_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    admin = get_admin_by_id(id)
    if admin:
        return jsonify(admin.toDict()), Status.HTTP_200_OK
    
    return jsonify({'message': 'Admin not found'}), Status.HTTP_404_NOT_FOUND

@admin_routes.route('/<id>', methods=['PUT'])
@jwt_required()
def update_existing_admin(id):
    
    # Admin Should be the same as the requested admin.
    is_requested_admin_or_super = check_super_and_current_admin(admin=get_jwt_identity(), id=id)
    if not is_requested_admin_or_super:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    data = request.get_json()
    updated_admin = update_admin(id, **data)
    if updated_admin:
        return jsonify(updated_admin.toDict()), Status.HTTP_200_OK
    
    return jsonify({'message': 'Admin not found'}), Status.HTTP_404_NOT_FOUND

@admin_routes.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete_existing_admin(id):
    
    # Admin Should be the same as the requested admin.
    is_requested_admin_or_super = check_super_and_current_admin(admin=get_jwt_identity(), id=id)
    if not is_requested_admin_or_super:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    deleted_admin = delete_admin(id)
    if deleted_admin:
        return jsonify({'message': f'Admin with id {id} deleted successfully!'}), Status.HTTP_204_NO_CONTENT
    
    return jsonify({'message': 'Admin not found'}), Status.HTTP_404_NOT_FOUND

# -- Auth Routes -- #

# Admin Login Endpoint
@admin_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Check mandatory fields/keys
    is_missing, missing_keys = check_mandatory(['email', 'password'], data)
    if is_missing:
        return jsonify(error=f'Missing mandatory key(s): {", ".join(missing_keys)}'), Status.HTTP_422_UNPROCESSABLE_ENTITY
    
    email = data.get('email')
    password = data.get('password')

    # Check if Admin is authorized (credentials correct) & generate the access token.
    is_authorized, token = generate_access_token(email=email, password=password)
    if is_authorized:
        return jsonify(access_token=token), Status.HTTP_200_OK
    
    return jsonify({'message': 'Invalid credentials'}), Status.HTTP_401_UNAUTHORIZED
