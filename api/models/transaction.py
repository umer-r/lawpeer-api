from datetime import datetime
from api.database import db
from api.utils.helper import to_dict

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime(timezone=True), default=datetime.now)                            # The Date of the Instance Creation => Created one Time when Instantiation
    updated = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)     # The Date of the Instance Update => Changed with Every Update
    description = db.Column(db.String(255))
    amount = db.Column(db.Integer)
    pending = db.Column(db.Boolean, default=True)
    transaction_mode = db.Column(db.String(50))  # "credit" or "debit"
    
    # Foreign key to associate transaction with contract
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'))
    contract = db.relationship('Contract', backref='transactions')

    def to_dict(self):
        return to_dict(self)

    def __repr__(self):
        return f"<Transaction {self.id}>"
