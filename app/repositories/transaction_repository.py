from sqlalchemy.orm import Session
from app.models import Transaction


def create(db: Session, student_id, merchant_id, amount):
    txn = Transaction(student_id=student_id, merchant_id=merchant_id, amount=amount, status="PENDING")
    db.add(txn)
    db.flush()
    return txn


def list_by_student(db: Session, student_id: int):
    return (db.query(Transaction).filter(Transaction.student_id == student_id)
            .order_by(Transaction.id.desc()).all())


def list_by_merchant(db: Session, merchant_id: int):
    return (db.query(Transaction).filter(Transaction.merchant_id == merchant_id)
            .order_by(Transaction.id.desc()).all())


def list_between(db: Session, start, end):
    return (db.query(Transaction)
            .filter(Transaction.created_at >= start, Transaction.created_at < end,
                    Transaction.status == "SUCCESS").all())
