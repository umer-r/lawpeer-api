# Module Imports
import os
import stripe
from datetime import datetime
from stripe import StripeError, checkout

from datetime import datetime
from api.database import db
from api.models.contract import Contract
from api.utils.status_codes import Status

# ----------------------------------------------- #

def create_contract(title, description, lawyer_id, client_id, price, **kwargs):
    new_contract = Contract(title=title, description=description, lawyer_id=lawyer_id, client_id=client_id, price=price, **kwargs)
    db.session.add(new_contract)
    db.session.commit()
    return new_contract

def get_all_contracts():
    
    return Contract.query.all()

def get_all_contract_by_id(id):
    
    return Contract.query.get(id)

def get_all_user_contracts(id):
    
    contracts = Contract.query.filter(
            (Contract.lawyer_id == id) |
            (Contract.client_id == id)
        ).all()
    
    return contracts

def delete_contract_by_id(id):
    contract = Contract.query.get(id)
    if contract:
        if contract.is_paid:
            return {'error': 'Contract is already paid. Can not delete'}, Status.HTTP_400_BAD_REQUEST
        else:
            db.session.delete(contract)
            db.session.commit()
            return {'message': f'Contract with id {id} deleted successfully'}, Status.HTTP_204_NO_CONTENT
            
    return {'error': 'Contract not found'}, Status.HTTP_404_NOT_FOUND

def end_user_contract(contract_id, reason, client_id):
    contract = Contract.query.get(contract_id)
    if contract:
        if contract.is_paid:
            if contract.client_id != client_id:
                return {'error': 'Unauthorized access. Client not associated with the contract'}, Status.HTTP_401_UNAUTHORIZED
            else:
                contract.is_ended = True
                contract.ended_on = datetime.now()
                contract.ended_reason = reason
                db.session.commit()
                return {'message': f'Contract with ID: {contract_id} successfully ended!'}, Status.HTTP_200_OK
        else:
            return {'error': 'Cannot end unpaid contracts'}, Status.HTTP_400_BAD_REQUEST
        
    return {'error': 'Contract not found'}, Status.HTTP_404_NOT_FOUND

def create_checkout_session(id, success_url, cancel_url):
    
    # Retrieve contract details
    contract = Contract.query.get(id)
    if not contract:
        return {'error': 'Contract not found'}, Status.HTTP_404_NOT_FOUND
    
    if contract.is_paid:
        return {'error': 'Contract price is already paid'}, Status.HTTP_400_BAD_REQUEST

    # Check if the contract price is valid
    price = contract.price
    if not price:
        return {'error': 'Contract price is missing or invalid'}, Status.HTTP_400_BAD_REQUEST

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
        return {'error': str(e)}, Status.HTTP_500_INTERNAL_SERVER_ERROR


def stripe_payment_intent(contract_id, client_id):
    
    contract = Contract.query.get(contract_id)
    if not contract:
        return {'error': 'Contract not found'}, Status.HTTP_404_NOT_FOUND
    
    if contract.is_paid:
        return {'error': 'Contract price is already paid'}, Status.HTTP_400_BAD_REQUEST

    # Check if the contract price is valid
    price = contract.price
    if not price:
        return {'error': 'Contract price is missing or invalid'}, Status.HTTP_400_BAD_REQUEST
    
    if client_id != contract.client_id:
        return {'error': 'Unauthorized Access. Client not associated with the contract.'}, Status.HTTP_401_UNAUTHORIZED
    
    amount = int(price)
    try:

        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency="INR",
            payment_method_types=["card"],
            metadata={"contract_id": contract.id, "contract_title": contract.title, "amount": amount, "contract_created": contract.created}
        )

        client_secret = payment_intent.client_secret

        return {"message": "Payment initiated", "clientSecret": client_secret}, Status.HTTP_200_OK
    except Exception as e:
        print(e)
        return {"message": "Internal Server Error"}, Status.HTTP_500_INTERNAL_SERVER_ERROR
    
def webhook(payload, signature):
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, os.environ.get("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError as e:
        # Invalid payload
        return {"error": str(e)}, Status.HTTP_400_BAD_REQUEST
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return {"error": str(e)}, Status.HTTP_400_BAD_REQUEST

    # Handle the event
    if event.type == "payment_intent.created":
        print(f"{event.data.object.metadata['contract_id']} payment initiated!")
    elif event.type == "payment_intent.succeeded":
        id = event.data.object.metadata['contract_id']
        print(f"contract {id} payment succeeded!")
        contract = Contract.query.get(id)
        contract.is_paid = True
        contract.paid_on = datetime.now()
        db.session.commit()

    return {"ok": True}, Status.HTTP_200_OK
