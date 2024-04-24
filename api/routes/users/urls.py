"""
    FIXME:  1  - Add missing keys error in routes.                                       - [DONE]
            2  - Add account deactivation/activation route.                              - [DONE]
            3  - Add account suspension & STATUS route.                                  - [DONE]
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
            14 - Change update existing user controller to handle all user updation.     - [DONE]
            15 - FIX: Cascade in lawyers & clients table upon user deletion              - [DONE] -> VIA Controller
            16 - Substitute prefixes in routes with (-) e.g. de-activate                 - [DONE]
            17 - Add Comments.                                                           - []
            18 - Remove JWT from get_user, get_lawyer and get_client                     - [DONE]
            19 - Make auth_controller or access_checker decorator as well                -
    
    TODO:
        Refactor:
            1 - Make code more reusable.
                  - Moved check_mandatory() to decorators, previous version depreciated.
            2 - Separate unconcering logic.
            3 - Remove redundant bits.
"""

# Lib Imports
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from

# Module Imports
from api.routes.users.controllers import create_user, get_all_users, update_user, delete_user, get_user_by_id, get_all_lawyers, get_all_clients, self_activate_user_account, self_deactivate_user_account, change_password
from api.routes.users.auth_controllers import generate_access_token, check_admin, check_user_or_admin
from api.utils.status_codes import Status
from api.utils.helper import omit_sensitive_fields
from api.utils.decorators import check_mandatory

# ----------------------------------------------- #

user_routes = Blueprint('users', __name__)

# -- Lawyer Specific -- #

@user_routes.route('/lawyer', methods=['POST'])
@swag_from(methods=['POST']) 
@check_mandatory(['email', 'username', 'password', 'first_name', 'last_name', 'address'])
def create_new_lawyer():
    """
    Endpoint to create a new lawyer.

    ---
    tags:
      - Lawyer
    description: Create a new lawyer with the provided information.
    parameters:
      - name: email
        in: formData
        type: string
        required: true
        description: Email address of the lawyer.
      - name: username
        in: formData
        type: string
        required: true
        description: Username of the lawyer.
      # Add other parameters here...

    responses:
      200:
        description: Successful operation. Returns the created lawyer.
      409:
        description: Conflict. User with the same email or username already exists.
    """
    
    data = request.form
    
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    dob = data.get('dob')
    country = data.get('country')
    phone_number = data.get('phone_number')
    address = data.get('address')
    bar_association_id = data.get('bar_association_id')
    experience_years = data.get('experience_years')
    profile_image = request.files.get('profile_pic')

    new_lawyer = create_user(email, username, password, first_name, last_name, dob, country, phone_number, address, profile_image, role='lawyer', bar_association_id=bar_association_id, experience_years=experience_years)
    if new_lawyer is None:
        return jsonify({'message': 'User with the same email or username already exists'}), Status.HTTP_409_CONFLICT
    
    returned_lawyer = omit_sensitive_fields(new_lawyer)
    return jsonify(returned_lawyer), Status.HTTP_200_OK

# JWT Not required - can be accessed outside authorization
@user_routes.route('/lawyer', methods=['GET'])
@swag_from(methods=['GET'])
def all_lawyers():
    """
    Endpoint to retrieve all lawyers.

    ---
    tags:
      - Lawyer
    description: Retrieve a list of all lawyers.
    responses:
      200:
        description: Successful operation. Returns a list of lawyers.
      404:
        description: No lawyer user found.
    """
    
    lawyers = get_all_lawyers()
    if lawyers:
        return jsonify([lawyer.to_dict() for lawyer in lawyers]), Status.HTTP_200_OK
    return jsonify({'message': 'No lawyer user found'}), Status.HTTP_404_NOT_FOUND

# -- Client Specific -- #

@user_routes.route('/client', methods=['POST'])
@swag_from(methods=['POST'])
@check_mandatory(['email', 'username', 'password', 'first_name', 'last_name', 'address'])
def create_new_client():
    """
    Endpoint to create a new client.

    ---
    tags:
      - Client
    description: Create a new client with the provided information.
    parameters:
      - name: email
        in: formData
        type: string
        required: true
        description: Email address of the client.
      - name: username
        in: formData
        type: string
        required: true
        description: Username of the client.
      # Add other parameters here...

    responses:
      200:
        description: Successful operation. Returns the created client.
      409:
        description: Conflict. User with the same email or username already exists.
    """
    
    data = request.form
    
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    dob = data.get('dob')
    country = data.get('country')
    phone_number = data.get('phone_number')
    address = data.get('address')
    case_details = data.get('case_details')
    profile_image = request.files.get('profile_pic')

    new_client = create_user(email, username, password, first_name, last_name, dob, country, phone_number, address, profile_image, role='client', case_details=case_details)
    if new_client is None:
        return jsonify({'message': 'User with the same email or username already exists'}), Status.HTTP_409_CONFLICT
    
    # Remove sensitive fields
    returned_client = omit_sensitive_fields(new_client)
    return jsonify(returned_client), Status.HTTP_200_OK

