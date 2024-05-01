# Lib Imports
from datetime import datetime

# Module Imports:
from api.database import db
from api.utils.helper import to_dict

# ----------------------------------------------- #

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime(timezone=True), default=datetime.now)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    
    # Rating given by client to lawyer (Assuming rating ranges from 1 to 5)
    rating = db.Column(db.Integer, nullable=False)
    
    # Review text provided by client
    review_text = db.Column(db.Text)

    # Relationships
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    client = db.relationship('Client', backref='reviews_association')
    
    lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'), nullable=False)
    lawyer = db.relationship('Lawyer', backref='reviews_association')
    
    def to_dict(self):
        return to_dict(self)

    def __repr__(self):
        return f"<Review {self.id}>"
