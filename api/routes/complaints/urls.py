# Lib Imports:
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# Controllers Imports:
from .controllers import create_new_complaint, get_all_complaints, get_complaint_by_id, get_user_complaints, update_complaint_status, check_client_association_with_contract, get_complaint_by_contract

# Decorators Imports:
from api.decorators.mandatory_keys import check_mandatory
from api.decorators.access_control_decorators import admin_required, user_or_admin_required, client_required

# Module Imports:
from api.utils.status_codes import Status

complaint_routes = Blueprint('complaint_routes', __name__)

@complaint_routes.route('/', methods=['POST'])
@jwt_required()
@check_mandatory(['subject', 'description', 'contract_id', 'lawyer_id'])
@client_required
def create_complaint():
    data = request.get_json()
    
    subject = data.get('subject')
    description = data.get('description')
    contract_id = data.get('contract_id')
    client_id = get_jwt_identity().get('id')
    lawyer_id = data.get('lawyer_id')
    
    check_client = check_client_association_with_contract(client_id, contract_id)
    if check_client:
        
        check_contract = get_complaint_by_contract(contract_id)
        if check_contract:
            return jsonify({'message': 'Complaint for this contract already exists!'}), Status.HTTP_409_CONFLICT
        
        complaint = create_new_complaint(subject, description, contract_id, client_id, lawyer_id)
        if complaint:
            return jsonify({'message': 'Complaint created successfully'}), Status.HTTP_201_CREATED
        else:
            return jsonify({'message': 'Contract does not exist or is not ended'}), Status.HTTP_400_BAD_REQUEST
    else:
        return jsonify({'message': 'Unauthorized Access. User not associated with contract'}), Status.HTTP_401_UNAUTHORIZED

@complaint_routes.route('/', methods=['GET'])
@jwt_required()
@admin_required
def all_complaints():
    complaints = get_all_complaints()
    if complaints:
        return jsonify([complaint.to_dict() for complaint in complaints]), Status.HTTP_200_OK
    return jsonify({'message': 'No Complaints found'}), Status.HTTP_404_NOT_FOUND

@complaint_routes.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_complaint(id):
        
    complaint = get_complaint_by_id(id)
    if complaint:
        return jsonify(complaint.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'message': 'Complaint not found'}), Status.HTTP_404_NOT_FOUND

@complaint_routes.route('/user/<int:id>', methods=['GET'])
@jwt_required()
@user_or_admin_required
def user_complaints(id):
    
    complaints = get_user_complaints(id)
    if complaints:
        return jsonify([complaint.to_dict() for complaint in complaints]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No complaints found'}), Status.HTTP_404_NOT_FOUND

@complaint_routes.route('/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
@check_mandatory(['status'])
def update_complaint(id):
    data = request.get_json()
    admin_id = get_jwt_identity().get('id')
    status = data.get('status')
    details = data.get('details')
    completed = data.get('completed')
    
    complaint = update_complaint_status(id, admin_id, status, details, completed)
    if complaint:
        return jsonify({'message': f'Complaint with id: {id} updated successfully!'}), Status.HTTP_200_OK
    
    return jsonify({'message': 'Complaint not found'}), Status.HTTP_404_NOT_FOUND