@user_routes.route('/client', methods=['GET'])
@swag_from(methods=['GET'])
def all_clients():
    """
    Endpoint to retrieve all clients.

    ---
    tags:
      - Client
    description: Retrieve a list of all clients.
    responses:
      200:
        description: Successful operation. Returns a list of clients.
      401:
        description: Unauthorized access.
      404:
        description: No client user found.
    """
    
    clients = get_all_clients()
    if clients:
        return jsonify([client.to_dict() for client in clients]), Status.HTTP_200_OK
    return jsonify({'message': 'No client user found'}), Status.HTTP_404_NOT_FOUND

# -- General User Routes -- #

@user_routes.route('/<int:user_id>', methods=['GET'])
@swag_from(methods=['GET'])
def get_user(user_id):
    """
    Endpoint to retrieve user details by user ID.

    ---
    tags:
      - User
    description: Retrieve user details by user ID.
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: ID of the user to retrieve.
    responses:
      200:
        description: Successful operation. Returns user details.
      401:
        description: Unauthorized access.
      404:
        description: User not found.
    """
    
    user = get_user_by_id(user_id)
    
    if user:
      returned_user = omit_sensitive_fields(user)
      return jsonify(returned_user), Status.HTTP_200_OK
    
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/', methods=['GET'])
@jwt_required()
@swag_from(methods=['GET'])
def get_all():
    """
    Endpoint to retrieve all users.

    ---
    tags:
      - User
    description: Retrieve a list of all users.
    security:
      - JWT: []
    responses:
      200:
        description: Successful operation. Returns a list of users.
      401:
        description: Unauthorized access.
      404:
        description: No user found.
    """
    
    is_admin = check_admin(get_jwt_identity())
    if not is_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    users = get_all_users()
    if users:
        return jsonify([user.to_dict() for user in users]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No user found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@swag_from(methods=['PUT'])
def update_existing_user(user_id):
    """
    Endpoint to update an existing user by user ID.

    ---
    tags:
      - User
    description: Update an existing user by user ID.
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: ID of the user to update.
    responses:
      200:
        description: Successful operation. Returns the updated user details.
      401:
        description: Unauthorized access.
      404:
        description: User not found.
    """
    
    # Get the identity (user ID and role) from the JWT token
    is_user_or_admin = check_user_or_admin(user=get_jwt_identity(), id=user_id)
    if not is_user_or_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    data = request.form
    profile_image = request.files.get('profile_image')
    
    updated_user = update_user(user_id, profile_image=profile_image, **data)
    if updated_user:
        return jsonify(updated_user.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@swag_from(methods=['DELETE'])
def delete_existing_user(user_id):
    """
    Endpoint to delete an existing user by user ID.

    ---
    tags:
      - User
    description: Delete an existing user by user ID.
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: ID of the user to delete.
    responses:
      204:
        description: Successful operation. No content returned.
      401:
        description: Unauthorized access.
      404:
        description: User not found.
    """
    
    is_user_or_admin = check_user_or_admin(user=get_jwt_identity(), id=user_id)
    if not is_user_or_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    deleted_user = delete_user(user_id)
    if deleted_user:
        return jsonify({'message': f'User with id {user_id} deleted successfully!'}), Status.HTTP_204_NO_CONTENT
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/de-activate/<int:user_id>', methods=['POST'])
@jwt_required()
@swag_from(methods=['POST'])
@check_mandatory(['reason'])
def deactivate_account(user_id):
    """
    Endpoint to deactivate an account by user ID.

    ---
    tags:
      - User
    description: Deactivate an account by user ID.
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: ID of the user to deactivate.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              reason:
                type: string
                description: Reason for deactivation.
    responses:
      200:
        description: Successful operation. User deactivated.
      401:
        description: Unauthorized access.
      404:
        description: User not found.
    """
    
    current_user = get_jwt_identity()
    
    data = request.get_json()
    reason = data.get('reason')
    
    # Admin can also de-activate user account.
    is_user_or_admin = check_user_or_admin(user=current_user, id=user_id)
    if not is_user_or_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED  
    
    deactivated_user = self_deactivate_user_account(user_id=user_id, reason=reason)
    
    if deactivated_user is not None:
        return jsonify({'message': f'User with id {user_id} deactivated successfully!'}), Status.HTTP_200_OK
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND
    
@user_routes.route('/activate/<int:user_id>', methods=['GET'])
@jwt_required()
@swag_from(methods=['GET'])
def activate_account(user_id):
    """
    Endpoint to activate an account by user ID.

    ---
    tags:
      - User
    description: Activate an account by user ID.
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: ID of the user to activate.
    responses:
      200:
        description: Successful operation. User activated.
      401:
        description: Unauthorized access.
      404:
        description: User not found.
    """
    
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

@user_routes.route('/suspend/<int:user_id>', methods=['POST'])
@jwt_required()
@swag_from(methods=['POST'])
@check_mandatory(['status'])
def suspend_account(user_id):
    """
    Endpoint to suspend an account by user ID.

    ---
    tags:
      - User
    description: Suspend an account by user ID.
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: ID of the user to suspend.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              status:
                type: string
                description: Status of the suspension.
              reason:
                type: string
                description: Reason for suspension.
    responses:
      200:
        description: Successful operation. User suspended.
      401:
        description: Unauthorized access.
      404:
        description: User not found.
    """
    
    current_user = get_jwt_identity()
    
    # Admin can also activate user account.
    is_admin = check_admin(user=current_user)
    if not is_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    data = request.get_json()
    
    status = data.get('status')
    reason = data.get('reason')
    
    suspended_user = update_existing_user(user_id=user_id, is_suspended=True, status=status, reason=reason)
    
    # User exists check:
    if suspended_user is not None:
        return jsonify({'message': f'User with id {user_id} activated successfully!'}), Status.HTTP_200_OK
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/un-suspend/<int:user_id>', methods=['POST'])
@jwt_required()
@swag_from(methods=['POST'])
@check_mandatory(['status'])
def unsuspend_account(user_id):
    """
    Endpoint to unsuspend an account by user ID.

    ---
    tags:
      - User
    description: Unsuspend an account by user ID.
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: ID of the user to unsuspend.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              status:
                type: string
                description: Status of the unsuspension.
              reason:
                type: string
                description: Reason for unsuspension.
    responses:
      200:
        description: Successful operation. User unsuspended.
      401:
        description: Unauthorized access.
      404:
        description: User not found.
    """
    
    current_user = get_jwt_identity()
    
    # Admin can also activate user account.
    is_admin = check_admin(user=current_user)
    if not is_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    data = request.get_json()
    
    status = data.get('status')
    reason = data.get('reason')
    
    unsuspended_user = update_existing_user(user_id=user_id, is_suspended=False, status=status, reason=reason)
    
    # User exists check:
    if unsuspended_user is not None:
        return jsonify({'message': f'User with id {user_id} activated successfully!'}), Status.HTTP_200_OK
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/change-password/<int:user_id>', methods=['POST'])
@jwt_required()
@swag_from(methods=['POST'])
@check_mandatory(['old_password', 'new_password'])
def change_user_password(user_id):
    """
    Endpoint to change a user's password by user ID.

    ---
    tags:
      - User
    description: Change a user's password by user ID.
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: ID of the user to change password for.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              prev_pass:
                type: string
                description: Previous password.
              new_pass:
                type: string
                description: New password.
    responses:
      200:
        description: Successful operation. Password changed.
      401:
        description: Unauthorized access.
      400:
        description: New password and previous password do not match.
      404:
        description: User not found.
    """
    
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # Access control check:
    is_user_or_admin = check_user_or_admin(user=current_user, id=user_id)
    if not is_user_or_admin:
        return jsonify({'message': 'Unauthorized access'}), Status.HTTP_401_UNAUTHORIZED
    
    prev_pass = data.get('old_password')
    new_pass = data.get('new_password')
    
    changed_user_password = change_password(user_id=user_id, prev_password=prev_pass, new_password=new_pass)
    
    if not changed_user_password:
        return jsonify({'message': 'New password and previous password do not match!'}), Status.HTTP_400_BAD_REQUEST
    
    if changed_user_password is not None:
        return jsonify({'message': f'Password change operation for User with id {user_id} successful!'}), Status.HTTP_200_OK
    
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

# -- Auth Routes -- #

# User Login Endpoint
@user_routes.route('/login', methods=['POST'])
@swag_from(methods=['POST'])
@check_mandatory(['email', 'password'])
def login():
    """
    Endpoint for user login.

    ---
    tags:
      - Auth
    description: Authenticate user and generate access token.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                description: User's email address.
              password:
                type: string
                description: User's password.
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

    is_authorized, token = generate_access_token(email=email, password=password)
    if is_authorized:
        return jsonify(access_token=token), Status.HTTP_200_OK
    
    return jsonify({'message': 'Invalid credentials'}), Status.HTTP_401_UNAUTHORIZED
