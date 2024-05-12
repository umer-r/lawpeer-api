"""
    Blueprint (urls) File; Contains routes related to reviews management.

    External Libraries:
        - flask
        - flask_jwt_extended

    Function Names:
        - create_review: (JWT)     Create a new review, AC: client_required, MANDATORY: contract_id, rating, review_text, lawyer_id.
        - get_all:                 Retrieve all reviews.
        - get_review:              Retrieve a specific review by its ID.
        - get_all_client:          Retrieve all reviews of a specific client by ID.
        - get_all_lawyer:          Retrieve all reviews of a specific lawyer by ID.
        - delete_review: (JWT)     Delete review by ID.

    TODO:   1 - Implement JWT access control                                                - [DONE]
            2 - Implement average rating for get_all_lawyer route via controller            - [DONE] -> In User Model.
            3 - create_review:
                - Check if contract exists.                                                 - [DONE]
                - Check if contract is ended.                                               - [DONE]
                - Check if a review is already present for a contract.                      - [DONE]
                - Update the contract.review_id field.                                      - [DONE]
"""

# Lib Imports:
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

# Controller Imports:
from .controllers import create_new_review, get_all_reviews, get_review_by_id, delete_review_by_id, get_client_reviews, get_lawyer_reviews

# Decorators Imports:
from api.decorators.mandatory_keys import check_mandatory
from api.decorators.access_control_decorators import client_required

# Module Imports:
from api.utils.status_codes import Status

# ----------------------------------------------- #

review_routes = Blueprint('review', __name__, url_prefix='/reviews')

# CREATE: Create a new review
@review_routes.route('/', methods=['POST'])
@jwt_required()
@check_mandatory(['contract_id', 'rating', 'review_text', 'lawyer_id'])
@client_required
def create_review():
    data = request.json
    
    contract_id = data.get('contract_id')
    rating = data.get('rating')
    review_text = data.get('review_text')
    client_id = get_jwt_identity().get('id')
    lawyer_id = data.get('lawyer_id')
    
    response, status_code = create_new_review(contract_id=contract_id, client_id=client_id, lawyer_id=lawyer_id, rating=rating, review_text=review_text)
    return jsonify(response), status_code

# READ-1: Retrieve all reviews
@review_routes.route('/', methods=['GET'])
def get_all():
    
    reviews = get_all_reviews()
    if reviews:
        return jsonify([review.to_dict() for review in reviews]), Status.HTTP_200_OK
    
    return jsonify({'error': 'No reviews found'}), Status.HTTP_404_NOT_FOUND

# READ-2: Retrieve a specific review by its ID
@review_routes.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    
    review = get_review_by_id(review_id)
    if review:
        return jsonify(review.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'error': 'Review not found'}), Status.HTTP_404_NOT_FOUND

# READ-3: Client specific Reviews
@review_routes.route('/client/<int:id>', methods=['GET'])
def get_all_client(id):
    reviews = get_client_reviews(id)
    if reviews:
        return jsonify([review.to_dict() for review in reviews]), Status.HTTP_200_OK
    
    return jsonify({'error': 'No reviews found!'}), Status.HTTP_404_NOT_FOUND

# READ-4: Lawyer specific Reviews
@review_routes.route('/lawyer/<int:id>', methods=['GET'])
def get_all_lawyer(id):
    reviews = get_lawyer_reviews(id)
    if reviews:
        return jsonify([review.to_dict() for review in reviews]), Status.HTTP_200_OK
    
    return jsonify({'error': 'No reviews found!'}), Status.HTTP_404_NOT_FOUND

# DELETE: delete review by id
@review_routes.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    
    deleted_review = delete_review_by_id(review_id)
    if deleted_review:
        return jsonify({'message': f'Review with id {id} deleted successfully!'}), Status.HTTP_204_NO_CONTENT
    
    return jsonify({'error': 'Review not found'}), Status.HTTP_404_NOT_FOUND
