from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.core.database import Base
from app.core.utils import utcnow


class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)


class WalletLedger(Base):
    """Every balance change is recorded here (TOPUP +, PAYMENT -, CASHBACK +). Used by reconciliation."""
    __tablename__ = "wallet_ledger"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    entry_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)  # signed
    reference = Column(String)
    created_at = Column(DateTime, default=utcnow)
