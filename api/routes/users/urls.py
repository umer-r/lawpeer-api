"""
    FIXME:  1  - Add missing keys error in routes.                                       - [DONE]
            2  - Add account deactivation/activation route.                              - [DONE]
            3  - Add account suspension & STATUS route.                                  - [DONE]
            4  - Omit the sensitive fields from returning the users.                     - [DONE]
            5  - Change Status 400 to 422 UNPROCESSABLE_ENTITY.                          - [DONE]
            6  - Implement Profile picture send back functionality in get user by ID.    - [DONE]
            7  - Implement Refresh Token Logic.                                          - [HALT] -> Moved to (9).
            8  - Implement Email verification for users.                                 - [DONE]
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
            19 - Make auth_controller or access_checker decorator as well                - [DONE]
            20 - Implement forget password functionality.                                - [DONE]
            21 - Make filter-lawyer handle lawyer names searches                         - []
            
    
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
from flask_mail import Message
from flasgger import swag_from

# Extentions Imports:
from api.extentions.mail import mail
# from api.__init__ import mail

# Utils Imports:
from api.utils.otp_generator import save_otp, verify_otp, generate_otp, delete_all_otps
from api.utils.status_codes import Status
from api.utils.helper import omit_user_sensitive_fields
from api.utils.token_generator import generate_user_access_token

# Controllers Imports:
from .controllers import create_user, get_all_users, update_user, update_profile_picture, delete_user, get_user_by_id, get_all_lawyers, get_all_clients, self_activate_user_account, self_deactivate_user_account, change_password, reset_password, verify_user_account, filter_lawyer_users

# Decorators Imports:
from api.decorators.mandatory_keys import check_mandatory, check_at_least_one_key
from api.decorators.access_control_decorators import admin_required, user_or_admin_required

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
    
    returned_lawyer = omit_user_sensitive_fields(new_lawyer)
    return jsonify(returned_lawyer), Status.HTTP_200_OK

@user_routes.route('/lawyer', methods=['GET'])
@swag_from(methods=['GET'])
@jwt_required()
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
    is_admin = get_jwt_identity().get('role')
    lawyers = get_all_lawyers(is_admin)
    if lawyers:
        return jsonify([lawyer.to_dict() for lawyer in lawyers]), Status.HTTP_200_OK
    return jsonify({'message': 'No lawyer user found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/lawyer/filter-lawyers', methods=['POST'])
@jwt_required()
@check_at_least_one_key(['city', 'skill_ids', 'above_experience_years', 'above_average_rating'])
def filter_lawyers():
    data = request.json

    is_admin = get_jwt_identity().get('role')
    city = data.get('city')
    skill_ids = data.get('skill_ids', [])
    above_experience_years = data.get('above_experience_years')
    above_average_rating = data.get('above_average_rating')
    
    lawyers = filter_lawyer_users(is_admin=is_admin, city=city, skill_ids=skill_ids, above_experience_years=above_experience_years, above_average_rating=above_average_rating)
    if lawyers:
      return jsonify([lawyer.to_dict() for lawyer in lawyers]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No Lawyer user found matching the filters'}), Status.HTTP_404_NOT_FOUND

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
    returned_client = omit_user_sensitive_fields(new_client)
    return jsonify(returned_client), Status.HTTP_200_OK

@user_routes.route('/client', methods=['GET'])
@swag_from(methods=['GET'])
@jwt_required()
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
    
    is_admin = get_jwt_identity().get('role')
    clients = get_all_clients(is_admin)
    if clients:
        return jsonify([client.to_dict() for client in clients]), Status.HTTP_200_OK
    return jsonify({'message': 'No client user found'}), Status.HTTP_404_NOT_FOUND

# -- General User Routes -- #

@user_routes.route('/<int:id>', methods=['GET'])
@swag_from(methods=['GET'])
@jwt_required()
def get_user(id):
    """
    Endpoint to retrieve user details by user ID.

    ---
    tags:
      - User
    description: Retrieve user details by user ID.
    parameters:
      - name: id
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
    
    is_admin = get_jwt_identity().get('role')
    current_user = get_jwt_identity().get('id')
    is_same_user = True if current_user == id else False
    user = get_user_by_id(id, is_admin, is_same_user)
    
    if user:
      returned_user = omit_user_sensitive_fields(user)
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
    
    users = get_all_users()
    if users:
        return jsonify([user.to_dict() for user in users]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No user found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/<int:id>', methods=['PUT'])
@jwt_required()
@swag_from(methods=['PUT'])
@user_or_admin_required
def update_existing_user(id):
    """
    Endpoint to update an existing user by user ID.

    ---
    tags:
      - User
    description: Update an existing user by user ID.
    security:
      - JWT: []
    parameters:
      - name: id
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

    data = request.form
    profile_image = request.files.get('profile_image')
    
    updated_user = update_user(id, profile_image=profile_image, **data)
    if updated_user:
        return jsonify(updated_user.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND
  
@user_routes.route('/update-profile-image/<int:id>', methods=['PUT'])
@jwt_required()
@user_or_admin_required
def update_profile(id):
  
    profile_image = request.files.get('profile_image')
    
    updated_user = update_profile_picture(id, profile_image=profile_image)
    if updated_user:
        return jsonify(updated_user.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@swag_from(methods=['DELETE'])
@admin_required
def delete_existing_user(id):
    """
    Endpoint to delete an existing user by user ID.

    ---
    tags:
      - User
    description: Delete an existing user by user ID.
    security:
      - JWT: []
    parameters:
      - name: id
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
        
    deleted_user = delete_user(id)
    if deleted_user:
        return jsonify({'message': f'User with id {id} deleted successfully!'}), Status.HTTP_204_NO_CONTENT
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/de-activate/<int:id>', methods=['POST'])
@jwt_required()
@swag_from(methods=['POST'])
@user_or_admin_required
@check_mandatory(['reason'])
def deactivate_account(id):
    """
    Endpoint to deactivate an account by user ID.

    ---
    tags:
      - User
    description: Deactivate an account by user ID.
    security:
      - JWT: []
    parameters:
      - name: id
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
        
    data = request.get_json()
    reason = data.get('reason')
    
    deactivated_user = self_deactivate_user_account(user_id=id, reason=reason)
    
    if deactivated_user is not None:
        return jsonify({'message': f'User with id {id} deactivated successfully!'}), Status.HTTP_200_OK
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND
    
@user_routes.route('/activate/<int:id>', methods=['GET'])
@jwt_required()
@swag_from(methods=['GET'])
@user_or_admin_required
def activate_account(id):
    """
    Endpoint to activate an account by user ID.

    ---
    tags:
      - User
    description: Activate an account by user ID.
    security:
      - JWT: []
    parameters:
      - name: id
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
      
    activated_user = self_activate_user_account(user_id=id)
    
    # Test the following logic:
    if activated_user is not None:
        return jsonify({'message': f'User with id {id} activated successfully!'}), Status.HTTP_200_OK
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/suspend/<int:id>', methods=['POST'])
@jwt_required()
@swag_from(methods=['POST'])
@check_mandatory(['status'])
@admin_required
def suspend_account(id):
    """
    Endpoint to suspend an account by user ID.

    ---
    tags:
      - User
    description: Suspend an account by user ID.
    security:
      - JWT: []
    parameters:
      - name: id
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
       
    data = request.get_json()
    
    status = data.get('status')
    reason = data.get('reason')
    
    suspended_user = update_user(user_id=id, is_suspended=True, status=status, reason=reason)
    
    # User exists check:
    if suspended_user is not None:
        return jsonify({'message': f'User with id {id} Suspended successfully!'}), Status.HTTP_200_OK
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/un-suspend/<int:id>', methods=['POST'])
@jwt_required()
@swag_from(methods=['POST'])
@check_mandatory(['status'])
@admin_required
def unsuspend_account(id):
    """
    Endpoint to unsuspend an account by user ID.

    ---
    tags:
      - User
    description: Unsuspend an account by user ID.
    security:
      - JWT: []
    parameters:
      - name: id
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

    data = request.get_json()
    
    status = data.get('status')
    reason = data.get('reason')
    
    unsuspended_user = update_user(user_id=id, is_suspended=False, status=status, reason=reason)
    
    # User exists check:
    if unsuspended_user is not None:
        return jsonify({'message': f'User with id {id} un-suspended successfully!'}), Status.HTTP_200_OK
    return jsonify({'message': 'User not found'}), Status.HTTP_404_NOT_FOUND

@user_routes.route('/change-password/<int:id>', methods=['POST'])
@jwt_required()
@swag_from(methods=['POST'])
@check_mandatory(['old_password', 'new_password'])
@user_or_admin_required
def change_user_password(id):
    """
    Endpoint to change a user's password by user ID.

    ---
    tags:
      - User
    description: Change a user's password by user ID.
    security:
      - JWT: []
    parameters:
      - name: id
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
    
    data = request.get_json()
    
    prev_pass = data.get('old_password')
    new_pass = data.get('new_password')
    
    changed_user_password = change_password(user_id=id, prev_password=prev_pass, new_password=new_pass)
    
    if not changed_user_password:
        return jsonify({'message': 'New password and previous password do not match!'}), Status.HTTP_400_BAD_REQUEST
    
    if changed_user_password is not None:
        return jsonify({'message': f'Password change operation for User with id {id} successful!'}), Status.HTTP_200_OK
    
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

    is_authorized, token = generate_user_access_token(email=email, password=password)
    if is_authorized:
        return jsonify(access_token=token), Status.HTTP_200_OK
    
    return jsonify({'message': 'Invalid credentials'}), Status.HTTP_401_UNAUTHORIZED

# -- Forgot Password -- #

@user_routes.route('/forgot-password-otp', methods=['POST'])
@check_mandatory(['email'])
def forgot_pass():
    email = request.json.get('email')
    
    otp = generate_otp()
    save_otp(email, otp, otp_for='password_reset')

    msg = Message('Forgot Password - OTP', sender='info.lawpeer@gmail.com', recipients=[email])
    msg.body = f'Your OTP for resetting the password is: {otp}'
    
    try:
        mail.send(msg)
        return jsonify({'message': 'OTP sent successfully'}), Status.HTTP_200_OK
    except Exception as e:
        delete_all_otps(email)
        return jsonify({'error': str(e)}), Status.HTTP_500_INTERNAL_SERVER_ERROR
  
@user_routes.route('/reset-password', methods=['POST'])
@check_mandatory(['email', 'new_password', 'otp'])
def password_reset():
    email = request.json.get('email')
    otp = request.json.get('otp')
    new_password = request.json.get('new_password')
    
    if verify_otp(email, otp):
        resetted_pass = reset_password(email, new_password)
        if resetted_pass:
          delete_all_otps(email)
          return jsonify({'message': 'Password reset successfully'}), Status.HTTP_200_OK
        else:
         return jsonify({'error': f'User with email: {email} not found'}), Status.HTTP_404_NOT_FOUND 
    else:
        return jsonify({'error': 'Invalid OTP or OTP expired'}), Status.HTTP_400_BAD_REQUEST

# -- Email Verification -- #

@user_routes.route('/verify-email-otp', methods=['POST'])
@jwt_required()
@check_mandatory(['email'])
def verify_email_otp():
    email = request.json.get('email')
    
    otp = generate_otp()
    save_otp(email, otp, otp_for='email_verification')

    msg = Message('Email Verification - OTP', sender='info.lawpeer@gmail.com', recipients=[email])
    msg.body = f'Your OTP for email verification is: {otp}'
    
    try:
        mail.send(msg)
        return jsonify({'message': 'OTP sent successfully'}), Status.HTTP_200_OK
    except Exception as e:
        delete_all_otps(email)
        return jsonify({'error': str(e)}), Status.HTTP_500_INTERNAL_SERVER_ERROR
      
@user_routes.route('/verify-email', methods=['POST'])
@jwt_required()
@check_mandatory(['email', 'otp'])
def email_verification():
    email = request.json.get('email')
    otp = request.json.get('otp')
    
    if verify_otp(email, otp):
        verified = verify_user_account(email)
        if verified:
          delete_all_otps(email)
          return jsonify({'message': 'User account verified!'}), Status.HTTP_200_OK
        else:
         return jsonify({'error': f'User with email: {email} not found'}), Status.HTTP_404_NOT_FOUND 
    else:
        return jsonify({'error': 'Invalid OTP or OTP expired'}), Status.HTTP_400_BAD_REQUEST
