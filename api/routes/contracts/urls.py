"""
    DESC:
        Blueprint for Contract related routes.
"""

# Lib Imports
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

# Module Imports
from .controllers import create_contract, get_all_contracts, get_all_contract_by_id, get_all_user_contracts, accept_user_contract, end_user_contract
from api.utils.status_codes import Status
from api.decorators.mandatory_keys import check_mandatory
from api.decorators.access_control_decorators import admin_required, user_or_admin_required

# ----------------------------------------------- #

contract_routes = Blueprint('contract', __name__)

@contract_routes.route('/', methods=['POST'])
@jwt_required()
@check_mandatory(['title', 'description', 'client_id', 'lawyer_id'])
def create_new_contract():
        
    data = request.get_json()
    creator_id = get_jwt_identity().get('id')
    title = data.get('title')
    description = data.get('description')
    client_id = data.get('client_id')
    lawyer_id = data.get('lawyer_id')
    
    new_contract = create_contract(creator_id, title, description, lawyer_id, client_id)
    if new_contract is None:
        return jsonify({'message': 'Error while creating contract'}), Status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return jsonify(new_contract.to_dict()), Status.HTTP_200_OK

@contract_routes.route('/', methods=['GET'])
@jwt_required()
@admin_required
def all_contracts():
    
    contracts = get_all_contracts()
    if contracts:
        return jsonify([contract.to_dict() for contract in contracts]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No contract found'}), Status.HTTP_404_NOT_FOUND

@contract_routes.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_contract(id):
        
    contract = get_all_contract_by_id(id)
    if contract:
        return jsonify(contract.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'message': 'Contract not found'}), Status.HTTP_404_NOT_FOUND

@contract_routes.route('/my-contracts', methods=['GET'])
@jwt_required()
def get_user_contracts():
    
    id = get_jwt_identity().get('id')
    contracts = get_all_user_contracts(id)
    if contracts:
        return jsonify([contract.to_dict() for contract in contracts]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No contracts found'}), Status.HTTP_404_NOT_FOUND

@contract_routes.route('/user/<int:id>', methods=['GET'])
@jwt_required()
@user_or_admin_required
def get_user_contracts_id(id):
    
    contracts = get_all_user_contracts(id)
    if contracts:
        return jsonify([contract.to_dict() for contract in contracts]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No contracts found'}), Status.HTTP_404_NOT_FOUND

@contract_routes.route('/accept-contract/<int:id>', methods=['GET'])
@jwt_required()
def approve_contract(id):
    
    approver_id = get_jwt_identity().get('id')
    response, status_code = accept_user_contract(contract_id=id, approver_id=approver_id)
    return jsonify(response), status_code

@contract_routes.route('/end-contract/<int:id>', methods=['POST'])
@jwt_required()
@check_mandatory(['ended_reason'])
def end_contract(id):
    
    data = request.get_json()
    reason = data.get('ended_reason')
    contract = end_user_contract(contract_id=id, reason=reason)
    if contract:
        return jsonify(contract.to_dict()), Status.HTTP_200_OK
    return jsonify({'message': 'Contract not found'}), Status.HTTP_404_NOT_FOUND

