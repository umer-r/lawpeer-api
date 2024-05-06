# Module Imports
import stripe
from stripe import StripeError, checkout

from datetime import datetime
from api.database import db
from api.models.contract import Contract
from api.utils.status_codes import Status

# ----------------------------------------------- #

def create_contract(creator_id, title, description, lawyer_id, client_id, price, **kwargs):
    
    new_contract = Contract(creator_id=creator_id, title=title, description=description, lawyer_id=lawyer_id, client_id=client_id, price=price, **kwargs)
    db.session.add(new_contract)
    db.session.commit()
    
    return new_contract

def get_all_contracts():
    
    return Contract.query.all()

def get_all_contract_by_id(id):
    
    return Contract.query.get(id)

def get_all_user_contracts(id):
    
    contracts = Contract.query.filter(
            (Contract.creator_id == id) |
            (Contract.lawyer_id == id) |
            (Contract.client_id == id)
        ).all()
    
    return contracts

def accept_user_contract(contract_id, approver_id):
    # Check if the contract with the given ID exists
    contract = Contract.query.get(contract_id)
    if not contract:
        return {'message': 'Contract not found'}, Status.HTTP_404_NOT_FOUND

    # Check if the current user is authorized to approve the contract
    if approver_id == contract.creator_id:
        return {'message': 'Unauthorized access. Creator cannot accept contract'}, Status.HTTP_401_UNAUTHORIZED
    if approver_id not in [contract.client_id, contract.lawyer_id]:
        return {'message': 'Unauthorized access. User not associated with contract'}, Status.HTTP_401_UNAUTHORIZED

    # Update the contract status to approved
    contract.is_accepted = True
    contract.accepted_on = datetime.now()
    db.session.commit()

    return {'message': f'Success! User: {approver_id} accepted the Contract.'}, Status.HTTP_200_OK

def end_user_contract(contract_id, reason):
    contract = Contract.query.get(contract_id)
    if contract:
        contract.is_ended = True
        contract.ended_on = datetime.now()
        contract.ended_reason = reason
        db.session.commit()
        return contract
    return None

def create_checkout_session(id, success_url, cancel_url):
    
    # Retrieve contract details
    contract = Contract.query.get(id)
    if not contract:
        return {'message': 'Contract not found'}, Status.HTTP_404_NOT_FOUND

    # Check if the contract price is valid
    price = contract.price
    if not price:
        return {'message': 'Contract price is missing or invalid'}, Status.HTTP_400_BAD_REQUEST

    try:
        # Create Stripe Checkout session
        session = checkout.Session.create(
            success_url=success_url,
            cancel_url=cancel_url,
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "unit_amount": price * 100, 
                        "currency": "usd", 
                        "product": "Contract"
                    }, 
                    "quantity": 1
                }],
            mode="payment",
        )
        return {'session_id': session.id, 'success_url': session.success_url, 'cancel_url': session.cancel_url}, Status.HTTP_200_OK
    
    except StripeError as e:
        return {'message': str(e)}, Status.HTTP_500_INTERNAL_SERVER_ERROR
