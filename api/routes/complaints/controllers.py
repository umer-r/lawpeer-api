# Lib Imports:
from datetime import datetime

# Module Imports:
from api.database import db
from api.models.contract import Contract
from api.models.complaint import Complaint

def create_new_complaint(subject, description, contract_id, client_id, lawyer_id, creator_id):
    # Check if the contract exists
    contract = Contract.query.get(contract_id)
    if contract:
        if contract.is_paid:
            complaint = Complaint(subject=subject, description=description, contract_id=contract_id, client_id=client_id, lawyer_id=lawyer_id, creator_id=creator_id, status='In Process')
            db.session.add(complaint)
            db.session.commit()
            return complaint
        else:
            return None
    return None

def check_client_association_with_contract(client_id, contract_id):
    contract = Contract.query.get(contract_id)
    if contract:
        if contract.client_id == client_id:
            return True
    return False

def check_users_association_with_contract(client_id, lawyer_id, contract_id):
    contract = Contract.query.get(contract_id)
    if contract:
        if contract.client_id == client_id and contract.lawyer_id == lawyer_id:
            return True
    return False

def get_all_complaints():
    return Complaint.query.all()

def get_complaint_by_id(id):
    return Complaint.query.get(id)

def get_user_complaints(id):
    return Complaint.query.filter_by(creator_id=id).all()

def check_creator_complaints(id, creator_id):
    # Check if the creator has already submitted a complaint for the contract
    existing_complaint = Complaint.query.filter_by(contract_id=id, creator_id=creator_id).first()
    if existing_complaint:
        return True  # Creator has already submitted a complaint
    
    # # Check if there are already two complaints for the contract
    # complaints_count = Complaint.query.filter_by(contract_id=id).count()
    # return complaints_count >= 2  # Return True if there are already two complaints, False otherwise
    
def update_complaint_status(id, admin_id, status, details=None, completed=None):
    complaint = Complaint.query.get(id)
    if complaint:
        complaint.status = status
        complaint.admin_id = admin_id
        if details:
            complaint.details = details
            
        if completed:
            complaint.is_resolved = True
            complaint.resolved_on = datetime.now()
        
        db.session.commit()
        return complaint
    return None
