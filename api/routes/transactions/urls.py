"""
    Blueprint (urls) File; Manages routes related to transactions.

    External Libraries:
        - flask
        - flask_jwt_extended
        - sqlalchemy

    Function Names:
        - user_transactions_by_id:          Retrieve transactions of a user by ID.
        - user_transactions: (JWT)          Retrieve transactions of the logged-in user.
        - create_debit_transaction: (JWT)   Create a debit transaction, MANDATORY: description, amount, contract_id.
"""

# Lib Imports:
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from api.models.transaction import Transaction
from api.models.contract import Contract
from api.database import db
from sqlalchemy import inspect
# Module Imports:
from api.utils.status_codes import Status

# Decorators Imports:
from api.decorators.mandatory_keys import check_mandatory
from api.decorators.access_control_decorators import admin_required

# ----------------------------------------------- #

transaction_routes = Blueprint('transaction_routes', __name__)

@transaction_routes.route('/user/<int:user_id>', methods=['GET'])
def user_transactions_by_id(user_id):
    # Retrieve contracts associated with the user
    contracts = Contract.query.filter(
        (Contract.client_id == user_id) | (Contract.lawyer_id == user_id)
    ).all()
    
    # Retrieve transactions associated with the contracts
    transactions = []
    for contract in contracts:
        transactions.extend(contract.transactions)
    
    if transactions:
        return jsonify([transaction.to_dict() for transaction in transactions]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No transactions found!'}), Status.HTTP_404_NOT_FOUND

@transaction_routes.route('/my-transactions', methods=['GET'])
@jwt_required()
def user_transactions():
    # Get user id from JWT token
    user_id = get_jwt_identity().get('id')
    
    # Retrieve contracts associated with the user
    contracts = Contract.query.filter(
        (Contract.client_id == user_id) | (Contract.lawyer_id == user_id)
    ).all()
    
    # Filter transactions based on user type
    transactions = []
    for contract in contracts:
        if contract.client_id == user_id:
            # User is a client, only show debit transactions
            client_transactions = [t for t in contract.transactions if t.transaction_mode == 'debit']
            transactions.extend(client_transactions)
        else:
            # User is a lawyer, show all transactions
            transactions.extend(contract.transactions)
        
    if transactions:
        return jsonify([transaction.to_dict() for transaction in transactions]), Status.HTTP_200_OK
    else:
        return jsonify({'message': 'No transactions found!'}), Status.HTTP_404_NOT_FOUND

@transaction_routes.route('/debit', methods=['POST'])
@check_mandatory(['description', 'amount', 'contract_id'])
@jwt_required()
@admin_required
def create_debit_transaction():
    data = request.json
    
    # Extract required data for the debit transaction
    description = data.get('description')
    amount = data.get('amount')
    contract_id = data.get('contract_id')
    
    # Create a new debit transaction
    transaction = Transaction(
        description=description,
        amount=amount,
        pending=False,
        transaction_mode='debit',
        contract_id=contract_id
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({'message': 'Debit transaction created successfully'}), Status.HTTP_201_CREATED
