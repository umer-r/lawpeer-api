"""
    TODO:   1 - Add missing keys error in routes. - Done
            2 - Add account deactivation route.
            3 - Add account suspension & STATUS route.
            4 - Omit the sensitive fields from returning the users.
"""

# Lib Imports
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

# Module Imports
from api.routes.users.controllers import create_user, get_all_users, update_user, delete_user, get_user_by_id, get_all_lawyers, get_all_clients
from api.routes.users.auth_controllers import generate_access_token, check_admin, check_user_or_admin
from api.utils.status_codes import Status
from api.utils.helper import check_mandatory

# ----------------------------------------------- #

user_routes = Blueprint('users', __name__)

# -- Lawyer Specific -- #

@user_routes.route('/lawyer', methods=['POST'])
def create_new_lawyer():
    data = request.get_json()
    
    is_missing, missing_keys = check_mandatory(['email', 'username', 'password', 'first_name', 'last_name'], data)
    if is_missing:
        return jsonify(error=f'Missing mandatory key(s): {", ".join(missing_keys)}'), Status.HTTP_400_BAD_REQUEST
    
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

    new_lawyer = create_user(email, username, password, first_name, last_name, dob, country, phone_number, role='lawyer', bar_association_id=bar_association_id, experience_years=experience_years)
    if new_lawyer is None:
        return jsonify({'message': 'User with the same email or username already exists'}), Status.HTTP_409_CONFLICT
    return jsonify(new_lawyer.toDict()), Status.HTTP_200_OK

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
    data = request.get_json()
    
    is_missing, missing_keys = check_mandatory(['email', 'username', 'password', 'first_name', 'last_name'], data)
    if is_missing:
        return jsonify(error=f'Missing mandatory key(s): {", ".join(missing_keys)}'), Status.HTTP_400_BAD_REQUEST
    
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    dob = data.get('dob')
    country = data.get('country')
    phone_number = data.get('phone_number')
    case_details = data.get('case_details')

    new_client = create_user(email, username, password, first_name, last_name, dob, country, phone_number, role='client', case_details=case_details)
    if new_client is None:
        return jsonify({'message': 'User with the same email or username already exists'}), Status.HTTP_409_CONFLICT
    
    return jsonify(new_client.toDict()), Status.HTTP_200_OK

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
    
    is_user_or_admin = check_user_or_admin(user=get_jwt_identity(), id=user_id)
    if not is_user_or_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    user = get_user_by_id(user_id)
    if user:
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

# -- Auth Routes -- #

# User Login Endpoint
@user_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    is_missing, missing_keys = check_mandatory(['email', 'password'], data)
    if is_missing:
        return jsonify(error=f'Missing mandatory key(s): {", ".join(missing_keys)}'), Status.HTTP_400_BAD_REQUEST
    
    email = data.get('email')
    password = data.get('password')

    is_authorized, token = generate_access_token(email=email, password=password)
    if is_authorized:
        return jsonify(access_token=token), Status.HTTP_200_OK
    
    return jsonify({'message': 'Invalid credentials'}), Status.HTTP_401_UNAUTHORIZED

# Protected Endpoint for Users
@user_routes.route('/profile', methods=['GET'])
@jwt_required()  # Requires authentication with JWT
def user_profile():
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id=user_id)
    return jsonify({'email': user.email, 'username': user.username})
