from api.models.transaction import Transaction
from api.models.contract import Contract
from api.database import db

def create_debit_transaction(description, amount, pending):
    
    transaction = Transaction(
        description=description,
        amount=amount,
        pending=pending,
        transaction_mode='debit'
    )
    
    db.session.add(transaction)
    db.session.commit()