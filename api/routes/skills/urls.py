"""
    TODO:   1 - Create a endpoint to filter by multiple skill ids                       - [HALT]
            2 - Update the add-skills to handle updation of skills                      - [DONE]
            3 - Find a way to send response from endpoint not from controller           - []
            
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.decorators.mandatory_keys import check_mandatory
from api.decorators.access_control_decorators import lawyer_required, admin_required
from api.utils.status_codes import Status
from api.database import db
from api.models.user import Lawyer
from api.models.skill import Skill

from .controllers import get_all_skills, add_skills_to_lawyer, filter_lawyer_by_skill, get_lawyer_skills, get_skills_of_all_lawyers

skill_routes = Blueprint('skill', __name__)

@skill_routes.route('/', methods=['GET'])
def all_skills():
    skills = get_all_skills()
    if skills:
        return jsonify([skill.to_dict() for skill in skills]), Status.HTTP_200_OK
    
    return jsonify({'error': 'No Skills found!'}), Status.HTTP_404_NOT_FOUND
    
@skill_routes.route('/add-skills', methods=['POST'])
@jwt_required()
@check_mandatory(['skill_ids'])
def skill_to_lawyer():
    data = request.json
    
    skill_ids = data.get('skill_ids')
    lawyer_id = get_jwt_identity().get('id')
    
    response, status_code = add_skills_to_lawyer(lawyer_id=lawyer_id, skill_ids=skill_ids)
    return jsonify(response), status_code    

@skill_routes.route('/filter-by-skill/<int:id>', methods=['GET'])
def get_lawyers_by_skill(id):
    
    lawyers = filter_lawyer_by_skill(id)
    if lawyers:
        return jsonify([lawyer.to_dict() for lawyer in lawyers]), Status.HTTP_200_OK
    
    return jsonify({'error': f'No Lawyers found for particular skill id: {id} OR skill not present!'}), Status.HTTP_404_NOT_FOUND

@skill_routes.route('/lawyer-skills/<int:id>', methods=['GET'])
def lawyer_skills_by_id(id):
    
    lawyer_skills, lawyer_found = get_lawyer_skills(id)
    if lawyer_found:
        if lawyer_skills:
            return jsonify(lawyer_skills), Status.HTTP_200_OK
        else:
            return jsonify({'error': 'Lawyer does not have skills selected'}), Status.HTTP_404_NOT_FOUND
    else:
        return jsonify({'error': 'Lawyer not found'}), Status.HTTP_404_NOT_FOUND

@skill_routes.route('/my-skills', methods=['GET'])
@jwt_required()
def lawyer_skills():
    id = get_jwt_identity().get('id')
    
    lawyer_skills, lawyer_found = get_lawyer_skills(id)
    if lawyer_found:
        if lawyer_skills:
            return jsonify(lawyer_skills), Status.HTTP_200_OK
        else:
            return jsonify({'error': 'Lawyer does not have skills selected'}), Status.HTTP_404_NOT_FOUND
    else:
        return jsonify({'error': 'Lawyer not found'}), Status.HTTP_404_NOT_FOUND

@skill_routes.route('/all-lawyer-skills', methods=['GET'])
def skills_of_lawyers():
    
    lawyers_skills, lawyers_found = get_skills_of_all_lawyers()
    if lawyers_found:
        if lawyers_skills:
            return jsonify(lawyers_skills), Status.HTTP_200_OK
        else:
            return jsonify({'error': 'Lawyers have no selected skills'}), Status.HTTP_404_NOT_FOUND
    else:
        return jsonify({'error': 'No lawyers found'}), Status.HTTP_404_NOT_FOUND

