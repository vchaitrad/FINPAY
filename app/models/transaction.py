from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.core.database import Base
from app.core.utils import utcnow


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    cashback = Column(Float, default=0.0)
    status = Column(String, default="PENDING")  # PENDING | SUCCESS
    created_at = Column(DateTime, default=utcnow, index=True)
