from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=6)
    role: str = "student"  # student | merchant | admin


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class UserOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    email: str
    role: str


class TopupIn(BaseModel):
    amount: float = Field(gt=0)


class BalanceOut(BaseModel):
    user_id: int
    balance: float


class LedgerOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    entry_type: str
    amount: float
    reference: Optional[str]
    created_at: datetime


class MerchantIn(BaseModel):
    business_name: str
    category: str = "general"


class MerchantOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    user_id: int
    business_name: str
    category: str


class PaymentIn(BaseModel):
    merchant_id: int
    amount: float = Field(gt=0)


class TransactionOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    student_id: int
    merchant_id: int
    amount: float
    cashback: float
    status: str
    created_at: datetime


class CashbackOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    transaction_id: int
    amount: float
    rate: float
    created_at: datetime
