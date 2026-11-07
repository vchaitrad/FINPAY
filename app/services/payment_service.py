from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.repositories import transaction_repository
from app.services import wallet_service, merchant_service, cashback_service


def pay(db: Session, student, merchant_id: int, amount: float):
    if amount <= 0:
        raise AppError("Amount must be positive")
    merchant = merchant_service.get_or_404(db, merchant_id)

    txn = transaction_repository.create(db, student.id, merchant.id, amount)
    try:
        wallet_service.debit(db, student.id, amount, f"payment to {merchant.business_name} (txn {txn.id})")
        txn.cashback = cashback_service.apply(db, student.id, txn.id, amount)
        txn.status = "SUCCESS"
        db.commit()  # debit + transaction + cashback saved together, or nothing at all
    except Exception:
        db.rollback()
        raise
    db.refresh(txn)
    return txn


def student_history(db: Session, student_id: int):
    return transaction_repository.list_by_student(db, student_id)


def merchant_history(db: Session, user):
    merchant = merchant_service.my_profile(db, user)
    return transaction_repository.list_by_merchant(db, merchant.id)
