# Module Imports
import stripe
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

def process_contract_payment(contract_id, token):
    # Retrieve the contract from the database
    contract = Contract.query.get(contract_id)
    if not contract:
        return {'error': 'Contract not found.'}, Status.HTTP_404_NOT_FOUND
    
    # Calculate the amount to charge (in cents or your currency's smallest unit)
    amount = contract.price
    
    try:
        # Create a charge using the Stripe token
        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',  # Change this to your desired currency
            source=token,
            description='Payment for contract'
        )
        
        # Update contract fields based on payment success
        contract.is_paid = True
        contract.accepted_on = datetime.now()
        
        # Commit changes to the database
        db.session.commit()
        
        return {'message': 'Payment successful.'}, Status.HTTP_200_OK
    
    except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
        return {'error': str(e)}, Status.HTTP_400_BAD_REQUEST
    
    except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
        return {'error': 'Rate limit error.'}, Status.HTTP_429_TOO_MANY_REQUESTS
    
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
        return {'error': 'Invalid parameters.'}, Status.HTTP_400_BAD_REQUEST
    
    except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        return {'error': 'Authentication failed.'}, Status.HTTP_401_UNAUTHORIZED
    
    except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
        return {'error': 'Network communication failed.'}, Status.HTTP_500_INTERNAL_SERVER_ERROR
    
    except stripe.error.StripeError as e:
        # Generic error from Stripe
        return {'error': 'Stripe error.'}, Status.HTTP_500_INTERNAL_SERVER_ERROR
    
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        return {'error': 'An error occurred.'}, Status.HTTP_500_INTERNAL_SERVER_ERROR
