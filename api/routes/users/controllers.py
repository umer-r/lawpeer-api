"""
    TODO:   1 - Add a Suspended account & Reason controller.                                -
            2 - If admin is de activating an account change the 'status' field in model.    - [HALT]
            3 - Modify create_user to store profile images as paths.                        - [DONE]
            4 - Add a check if ATTRIBUTE/FIELD is already changed 
                (e.g. user already deactivated), send appropriate status code back.         -
            5 - In create_user(), Split in two by Email & Username.                         - 
            6 - Error Handling on update_user()                                             -
"""

# Lib Imports:
from werkzeug.utils import secure_filename
from sqlalchemy import and_, or_, func
import os

# Module Imports:
from api.database import db
from api.models.user import User, Lawyer, Client
from api.models.skill import Skill
from api.utils.hasher import hash_password, verify_password
from api.utils.helper import allowed_file, get_upload_folder, rename_profile_image

# ----------------------------------------------- #

# -- General User Controller -- #

def create_user(email, username, password, first_name, last_name, dob, country, phone_number, address, profile_image=None, role=None, **kwargs):
    
    # Check for duplicate email or username.
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        # If user with same email or username already exists, return 409 Conflict
        return None

    hashed_password = hash_password(password=password)
    
    if role == 'lawyer':
        new_user = Lawyer(email=email, username=username, password=hashed_password, first_name=first_name, last_name=last_name, dob=dob, country=country, phone_number=phone_number, address=address, **kwargs)
    elif role == 'client':
        new_user = Client(email=email, username=username, password=hashed_password, first_name=first_name, last_name=last_name, dob=dob, country=country, phone_number=phone_number, address=address, **kwargs)
    else:
        new_user = User(email=email, username=username, password=hashed_password, first_name=first_name, last_name=last_name, dob=dob, country=country, phone_number=phone_number, address=address, **kwargs)
    
    UPLOAD_FOLDER = get_upload_folder()
    if profile_image:
        filename = secure_filename(rename_profile_image(profile_image))
        if allowed_file(filename):
            profile_image_path = os.path.join(UPLOAD_FOLDER, filename)
            profile_image.save(profile_image_path)
            
            # Refactor if gives a bug:
            new_user.profile_image = os.path.join('/static', filename).replace('\\', '/')
    
    db.session.add(new_user)
    db.session.commit()
    
    return new_user

def get_user_by_id(user_id, is_admin, is_same_user):
    """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User: The user object if found, otherwise None.
    """
    
    user = User.query.get(user_id)
    if is_admin in ['admin', 'super-admin'] or is_same_user:
        return user if user else None
    else:
        if user:
            if user.is_verified and not user.is_suspended and user.is_active:
                return user 
        else:
            return None

def get_all_users():
    return User.query.all()

def update_user(user_id, profile_image=None, email=None,
                username=None, dob=None, country=None, 
                phone_number=None, first_name=None, last_name=None, 
                is_active=None, is_suspended=None, status=None, 
                reason=None, address=None, case_details=None,
                bar_association_id=None, experience_years=None,
                longitude=None, latitude=None,
                **kwargs):

    user = User.query.get(user_id)
    if user:
        # Update profile image if provided
        if profile_image:
            UPLOAD_FOLDER = get_upload_folder()
            filename = secure_filename(rename_profile_image(profile_image))
            if allowed_file(filename):
                profile_image_path = os.path.join(UPLOAD_FOLDER, filename)
                profile_image.save(profile_image_path)
                user.profile_image = os.path.join('/static', filename).replace('\\', '/')
        
        if email:
            if user.email != email:
                user.email = email
                user.is_verified = False
        if username:
            user.username = username
        if dob:
            user.dob = dob
        if country:
            user.country = country
        if phone_number:
            user.phone_number = phone_number
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if is_active is not None:
            user.is_active = is_active
        if is_suspended is not None:
            user.is_suspended = is_suspended
        if status:
            user.status = status
        if reason:
            user.reason = reason
        if address:
            user.address = address

        # If the user has role-specific attributes, update them
        for key, value in kwargs.items():
            setattr(user, key, value)
        
        # Role specific fields:
        ## Update client specific fields
        if case_details and user.role == 'client':
            client = Client.query.filter_by(id=user_id).first()
            if client:
                client.case_details = case_details
                
        ## update location related fields:
        if longitude and latitude:
            try:
                user.fill_location_address(latitude, longitude)
            except Exception as e:
                print(f"Error occurred while updating location: {e}")
                
        ## Update Lawyer specific fields:
        if user.role == 'lawyer':
            lawyer = Lawyer.query.filter_by(id=user_id).first()
            if bar_association_id:
                if lawyer:
                    lawyer.bar_association_id = bar_association_id
            if experience_years:
                if lawyer:
                    lawyer.experience_years = experience_years
        
        db.session.commit()
        return user

    return None

