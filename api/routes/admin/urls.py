# Lib Imports
from flask import Blueprint, jsonify, request

# Module Imports
from api.routes.admin.controllers import create_admin, update_admin, delete_admin, get_admin_by_id, get_all_admin
from api.utils.status_codes import Status

# ----------------------------------------------- #

admin_routes = Blueprint('admin', __name__)

@admin_routes.route('/', methods=['POST'])
def create_new_admin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')
    
    new_admin = create_admin(email, password, phone_number, role='admin')
    if new_admin is None:
        return jsonify({'message': 'Admin with the same email already exists'}), Status.HTTP_409_CONFLICT
    return jsonify(new_admin.toDict()), Status.HTTP_200_OK

@admin_routes.route('/', methods=['GET'])
def all_admins():
    admins = get_all_admin()
    if admins:
        return jsonify([admin.toDict() for admin in admins]), Status.HTTP_200_OK
    return jsonify({'message': 'No admin found'}), Status.HTTP_404_NOT_FOUND

@admin_routes.route('/<id>', methods=['GET'])
def get_admin(id):
    admin = get_admin_by_id(id)
    if admin:
        return jsonify(admin.toDict()), Status.HTTP_200_OK
    return jsonify({'message': 'Admin not found'}), Status.HTTP_404_NOT_FOUND

@admin_routes.route('/<id>', methods=['PUT'])
def update_existing_admin(id):
    data = request.get_json()
    updated_admin = update_admin(id, **data)
    if updated_admin:
        return jsonify(updated_admin.toDict()), Status.HTTP_200_OK
    return jsonify({'message': 'Admin not found'}), Status.HTTP_404_NOT_FOUND

@admin_routes.route('/<id>', methods=['DELETE'])
def delete_existing_admin(id):
    deleted_admin = delete_admin(id)
    if deleted_admin:
        return jsonify({'message': f'Admin with id {id} deleted successfully!'}), Status.HTTP_204_NO_CONTENT
    return jsonify({'message': 'Admin not found'}), Status.HTTP_404_NOT_FOUND
