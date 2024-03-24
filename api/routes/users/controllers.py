from api.database import db
from api.models.user import User, Lawyer, Client

def create_user(username, role=None, **kwargs):
    if role == 'lawyer':
        new_user = Lawyer(username=username, role='lawyer', **kwargs)
    elif role == 'client':
        new_user = Client(username=username, role='client', **kwargs)
    else:
        new_user = User(username=username, role='nan' **kwargs)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def create_user(email, username, dob, country, phone_number, role=None, **kwargs):
    if role == 'lawyer':
        new_user = Lawyer(email=email, username=username, dob=dob, country=country, phone_number=phone_number, **kwargs)
    elif role == 'client':
        new_user = Client(email=email, username=username, dob=dob, country=country, phone_number=phone_number, **kwargs)
    else:
        new_user = User(email=email, username=username, dob=dob, country=country, phone_number=phone_number, **kwargs)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_all_users():
    return User.query.all()

def update_user(user_id, email=None, username=None, dob=None, country=None, phone_number=None, **kwargs):
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
        # If the user has a role-specific attributes, update them
        for key, value in kwargs.items():
            setattr(user, key, value)
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
