# Lib Imports
from datetime import datetime

# Module Imports:
from api.database import db
from api.utils.helper import to_dict

class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime(timezone=True), default=datetime.now)
    updated = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    
    # Description:
    creator_id = db.Column(db.Integer)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Admin related:
    status = db.Column(db.Text)
    details = db.Column(db.Text)
    
    # End:
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)
    resolved_on = db.Column(db.DateTime(timezone=True))
        
    # Relationships:
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    contract = db.relationship('Contract', backref='complaints')
    
    lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'))
    lawyer = db.relationship('Lawyer', backref='complaints')
    
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    client = db.relationship('Client', backref='complaints')
    
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    admin = db.relationship('Admin', backref='complaints')

    def to_dict(self):
        return to_dict(self)

    def __repr__(self):
        return f"<Complaint {self.id}>"
