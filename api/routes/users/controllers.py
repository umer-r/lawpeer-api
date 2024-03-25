# Module Imports
from api.database import db
from api.models.user import User, Lawyer, Client
from api.utils.hasher import hash_password

# ----------------------------------------------- #

# -- General User Controller -- #

def create_user(email, username, password, first_name, last_name, dob, country, phone_number, role=None, **kwargs):
    
    # Check for duplicate email or username.
    # NOTE: Split in two by Email & Username.
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        # If user with same email or username already exists, return 409 Conflict
        return None

    hashed_password = hash_password(password=password)
    
    if role == 'lawyer':
        new_user = Lawyer(email=email, username=username, password=hashed_password, first_name=first_name, last_name=last_name, dob=dob, country=country, phone_number=phone_number, **kwargs)
    elif role == 'client':
        new_user = Client(email=email, username=username, password=hashed_password, first_name=first_name, last_name=last_name, dob=dob, country=country, phone_number=phone_number, **kwargs)
    else:
        new_user = User(email=email, username=username, password=hashed_password, first_name=first_name, last_name=last_name, dob=dob, country=country, phone_number=phone_number, **kwargs)
        
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

# -- Lawyers Specific -- #

def get_all_lawyers():
    return User.query.filter_by(role='lawyer').all()

# -- Clients Specific -- #

def get_all_clients():
    return User.query.filter_by(role='client').all()
