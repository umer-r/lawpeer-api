"""
    TODO:   1 - CASCADE upon deletion from users.                               - [DONE] -> VIA Controller.
            2 - Remove status or reason field from users.                       - [HALT]
            3 - Move toDict to utils.helper                                     - [DONE]
            4 - Implement functions and fields for average rating of user       - [DONE]
"""

# Lib Imports
from datetime import datetime
from sqlalchemy import inspect
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

# Module Imports:
from api.database import db
from api.utils.helper import to_dict
from api.utils.geo_locator import get_address

# Models Imports:
from .review import Review
from .skill import lawyer_skills

# ----------------------------------------------- #

# SQL Datatype Objects => https://docs.sqlalchemy.org/en/14/core/types.html
class User(db.Model):
    __tablename__ = 'users'
    
    # Auto Generated Fields:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime(timezone=True), default=datetime.now)                            # The Date of the Instance Creation => Created one Time when Instantiation
    updated = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)     # The Date of the Instance Update => Changed with Every Update
    
    # Account Settings:
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_suspended = db.Column(db.Boolean, default=False, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(150))
    reason = db.Column(db.String(150))

    # Input by User Fields:
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    
    # Personal:
    profile_image = db.Column(db.String(255))   # Store image path
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(150)) # User added address
    dob = db.Column(db.Date)
    phone_number = db.Column(db.String(20))
    role = db.Column(db.String(50))  # Role can be 'lawyer' or 'client'
    

    @hybrid_property
    def role_type(self):
        return self.role

    @role_type.expression
    def role_type(cls):
        return cls.role

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': role,
    }
    
    # Location address:
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    country = db.Column(db.String(50))
    city = db.Column(db.String(50))
    postal_code = db.Column(db.Integer)
    geo_address = db.Column(db.Text)
    
    def fill_location_address(self, lat, long):
        try:
            country, city, postal_code, full_address = get_address(lat, long)
            self.latitude = lat
            self.longitude = long
            self.country = country
            self.city = city
            self.geo_address = full_address
            self.postal_code = postal_code
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error occurred while fetching address: {e}")
    
    # Additional fields for average rating & total rating
    total_ratings = db.Column(db.Float, default=0)
    average_rating = db.Column(db.Float, default=0)
    num_reviews = db.Column(db.Integer, default=0)
    
    def update_average_rating(self):
        if self.num_reviews > 0:
            self.average_rating = min(self.total_ratings / self.num_reviews, 5.0)
        else:
            self.average_rating = 0

    def add_review(self, rating):
        self.total_ratings += rating
        self.num_reviews += 1
        self.update_average_rating()
    
    def subtract_review(self, rating):
        self.total_ratings -= rating
        self.num_reviews -= 1
        self.update_average_rating()
    
    def to_dict(self):
        return to_dict(self)

    def __repr__(self):
        return f"<User {self.email}>"

class Lawyer(User):
    __tablename__ = 'lawyers'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    # Additional fields specific to Lawyer
    about = db.Column(db.Text)
    bar_association_id = db.Column(db.String(50))
    experience_years = db.Column(db.Integer)
    
    # Relationship with skills
    skills = db.relationship('Skill', secondary=lawyer_skills, backref=db.backref('lawyers', lazy='dynamic'))
    
    __mapper_args__ = {
        'polymorphic_identity': 'lawyer',
        
        # BUG Fixed: https://stackoverflow.com/questions/2863336/creating-self-referential-tables-with-polymorphism-in-sqlalchemy/2863398#2863398
        'inherit_condition': (id == User.id),
    }

    def __repr__(self):
        return f"<Lawyer {self.email}>"

class Client(User):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    # Additional fields specific to Client
    case_details = db.Column(db.Text)

    # # Review provied relationship
    # reviews = db.relationship('Review', backref='client_association', foreign_keys='Review.client_id')

    __mapper_args__ = {
        'polymorphic_identity': 'client',
        'inherit_condition': (id == User.id),
    }

    def __repr__(self):
        return f"<Client {self.email}>"
      
