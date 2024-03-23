# Lib Imports
from flask import Blueprint, jsonify, request, send_file
import os

# File Imports
from api.routes.users.controllers import create_user, get_user_by_id, get_all_users, update_user, delete_user

user_routes = Blueprint('users', __name__)


### Routes for Users below:
##
#
@user_routes.route('/', methods=['GET'])
def index():
    return jsonify(message='API Route for Users')

@user_routes.route('/client', methods=['POST'])
def create_new_user():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    dob = data.get('dob')
    country = data.get('country')
    phone_number = data.get('phone_number')

    new_user = create_user(email, username, dob, country, phone_number)
    return jsonify(new_user.toDict())

@user_routes.route('/client/<user_id>', methods=['GET'])
def get_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user.toDict())
    return jsonify({'message': 'User not found'}), 404

@user_routes.route('/client', methods=['GET'])
def get_all():
    users = get_all_users()
    return jsonify([user.toDict() for user in users])

@user_routes.route('/client/<user_id>', methods=['PUT'])
def update_existing_user(user_id):
    data = request.get_json()
    updated_user = update_user(user_id, **data)
    if updated_user:
        return jsonify(updated_user.toDict())
    return jsonify({'message': 'User not found'}), 404

@user_routes.route('/client/<user_id>', methods=['DELETE'])
def delete_existing_user(user_id):
    deleted_user = delete_user(user_id)
    if deleted_user:
        return jsonify({'message': f'User with id {user_id} deleted successfully!'}), 204
    return jsonify({'message': 'User not found'}), 404
