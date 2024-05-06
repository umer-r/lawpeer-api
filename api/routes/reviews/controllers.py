"""
    TODO:   1 - Implement error handling in create_new_review().                    - [DONE]
            2 - Implement addition and deletion of average rating:                  - [DONE]
                - update_user_average_rating_add -> create_new_review               - [DONE]
                - update_user_average_rating_sub -> delete_review_by_id             - [DONE]
"""

# Modules Imports:
from api.database import db

# Models Imports:
from api.models.review import Review
from api.models.contract import Contract
from api.models.user import Client, Lawyer

# Utils:
from api.utils.status_codes import Status

# ----------------------------------------------- #

def create_new_review(contract_id, client_id, lawyer_id, rating, review_text):
    contract = Contract.query.get(contract_id)
    if contract:
        if contract.review_id:
            return {'error': f'Unable to create review for contract id: {contract_id}. A review already exists!'}, Status.HTTP_409_CONFLICT
        if contract.client_id != client_id:
            return {'error': f'Unable to create review for contract id: {contract_id}. Client not associated with contract!'}, Status.HTTP_401_UNAUTHORIZED
        if contract.is_ended:
            new_review = Review( rating=rating, review_text=review_text, client_id=client_id, lawyer_id=lawyer_id)
            db.session.add(new_review)
            db.session.commit()
            
            # Update average rating for client & lawyer:
            update_user_average_rating_add(client_id, rating)
            update_user_average_rating_add(lawyer_id, rating)
            
            # Update contract's review_id with the ID of the created review for one - one relationship
            contract.review_id = new_review.id
            db.session.commit()
                
            return {'message': 'Review created successfully!'}, Status.HTTP_201_CREATED
        else:
            return {'error': f'Unable to create review for contract id: {contract_id}. The contract is not ended yet!'}, Status.HTTP_400_BAD_REQUEST
    
    return {'error': f'Unable to create review for contract id: {contract_id}. The contract does not exists!'}, Status.HTTP_404_NOT_FOUND

def update_user_average_rating_add(user_id, rating):
    user = None
    if Client.query.get(user_id):
        user = Client.query.get(user_id)
    elif Lawyer.query.get(user_id):
        user = Lawyer.query.get(user_id)

    if user:
        user.add_review(rating)
        db.session.commit()

def get_all_reviews():
    return Review.query.all()

def get_review_by_id(id):
    return Review.query.get(id)

def delete_review_by_id(id):
    review = Review.query.get(id)
    
    if review:
    
        update_user_average_rating_sub(review.client_id, review.rating)
        update_user_average_rating_sub(review.lawyer_id, review.rating)
        
        db.session.delete(review)
        db.session.commit()
        return review
    
    return None

def update_user_average_rating_sub(user_id, rating):
    user = None
    if Client.query.get(user_id):
        user = Client.query.get(user_id)
    elif Lawyer.query.get(user_id):
        user = Lawyer.query.get(user_id)

    if user:
        user.subtract_review(rating)
        db.session.commit()

def get_client_reviews(id):
    reviews = Review.query.filter_by(client_id=id).all()
    return reviews

def get_lawyer_reviews(id):
    reviews = Review.query.filter_by(lawyer_id=id).all()
    return reviews
