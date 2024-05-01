"""
    TODO:   1 - CASCADE upon deletion from users.               - [DONE] -> VIA Controller.
            2 - Remove status or reason field from users.       - [HALT]
            3 - Move toDict to utils.helper                     - [DONE]
"""

# Lib Imports
from datetime import datetime
from sqlalchemy import inspect
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

# Module Imports:
from api.database import db
from api.utils.helper import to_dict

# Models Imports:
from .review import Review

# ----------------------------------------------- #

# SQL Datatype Objects => https://docs.sqlalchemy.org/en/14/core/types.html
class User(db.Model):
    __tablename__ = 'users'
    
    # Auto Generated Fields:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime(timezone=True), default=datetime.now)                            # The Date of the Instance Creation => Created one Time when Instantiation
    updated = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)     # The Date of the Instance Update => Changed with Every Update
    
    # Account Settings:
    is_active = db.Column(db.Boolean, default=False, nullable=False)
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
    address = db.Column(db.String(150))
    dob = db.Column(db.Date)
    country = db.Column(db.String(100))
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

    # How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
    def to_dict(self):
        return to_dict(self)

    def __repr__(self):
        return f"<User {self.email}>"

class Lawyer(User):
    __tablename__ = 'lawyers'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    # Additional fields specific to Lawyer
    bar_association_id = db.Column(db.String(50))
    experience_years = db.Column(db.Integer)
    
    # Review received relationship
    reviews = db.relationship('Review', backref='lawyer_association')
    
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

    # Review provied relationship
    reviews = db.relationship('Review', backref='client_association')

    __mapper_args__ = {
        'polymorphic_identity': 'client',
        'inherit_condition': (id == User.id),
    }

    def __repr__(self):
        return f"<Client {self.email}>"
      
