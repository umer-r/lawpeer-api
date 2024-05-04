# Module Imports
from datetime import datetime
from api.database import db
from api.models.contract import Contract
from api.utils.status_codes import Status

# ----------------------------------------------- #

def create_contract(creator_id, title, description, lawyer_id, client_id, **kwargs):
    
    new_contract = Contract(creator_id=creator_id, title=title, description=description, lawyer_id=lawyer_id, client_id=client_id, **kwargs)
    db.session.add(new_contract)
    db.session.commit()
    
    return new_contract

def get_all_contracts():
    
    return Contract.query.all()

def get_all_contract_by_id(id):
    
    return Contract.query.get(id)

def get_all_user_contracts(id):
    
    return Contract.query.filter_by(creator_id=id).all()

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