def update_profile_picture(id, profile_image):
    user = User.query.get(id)
    if user:
        # Update profile image if provided
        if profile_image:
            UPLOAD_FOLDER = get_upload_folder()
            filename = secure_filename(rename_profile_image(profile_image))
            if allowed_file(filename):
                profile_image_path = os.path.join(UPLOAD_FOLDER, filename)
                profile_image.save(profile_image_path)
                user.profile_image = os.path.join('/static', filename).replace('\\', '/')
                
                db.session.commit()
                return user
    return None
    
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        if user.role == 'lawyer':
            # Delete from lawyers table
            lawyer = Lawyer.query.filter_by(id=user_id).first()
            if lawyer:
                db.session.delete(lawyer)
        elif user.role == 'client':
            # Delete from clients table
            client = Client.query.filter_by(id=user_id).first()
            if client:
                db.session.delete(client)
        
        # Delete from users table
        db.session.delete(user)
        db.session.commit()
        
        return user
    return None

def self_deactivate_user_account(user_id, reason=None):
    user = User.query.get(user_id)
    if user:
        user.is_active = False
        user.reason = reason
        db.session.commit()
        return user
    return None
    
def self_activate_user_account(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_active = True
        db.session.commit()
        return user
    return None

def change_password(user_id, prev_password, new_password):
    user = User.query.get(user_id)
    if user:
        if verify_password(prev_password, user.password):
            user.password = hash_password(new_password)
            db.session.commit()
            return user
        else:
            return False
    return None

def reset_password(email, new_password):
    user = User.query.filter_by(email=email).first()
    hashed_password = hash_password(password=new_password)
    if user:
        user.password = hashed_password
        db.session.commit()
        return user
    return None

def verify_user_account(email):
    user = User.query.filter_by(email=email).first()
    if user:
        user.is_verified = True
        db.session.commit()
        return user
    return None

def exclude_immature_accounts(users):
    """
        Filter out users based on certain conditions.
        
        Conditions:
            - is_verified must be True
            - is_suspended must be False
            - is_active must be True
    """
    
    filtered_users = []

    for user in users:
        if user.is_verified and not user.is_suspended and user.is_active:
            filtered_users.append(user)
    return filtered_users

# -- Lawyers Specific -- #

def get_all_lawyers(is_admin):
    lawyers = User.query.filter_by(role='lawyer').all()
    if is_admin in ['admin', 'super-admin']:
        return lawyers
    else:
        return exclude_immature_accounts(lawyers)

def filter_lawyer_users(is_admin, city=None, skill_ids=None, above_experience_years=None, above_average_rating=None):
        # Start building the query to filter lawyers
    query = Lawyer.query
    
    # Apply filters based on the provided parameters
    if city:
        city_words = city.split()
        # Construct a pattern with wildcard matching for each word in the city
        city_patterns = [f'%{word}%' for word in city_words]
        # Join the individual patterns with OR to match any part of the city name
        city_pattern = or_(*[func.lower(Lawyer.city).like(func.lower(pattern)) for pattern in city_patterns])
        # Apply the constructed pattern to the query
        query = query.filter(city_pattern)    
    if skill_ids:
        query = query.filter(Lawyer.skills.any(Skill.id.in_(skill_ids)))
    
    if above_experience_years:
        query = query.filter(Lawyer.experience_years >= above_experience_years)
    
    if above_average_rating:
        query = query.filter(Lawyer.average_rating >= above_average_rating)
    
    # Execute the query and fetch filtered lawyers
    filtered_lawyers = query.all()
    if is_admin in ['admin', 'super-admin']:
        return filtered_lawyers
    else:
        excluded_users = exclude_immature_accounts(filtered_lawyers)
        return excluded_users

# -- Clients Specific -- #

def get_all_clients(is_admin):
    clients = User.query.filter_by(role='client').all()
    if is_admin in ['admin', 'super-admin']:
        return clients
    else:
        return exclude_immature_accounts(clients)
    