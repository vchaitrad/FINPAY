from sqlalchemy.orm import Session
from app.repositories import cashback_repository
from app.services import wallet_service

# Cashback rules (assumed - change here if your faculty gave different ones)
RATE = 0.02          # 2% cashback
MIN_AMOUNT = 100.0   # payment must be at least this to earn cashback
MAX_CASHBACK = 50.0  # cap per transaction


def rules():
    return {"rate_percent": RATE * 100, "min_payment": MIN_AMOUNT, "max_cashback_per_payment": MAX_CASHBACK}


def calculate(amount: float) -> float:
    if amount < MIN_AMOUNT:
        return 0.0
    return round(min(amount * RATE, MAX_CASHBACK), 2)


def apply(db: Session, student_id: int, transaction_id: int, amount: float) -> float:
    """Calculate cashback, credit it to the student's wallet and store a record. No commit here."""
    cashback = calculate(amount)
    if cashback > 0:
        wallet_service.credit(db, student_id, cashback, "CASHBACK", f"cashback for txn {transaction_id}")
        cashback_repository.create(db, student_id, transaction_id, cashback, RATE)
    return cashback


def history(db: Session, student_id: int):
    return cashback_repository.list_by_student(db, student_id)
