"""
    Blueprint (urls) File; Contains routes related to contracts management.

    External Libraries:
        - flask
        - flask_jwt_extended
        - stripe

    Function Names:
        - create_new_contract: (JWT)    Create a new contract, AC: lawyer_required, MANDATORY: title, description, client_id, price.
        - all_contracts: (JWT)          Get all contracts from the database, AC: admin_required.
        - get_contract: (JWT)           Get single contract by ID.
        - get_user_contracts: (JWT)     Get all contracts of the current user.
        - delete_contract: (JWT)        Delete contract by ID.
        - get_user_contracts_id:        Get all contracts of a user by ID, AC: user_or_admin_required.
        - end_contract: (JWT)           End contract by ID, AC: client_required, MANDATORY: ended_reason.
        - checkout_session:             Create a checkout session for payment, MANDATORY: contract_id, success_url, cancel_url.
        - pay_contract: (JWT)           Initiate payment for a contract, AC: client_required, MANDATORY: contract_id.
        - stripe_webhook:               Handle Stripe webhook events.

    TODO:   1 - Implement Withdraw system for contracts                             - [HALT] -> Moved to deletion
            2 - GET for all contracts of client from jwt                            - [DONE]
            3 - Cascade review_id if contract deleted?                              - []
            4 - Remove accept-contract functionality                                - [DONE]
            5 - Implement access control                                            - [DONE]
            6 - Implement deletion of contracts                                     - [DONE]
"""

# Lib Imports:
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

# Module Imports:
from .controllers import create_contract, get_all_contracts, get_all_contract_by_id, get_all_user_contracts, end_user_contract, create_checkout_session, delete_contract_by_id, stripe_payment_intent, webhook
from api.utils.status_codes import Status
from api.decorators.mandatory_keys import check_mandatory
from api.decorators.access_control_decorators import admin_required, user_or_admin_required, lawyer_required, client_required

# ----------------------------------------------- #

contract_routes = Blueprint('contract', __name__)

@contract_routes.route('/', methods=['POST'])
@jwt_required()
@check_mandatory(['title', 'description', 'client_id', 'price'])
@lawyer_required
def create_new_contract():
        
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    client_id = data.get('client_id')
    lawyer_id = get_jwt_identity().get('id')
    price = data.get('price')
    
    new_contract = create_contract(title, description, lawyer_id, client_id, price)
    if new_contract is None:
        return jsonify({'error': 'Error while creating contract'}), Status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return jsonify(new_contract.to_dict()), Status.HTTP_200_OK

@contract_routes.route('/', methods=['GET'])
@jwt_required()
@admin_required
def all_contracts():
    
    contracts = get_all_contracts()
    if contracts:
        return jsonify([contract.to_dict() for contract in contracts]), Status.HTTP_200_OK
    
    return jsonify({'error': 'No contract found'}), Status.HTTP_404_NOT_FOUND

@contract_routes.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_contract(id):
        
    contract = get_all_contract_by_id(id)
    if contract:
        return jsonify(contract.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'error': 'Contract not found'}), Status.HTTP_404_NOT_FOUND

@contract_routes.route('/my-contracts', methods=['GET'])
@jwt_required()
def get_user_contracts():
    
    id = get_jwt_identity().get('id')
    contracts = get_all_user_contracts(id)
    if contracts:
        return jsonify([contract.to_dict() for contract in contracts]), Status.HTTP_200_OK
    
    return jsonify({'error': 'No contracts found'}), Status.HTTP_404_NOT_FOUND

@contract_routes.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_contract(id):
        
    response, status_code = delete_contract_by_id(id)
    return jsonify(response), status_code

@contract_routes.route('/user/<int:id>', methods=['GET'])
@jwt_required()
@user_or_admin_required
def get_user_contracts_id(id):
    
    contracts = get_all_user_contracts(id)
    if contracts:
        return jsonify([contract.to_dict() for contract in contracts]), Status.HTTP_200_OK
    
    return jsonify({'error': 'No contracts found'}), Status.HTTP_404_NOT_FOUND

@contract_routes.route('/end-contract/<int:id>', methods=['POST'])
@jwt_required()
@check_mandatory(['ended_reason'])
@client_required
def end_contract(id):
    
    data = request.get_json()
    reason = data.get('ended_reason')
    client_id = get_jwt_identity().get('id')
    response, status_code = end_user_contract(contract_id=id, reason=reason, client_id=client_id)
    
    return jsonify(response), status_code

@contract_routes.route('/create-checkout-session', methods=['POST'])
@check_mandatory(['contract_id', 'success_url', 'cancel_url'])
def checkout_session():
    data = request.get_json()
    contract_id = data.get('contract_id')
    success_url = data.get('success_url')
    cancel_url = data.get('cancel_url')

    response, status_code = create_checkout_session(contract_id, success_url, cancel_url)
    return jsonify(response), status_code

@contract_routes.route("/payment", methods=["POST"])
@jwt_required()
@client_required
@check_mandatory(['contract_id'])
def pay_contract():
    data = request.json
    contract_id = data.get("contract_id")
    client_id = get_jwt_identity().get('id')
    response, status_code = stripe_payment_intent(contract_id, client_id)
    return jsonify(response), status_code     

@contract_routes.route("/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("stripe-signature")

    response, status_code = webhook(payload, sig_header)
    return jsonify(response), status_code
