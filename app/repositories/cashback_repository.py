from sqlalchemy.orm import Session
from app.models import CashbackRecord


def create(db: Session, student_id, transaction_id, amount, rate):
    rec = CashbackRecord(student_id=student_id, transaction_id=transaction_id, amount=amount, rate=rate)
    db.add(rec)
    db.flush()
    return rec


def list_by_student(db: Session, student_id: int):
    return (db.query(CashbackRecord).filter(CashbackRecord.student_id == student_id)
            .order_by(CashbackRecord.id.desc()).all())


def list_between(db: Session, start, end):
    return (db.query(CashbackRecord)
            .filter(CashbackRecord.created_at >= start, CashbackRecord.created_at < end).all())
