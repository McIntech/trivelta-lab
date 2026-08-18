from app.models import TransactionType, Wallet, Transaction

# Creamos una función para actualizar el saldo de la wallet
def debit(db, wallet_id, amount):

    # select for update sobre el wallet
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).with_for_update().first()
    if not wallet:
        raise ValueError("Wallet not found")

    if wallet.balance < amount:
        raise ValueError("Insufficient balance")

    transaction = Transaction(wallet_id=wallet.id, amount=-amount, type=TransactionType.BET)
    wallet.balance -= amount
    db.add(transaction)
    db.commit()
    return wallet

