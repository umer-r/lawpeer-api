# controllers.py

from api.database import db
from api.models.user import User

def create_user(email, username, dob, country, phone_number):
    new_user = User(email=email, username=username, dob=dob, country=country, phone_number=phone_number)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_all_users():
    return User.query.all()

def update_user(user_id, email=None, username=None, dob=None, country=None, phone_number=None):
    user = User.query.get(user_id)
    if user:
        if email:
            user.email = email
        if username:
            user.username = username
        if dob:
            user.dob = dob
        if country:
            user.country = country
        if phone_number:
            user.phone_number = phone_number
        db.session.commit()
        return user
    return None

def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return user
    return None
