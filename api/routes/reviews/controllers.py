from api.models.review import Review
from api.models.contract import Contract
from api.database import db


def create_new_review(contract_id, client_id, lawyer_id, rating, review_text):
    contract = Contract.query.get(contract_id)
    if contract:
        if contract.is_ended:
            new_review = Review( rating=rating, review_text=review_text, client_id=client_id, lawyer_id=lawyer_id)
            db.session.add(new_review)
            db.session.commit()
            return new_review
    return None

def get_all_reviews():
    return Review.query.all()

def get_review_by_id(id):
    return Review.query.get(id)

def delete_review_by_id(id):
    review = Review.query.get(id)
    if review:
        db.session.delete(review)
        db.session.commit()
        return review
    return None

def get_client_reviews(id):
    reviews = Review.query.filter_by(client_id=id).all()
    return reviews

def get_lawyer_reviews(id):
    reviews = Review.query.filter_by(lawyer_id=id).all()
    return reviews
