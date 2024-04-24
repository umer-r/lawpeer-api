"""
    DESC:
        Blueprint for Admin related routes.
        
    TODO:   1 - Add JWT logic secure on all routes (Only admins can access these routes).   - [DONE]
            2 - Add DOC strings on each func.                                               - []
            3 - Implement Super admin logic.                                                - [DONE]
            4 - Test each of the following routes.                                          - [DONE]
            5 - Omit sensitive fields.                                                      - []
"""

# Lib Imports
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

# Module Imports
from api.routes.admin.controllers import create_admin, update_admin, delete_admin, get_admin_by_id, get_all_admin
from api.routes.admin.auth_controllers import generate_access_token, check_admin, check_current_admin, check_super_and_current_admin, check_super_admin
from api.utils.status_codes import Status
from api.utils.decorators import check_mandatory

# ----------------------------------------------- #

admin_routes = Blueprint('admin', __name__)

@admin_routes.route('/', methods=['POST'])
@jwt_required()
@swag_from(methods=['POST'])
@check_mandatory(['email', 'password'])
def create_new_admin():
    """
    Endpoint to create a new admin.

    ---
    tags:
      - Admin
    description: Create a new admin with the provided information.
    security:
      - JWT: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                description: Email address of the admin.
              password:
                type: string
                description: Password of the admin.
              phone_number:
                type: string
                description: Phone number of the admin.
    responses:
      200:
        description: Successful operation. Returns the created admin.
      409:
        description: Conflict. Admin with the same email already exists.
    """
    
    # Only (super) Admin can access:
    is_super_admin = check_super_admin(get_jwt_identity())
    if not is_super_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')
    
    new_admin = create_admin(email, password, phone_number, role='admin')
    if new_admin is None:
        return jsonify({'message': 'Admin with the same email already exists'}), Status.HTTP_409_CONFLICT
    
    return jsonify(new_admin.toDict()), Status.HTTP_200_OK

@admin_routes.route('/', methods=['GET'])
@jwt_required()
@swag_from(methods=['GET'])
def all_admins():
    """
    Endpoint to retrieve all admins.

    ---
    tags:
      - Admin
    description: Retrieve a list of all admins.
    security:
      - JWT: []
    responses:
      200:
        description: Successful operation. Returns a list of admins.
      401:
        description: Unauthorized access.
      404:
        description: No admin found.
    """
    
    # Only (all) Admins can access
    is_admin = check_admin(get_jwt_identity())
    if not is_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    admins = get_all_admin()
    if admins:
        return jsonify([admin.toDict() for admin in admins]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No admin found'}), Status.HTTP_404_NOT_FOUND

@admin_routes.route('/<int:id>', methods=['GET'])
@jwt_required()
@swag_from(methods=['GET'])
def get_admin(id):
    """
    Endpoint to retrieve admin details by admin ID.

    ---
    tags:
      - Admin
    description: Retrieve admin details by admin ID.
    security:
      - JWT: []
    parameters:
      - name: id
        in: path
        type: string
        required: true
        description: ID of the admin to retrieve.
    responses:
      200:
        description: Successful operation. Returns admin details.
      401:
        description: Unauthorized access.
      404:
        description: Admin not found.
    """
    
    # Only (all) Admins can access
    is_admin = check_admin(get_jwt_identity())
    if not is_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    admin = get_admin_by_id(id)
    if admin:
        return jsonify(admin.toDict()), Status.HTTP_200_OK
    
    return jsonify({'message': 'Admin not found'}), Status.HTTP_404_NOT_FOUND

@admin_routes.route('/<int:id>', methods=['PUT'])
@jwt_required()
@swag_from(methods=['PUT'])
def update_existing_admin(id):
    """
    Endpoint to update an existing admin by admin ID.

    ---
    tags:
      - Admin
    description: Update an existing admin by admin ID.
    security:
      - JWT: []
    parameters:
      - name: id
        in: path
        type: string
        required: true
        description: ID of the admin to update.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              # Add properties here as needed.
    responses:
      200:
        description: Successful operation. Returns the updated admin details.
      401:
        description: Unauthorized access.
      404:
        description: Admin not found.
    """
    
    # Admin Should be the same as the requested admin.
    is_requested_admin_or_super = check_super_and_current_admin(admin=get_jwt_identity(), id=id)
    if not is_requested_admin_or_super:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    data = request.get_json()
    updated_admin = update_admin(id, **data)
    if updated_admin:
        return jsonify(updated_admin.toDict()), Status.HTTP_200_OK
    
    return jsonify({'message': 'Admin not found'}), Status.HTTP_404_NOT_FOUND

@admin_routes.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@swag_from(methods=['DELETE'])
def delete_existing_admin(id):
    """
    Endpoint to delete an existing admin by admin ID.

    ---
    tags:
      - Admin
    description: Delete an existing admin by admin ID.
    security:
      - JWT: []
    parameters:
      - name: id
        in: path
        type: string
        required: true
        description: ID of the admin to delete.
    responses:
      204:
        description: Successful operation. No content returned.
      401:
        description: Unauthorized access.
      404:
        description: Admin not found.
    """
    
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
@swag_from(methods=['POST'])
@check_mandatory(['email', 'password'])
def login():
    """
    Endpoint for admin login.

    ---
    tags:
      - Auth
    description: Authenticate admin and generate access token.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                description: Admin's email address.
              password:
                type: string
                description: Admin's password.
    responses:
      200:
        description: Successful operation. Returns access token.
      401:
        description: Invalid credentials.
      422:
        description: Missing mandatory key(s) in request.
    """
    
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')

    # Check if Admin is authorized (credentials correct) & generate the access token.
    is_authorized, token = generate_access_token(email=email, password=password)
    if is_authorized:
        return jsonify(access_token=token), Status.HTTP_200_OK
    
    return jsonify({'message': 'Invalid credentials'}), Status.HTTP_401_UNAUTHORIZED
