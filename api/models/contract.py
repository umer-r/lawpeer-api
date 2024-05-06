# Lib Imports
from datetime import datetime

# Module Imports:
from api.database import db
from api.utils.helper import to_dict
from .user import Client, Lawyer

# ----------------------------------------------- #

class Contract(db.Model):
    __tablename__ = 'contracts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime(timezone=True), default=datetime.now)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    
    # Description:
    creator_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Payment:
    price = db.Column(db.Integer, nullable=False)
    is_paid = db.Column(db.Boolean, default=False, nullable=False)
    
    # Approval:
    is_accepted = db.Column(db.Boolean, default=False, nullable=False)
    accepted_on = db.Column(db.DateTime(timezone=True))
    
    # Ending:
    is_ended = db.Column(db.Boolean, default=False, nullable=False)
    ended_on = db.Column(db.DateTime(timezone=True))
    ended_reason = db.Column(db.Text)

    # Relationships:
    lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'), nullable=False)
    lawyer = db.relationship('Lawyer', backref='contracts')
    
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    client = db.relationship('Client', backref='contracts')
    
    # ForeignKeyConstraint to link contracts and reviews:
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'))
    review = db.relationship('Review', backref='contract', uselist=False)

    def to_dict(self):
        return to_dict(self)

    def __repr__(self):
        return f"<Contract {self.id}>"
