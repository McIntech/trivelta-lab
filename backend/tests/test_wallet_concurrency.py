import threading
from app.db import SessionLocal
from app.models import Operator, Player, Wallet, Transaction
from app.wallet import debit

def test_concurrent_debit_does_not_overdraft():
    setup_db = SessionLocal()
    operator = Operator(name="Test Operator")
    setup_db.add(operator)
    setup_db.commit()

    player = Player(name="Test Player", operator_id=operator.id)
    setup_db.add(player)
    setup_db.commit()

    wallet = Wallet(player_id=player.id, balance=100)
    setup_db.add(wallet)
    setup_db.commit()
    wallet_id = wallet.id      # guardamos el id antes de cerrar
    setup_db.close()

    results = []

    def job():
        db = SessionLocal()
        try:
            debit(db, wallet_id, 100)
            results.append("ok")
        except ValueError as e:
            results.append(str(e))
        finally:
            db.close()

    t1 = threading.Thread(target=job)
    t2 = threading.Thread(target=job)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    verify_db = SessionLocal()
    final_wallet = verify_db.query(Wallet).filter(Wallet.id == wallet_id).first()
    tx_count = verify_db.query(Transaction).filter(Transaction.wallet_id == wallet_id).count()


    assert final_wallet.balance == 0
    assert tx_count == 1
    assert results.count("Insufficient balance") == 1

    print(f"Final wallet balance: {final_wallet.balance}")
    print(f"Transaction count: {tx_count}")
    print(f"Results: {results}")
    verify_db.close()