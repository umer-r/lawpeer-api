# Lib Imports:
from datetime import datetime
from sqlalchemy import inspect

# Module Imports:
from api.database import db
from api.utils.helper import to_dict

# ----------------------------------------------- #

class Admin(db.Model):
    __tablename__ = 'admins'
    
    # Auto Generated Fields:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime(timezone=True), default=datetime.now)                            # The Date of the Instance Creation => Created one Time when Instantiation
    updated = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)     # The Date of the Instance Update => Changed with Every Update
    
    # Input by User Fields:
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    phone_number = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(50))  # Role is 'Admin'

    # How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
    def to_dict(self):
        return to_dict(self)

    def __repr__(self):
        return f"<Admin {self.email}>"
