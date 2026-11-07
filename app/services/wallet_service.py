from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.repositories import wallet_repository

MAX_TOPUP = 50000.0


def _wallet(db: Session, user_id: int):
    wallet = wallet_repository.get_by_user(db, user_id)
    if not wallet:
        raise AppError("Wallet not found", 404)
    return wallet


def get_balance(db: Session, user_id: int):
    return {"user_id": user_id, "balance": round(_wallet(db, user_id).balance, 2)}


def topup(db: Session, user_id: int, amount: float):
    if amount <= 0:
        raise AppError("Amount must be positive")
    if amount > MAX_TOPUP:
        raise AppError(f"Maximum top-up per transaction is {MAX_TOPUP:.0f}")
    credit(db, user_id, amount, "TOPUP", "wallet top-up")
    db.commit()
    return get_balance(db, user_id)


# debit / credit do NOT commit: the caller (payment service) commits once so everything is atomic
def debit(db: Session, user_id: int, amount: float, reference: str):
    wallet = _wallet(db, user_id)
    if wallet.balance < amount:
        raise AppError("Insufficient wallet balance")
    wallet.balance = round(wallet.balance - amount, 2)
    wallet_repository.add_ledger(db, user_id, "PAYMENT", -amount, reference)


def credit(db: Session, user_id: int, amount: float, entry_type: str, reference: str):
    wallet = _wallet(db, user_id)
    wallet.balance = round(wallet.balance + amount, 2)
    wallet_repository.add_ledger(db, user_id, entry_type, amount, reference)


def history(db: Session, user_id: int):
    return wallet_repository.ledger_for_user(db, user_id)


def verify_all_wallets(db: Session):
    """Used by reconciliation: balance must equal the sum of that wallet's ledger entries."""
    mismatches = []
    for w in wallet_repository.all_wallets(db):
        expected = round(wallet_repository.ledger_sum(db, w.user_id), 2)
        if abs(expected - w.balance) > 0.01:
            mismatches.append({"user_id": w.user_id, "wallet_balance": w.balance, "ledger_total": expected})
    return mismatches
