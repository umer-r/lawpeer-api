"""    
  Blueprint (urls) file; for Admin related routes.
        
  External Libraries:
    - flask: A micro web framework for Python.
    - flask_jwt_extended: An extension for Flask that adds JWT support to your application.
    - flask_mail: An extension for Flask that adds email sending capabilities to your application.
    - flasgger: An extension for Flask that provides Swagger documentation and UI integration.

  Function Names:
    - create_new_admin:       creates new admin, AC: super_admin_required, MANDATORY: email, password.
    - all_admins:             get all admins from database, AC: admin_required.
    - get_admin:              Get single admin by ID, AC: admin required.
    - update_existing_admin:  Update admin by ID, AC: super_or_current_admin_required.
    - delete_existing_admin:  Update admin by ID, AC: super_or_current_admin_required. 
    - login:                  Generate access_token for admin, MANDATORY: email, password.
    - forgot_pass:            Generate otp for forget password, MANDATORY: email.
    - password_reset:         Reset admin password: MANDATORY: email, new_password, otp.
      
  TODO: 1 - Add JWT logic secure on all routes (Only admins can access these routes).   - [DONE]
        2 - Add DOC strings on each func.                                               - [DONE]
        3 - Implement Super admin logic.                                                - [DONE]
        4 - Test each of the following routes.                                          - [DONE]
        5 - Omit sensitive fields.                                                      - [HALT]
        6 - Move access control to decorators.                                          - [DONE]
        7 - Move generate_access_token to utils.                                        - [DONE]
"""

# Lib Imports
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_mail import Message
from flasgger import swag_from

# Module Imports
from api.extentions.mail import mail
from api.utils.otp_generator import generate_otp, save_otp, verify_otp, delete_all_otps
from api.routes.admin.controllers import create_admin, update_admin, delete_admin, get_admin_by_id, get_all_admin, reset_password
from api.utils.token_generator import generate_admin_access_token
from api.utils.status_codes import Status
from api.decorators.mandatory_keys import check_mandatory
from api.decorators.access_control_decorators import admin_required, super_admin_required, super_or_current_admin_required

# ----------------------------------------------- #

admin_routes = Blueprint('admin', __name__)

@admin_routes.route('/', methods=['POST'])
@swag_from(methods=['POST'])
@jwt_required()
@super_admin_required
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
        
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')
    
    new_admin = create_admin(email, password, phone_number, role='admin')
    if new_admin is None:
        return jsonify({'error': 'Admin with the same email already exists'}), Status.HTTP_409_CONFLICT
    
    return jsonify(new_admin.to_dict()), Status.HTTP_200_OK

@admin_routes.route('/', methods=['GET'])
@jwt_required()
@swag_from(methods=['GET'])
@admin_required
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
    
    admins = get_all_admin()
    if admins:
        return jsonify([admin.to_dict() for admin in admins]), Status.HTTP_200_OK
    
    return jsonify({'error': 'No admin found'}), Status.HTTP_404_NOT_FOUND

@admin_routes.route('/<int:id>', methods=['GET'])
@jwt_required()
@swag_from(methods=['GET'])
@admin_required
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
        
    admin = get_admin_by_id(id)
    if admin:
        return jsonify(admin.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'error': 'Admin not found'}), Status.HTTP_404_NOT_FOUND

@admin_routes.route('/<int:id>', methods=['PUT'])
@jwt_required()
@swag_from(methods=['PUT'])
@super_or_current_admin_required
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
        
    data = request.get_json()
    updated_admin = update_admin(id, **data)
    if updated_admin:
        return jsonify(updated_admin.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'error': 'Admin not found'}), Status.HTTP_404_NOT_FOUND

@admin_routes.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@swag_from(methods=['DELETE'])
@super_or_current_admin_required
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
    
    deleted_admin = delete_admin(id)
    if deleted_admin:
        return jsonify({'message': f'Admin with id {id} deleted successfully!'}), Status.HTTP_204_NO_CONTENT
    
    return jsonify({'error': 'Admin not found'}), Status.HTTP_404_NOT_FOUND

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
    is_authorized, token = generate_admin_access_token(email=email, password=password)
    if is_authorized:
        return jsonify(access_token=token), Status.HTTP_200_OK
    
    return jsonify({'error': 'Invalid credentials'}), Status.HTTP_401_UNAUTHORIZED

@admin_routes.route('/forgot-password-otp', methods=['POST'])
@check_mandatory(['email'])
def forgot_pass():
    email = request.json.get('email')
    
    otp = generate_otp()
    save_otp(email, otp)

    msg = Message('Forgot Password - OTP', sender='info.lawpeer@gmail.com', recipients=[email])
    msg.body = f'Your OTP for resetting the password is: {otp}'
    
    try:
        mail.send(msg)
        return jsonify({'message': 'OTP sent successfully'}), Status.HTTP_200_OK
    except Exception as e:
        delete_all_otps(email)
        return jsonify({'error': str(e)}), Status.HTTP_500_INTERNAL_SERVER_ERROR
  
@admin_routes.route('/reset-password', methods=['POST'])
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
         return jsonify({'error': f'Admin with email: {email} not found'}), Status.HTTP_404_NOT_FOUND 
    else:
        return jsonify({'error': 'Invalid OTP or OTP expired'}), Status.HTTP_400_BAD_REQUEST
