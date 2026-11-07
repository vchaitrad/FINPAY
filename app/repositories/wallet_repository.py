from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Wallet, WalletLedger


def create_wallet(db: Session, user_id: int):
    wallet = Wallet(user_id=user_id, balance=0.0)
    db.add(wallet)
    db.flush()
    return wallet


def get_by_user(db: Session, user_id: int):
    return db.query(Wallet).filter(Wallet.user_id == user_id).first()


def all_wallets(db: Session):
    return db.query(Wallet).all()


def add_ledger(db: Session, user_id, entry_type, amount, reference=None):
    entry = WalletLedger(user_id=user_id, entry_type=entry_type, amount=amount, reference=reference)
    db.add(entry)
    db.flush()
    return entry


def ledger_for_user(db: Session, user_id: int):
    return (db.query(WalletLedger).filter(WalletLedger.user_id == user_id)
            .order_by(WalletLedger.id.desc()).all())


def ledger_sum(db: Session, user_id: int) -> float:
    total = db.query(func.coalesce(func.sum(WalletLedger.amount), 0.0)).filter(
        WalletLedger.user_id == user_id).scalar()
    return float(total)
