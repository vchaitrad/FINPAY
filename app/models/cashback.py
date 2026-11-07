from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from app.core.database import Base
from app.core.utils import utcnow


class CashbackRecord(Base):
    __tablename__ = "cashback_records"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    rate = Column(Float, nullable=False)
    created_at = Column(DateTime, default=utcnow, index=True)
