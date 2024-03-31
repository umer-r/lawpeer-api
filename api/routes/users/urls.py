"""
    TODO:   1  - Add missing keys error in routes.                                       - [DONE]
            2  - Add account deactivation/activation route.                              - [DONE]
            3  - Add account suspension & STATUS route.                                  -
            4  - Omit the sensitive fields from returning the users.                     - [DONE]
            5  - Change Status 400 to 422 UNPROCESSABLE_ENTITY.                          - [DONE]
            6  - Implement Profile picture send back functionality in get user by ID.    - [DONE]
            7  - Implement Refresh Token Logic.                                          - [HALT] -> Moved to (9).
            8  - Implement Email verification for users.                                 - 
            9  - Change the Access Token's Settings (Time -> 7 days, Secret key).        - [DONE]
            10 - Change JWT access to get_user_by_id().                                  - [DONE]
            11 - Add access control - omit fields if not user or admin in (10).          - [DONE]
            12 - Rename updated Image by users perspective (overwrite-protection).       - [DONE]
            13 - Add user password change route.                                         - [DONE]
            14 - Change update existing user controller to handle all user updation.     - []
            15 - FIX: Cascade in lawyers & clients table upon user deletion              - 
"""

# Lib Imports
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

# Module Imports
from api.routes.users.controllers import create_user, get_all_users, update_user, delete_user, get_user_by_id, get_all_lawyers, get_all_clients, self_activate_user_account, self_deactivate_user_account, change_password
from api.routes.users.auth_controllers import generate_access_token, check_admin, check_user_or_admin
from api.utils.status_codes import Status
from api.utils.helper import check_mandatory, omit_sensitive_fields

# ----------------------------------------------- #

user_routes = Blueprint('users', __name__)

# -- Lawyer Specific -- #

@user_routes.route('/lawyer', methods=['POST'])
def create_new_lawyer():
    data = request.form

    
    is_missing, missing_keys = check_mandatory(['email', 'username', 'password', 'first_name', 'last_name'], data)
    if is_missing:
        return jsonify(error=f'Missing mandatory key(s): {", ".join(missing_keys)}'), Status.HTTP_422_UNPROCESSABLE_ENTITY
    
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    dob = data.get('dob')
    country = data.get('country')
    phone_number = data.get('phone_number')
    bar_association_id = data.get('bar_association_id')
    experience_years = data.get('experience_years')
    profile_image = request.files.get('profile_pic')

    new_lawyer = create_user(email, username, password, first_name, last_name, dob, country, phone_number, profile_image, role='lawyer', bar_association_id=bar_association_id, experience_years=experience_years)
    if new_lawyer is None:
        return jsonify({'message': 'User with the same email or username already exists'}), Status.HTTP_409_CONFLICT
    
    returned_lawyer = omit_sensitive_fields(new_lawyer)
    return jsonify(returned_lawyer), Status.HTTP_200_OK

# JWT Not required - can be accessed outside authorization
@user_routes.route('/lawyer', methods=['GET'])
def all_lawyers():
    
    lawyers = get_all_lawyers()
    if lawyers:
        return jsonify([lawyer.toDict() for lawyer in lawyers]), Status.HTTP_200_OK
    return jsonify({'message': 'No lawyer user found'}), Status.HTTP_404_NOT_FOUND

# -- Client Specific -- #

@user_routes.route('/client', methods=['POST'])
def create_new_client():
    data = request.form
    
    is_missing, missing_keys = check_mandatory(['email', 'username', 'password', 'first_name', 'last_name'], data)
    if is_missing:
        return jsonify(error=f'Missing mandatory key(s): {", ".join(missing_keys)}'), Status.HTTP_422_UNPROCESSABLE_ENTITY
    
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    dob = data.get('dob')
    country = data.get('country')
    phone_number = data.get('phone_number')
    case_details = data.get('case_details')
    profile_image = request.files.get('profile_pic')

    new_client = create_user(email, username, password, first_name, last_name, dob, country, phone_number, profile_image, role='client', case_details=case_details)
    if new_client is None:
        return jsonify({'message': 'User with the same email or username already exists'}), Status.HTTP_409_CONFLICT
    
    # Remove sensitive fields
    returned_client = omit_sensitive_fields(new_client)
    return jsonify(returned_client), Status.HTTP_200_OK

@user_routes.route('/client', methods=['GET'])
@jwt_required()
def all_clients():
    
    is_admin = check_admin(get_jwt_identity())
    if not is_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    clients = get_all_clients()
    if clients:
        return jsonify([client.toDict() for client in clients]), Status.HTTP_200_OK
    return jsonify({'message': 'No client user found'}), Status.HTTP_404_NOT_FOUND

