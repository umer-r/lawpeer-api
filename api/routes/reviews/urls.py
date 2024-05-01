"""
    TODO:   1 - Implement JWT access control                                                - []
            2 - Implement average rating for get_all_lawyer route via controller            - 
"""

# Lib Imports:
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

# Controller Imports:
from .controllers import create_new_review, get_all_reviews, get_review_by_id, delete_review_by_id, get_client_reviews, get_lawyer_reviews

# Module Imports:
from api.utils.status_codes import Status
from api.utils.decorators import check_mandatory

# ----------------------------------------------- #

review_routes = Blueprint('review', __name__, url_prefix='/reviews')

# CREATE: Create a new review
@review_routes.route('/', methods=['POST'])
@jwt_required()
@check_mandatory(['rating', 'review_text', 'lawyer_id'])
def create_review():
    data = request.json
    
    rating = data.get('rating')
    review_text = data.get('review_text')
    client_id = data.get('client_id')
    lawyer_id = data.get('lawyer_id')
    
    create_new_review(client_id=client_id, lawyer_id=lawyer_id, rating=rating, review_text=review_text)
    
    return jsonify({'message': 'Review created successfully'}), Status.HTTP_201_CREATED

# READ-1: Retrieve all reviews
@review_routes.route('/', methods=['GET'])
def get_all():
    
    reviews = get_all_reviews()
    if reviews:
        return jsonify([review.to_dict() for review in reviews]), Status.HTTP_200_OK
    
    return jsonify({'message': 'No reviews found'}), Status.HTTP_404_NOT_FOUND

# READ-2: Retrieve a specific review by its ID
@review_routes.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    
    review = get_review_by_id(review_id)
    if review:
        return jsonify(review.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'message': 'Review not found'}), Status.HTTP_404_NOT_FOUND

# DELETE: delete review by id
@review_routes.route('/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    
    deleted_review = delete_review_by_id(review_id)
    if deleted_review:
        return jsonify({'message': f'Review with id {id} deleted successfully!'}), Status.HTTP_204_NO_CONTENT
    
    return jsonify({'message': 'Review not found'}), Status.HTTP_404_NOT_FOUND

@review_routes.route('/client/<int:client_id>', methods=['GET'])
def get_all_client(id):
    reviews = get_client_reviews(id)
    if reviews:
        return jsonify(reviews.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'message': 'No reviews found!'}), Status.HTTP_404_NOT_FOUND

@review_routes.route('/lawyer/<int:lawyer_id>', methods=['GET'])
def get_all_lawyer(id):
    reviews = get_lawyer_reviews(id)
    if reviews:
        return jsonify(reviews.to_dict()), Status.HTTP_200_OK
    
    return jsonify({'message': 'No reviews found!'}), Status.HTTP_404_NOT_FOUND
