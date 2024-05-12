from api.models.transaction import Transaction
from api.models.contract import Contract
from api.database import db

def create_debit_transaction(description, amount, contract_id):
    
    transaction = Transaction(
        description=description,
        amount=amount,
        pending=False,
        transaction_mode='debit',
        contract_id=contract_id
    )
    
    db.session.add(transaction)
    db.session.commit()
    