# -- General User Routes -- #

@user_routes.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        
        is_user_or_admin = check_user_or_admin(user=get_jwt_identity(), id=user_id)
        if not is_user_or_admin:
            returned_user = omit_sensitive_fields(user)
            return jsonify(returned_user), Status.HTTP_200_OK
        
        return jsonify(user.toDict()), Status.HTTP_200_OK
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/', methods=['GET'])
@jwt_required()
def get_all():
    is_admin = check_admin(get_jwt_identity())
    if not is_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    users = get_all_users()
    if users:
        return jsonify([user.toDict() for user in users]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No user found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/<user_id>', methods=['PUT'])
@jwt_required()
def update_existing_user(user_id):
    # Get the identity (user ID and role) from the JWT token
    is_user_or_admin = check_user_or_admin(user=get_jwt_identity(), id=user_id)
    if not is_user_or_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    data = request.get_json()
    
    updated_user = update_user(user_id, **data)
    if updated_user:
        return jsonify(updated_user.toDict()), Status.HTTP_200_OK
    
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_existing_user(user_id):
    
    is_user_or_admin = check_user_or_admin(user=get_jwt_identity(), id=user_id)
    if not is_user_or_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    deleted_user = delete_user(user_id)
    if deleted_user:
        return jsonify({'message': f'User with id {user_id} deleted successfully!'}), Status.HTTP_204_NO_CONTENT
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/deactivate/<user_id>', methods=['POST'])
@jwt_required()
def deactivate_account(user_id):
    
    current_user = get_jwt_identity()
    
    data = request.get_json()

    is_missing, missing_keys = check_mandatory(['reason'], data)
    if is_missing:
        return jsonify(error=f'Missing mandatory key(s): {", ".join(missing_keys)}'), Status.HTTP_422_UNPROCESSABLE_ENTITY
    
    reason = data.get('reason')
    
    # Admin can also de-activate user account.
    is_user_or_admin = check_user_or_admin(user=current_user, id=user_id)
    if not is_user_or_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED  
    
    deactivated_user = self_deactivate_user_account(user_id=user_id, reason=reason)
    
    if deactivated_user is not None:
        return jsonify({'message': f'User with id {user_id} deactivated successfully!'}), Status.HTTP_200_OK
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND
    
@user_routes.route('/activate/<user_id>', methods=['GET'])
@jwt_required()
def activate_account(user_id):
    
    current_user = get_jwt_identity()
    
    # Admin can also activate user account.
    is_user_or_admin = check_user_or_admin(user=current_user, id=user_id)
    if not is_user_or_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    activated_user = self_activate_user_account(user_id=user_id)
    
    # Test the following logic:
    if activated_user is not None:
        return jsonify({'message': f'User with id {user_id} activated successfully!'}), Status.HTTP_200_OK
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/change_password/<user_id>', methods=['POST'])
@jwt_required()
def change_user_password(user_id):
    
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # Mandatory fields check:
    is_missing, missing_keys = check_mandatory(['prev_pass', 'new_pass'], data)
    if is_missing:
        return jsonify(error=f'Missing mandatory key(s): {", ".join(missing_keys)}'), Status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Access control check:
    is_user_or_admin = check_user_or_admin(user=current_user, id=user_id)
    if not is_user_or_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    prev_pass = data.get('prev_pass')
    new_pass = data.get('new_pass')
    
    changed_user_password = change_password(user_id=user_id, prev_password=prev_pass, new_password=new_pass)
    
    if not changed_user_password:
        return jsonify({'message': 'New password and previous password do not match!'}), Status.HTTP_400_BAD_REQUEST
    
    if changed_user_password is not None:
        return jsonify({'message': f'Password change operation for User with id {user_id} successful!'}), Status.HTTP_200_OK
    
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

# -- Auth Routes -- #

# User Login Endpoint
@user_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    is_missing, missing_keys = check_mandatory(['email', 'password'], data)
    if is_missing:
        return jsonify(error=f'Missing mandatory key(s): {", ".join(missing_keys)}'), Status.HTTP_422_UNPROCESSABLE_ENTITY
    
    email = data.get('email')
    password = data.get('password')

    is_authorized, token = generate_access_token(email=email, password=password)
    if is_authorized:
        return jsonify(access_token=token), Status.HTTP_200_OK
    
    return jsonify({'message': 'Invalid credentials'}), Status.HTTP_401_UNAUTHORIZED
