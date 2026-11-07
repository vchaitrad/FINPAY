from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.repositories import merchant_repository


def register(db: Session, user, data):
    if merchant_repository.get_by_user(db, user.id):
        raise AppError("Merchant profile already exists for this user")
    merchant = merchant_repository.create(db, user.id, data.business_name, data.category)
    db.commit()
    return merchant


def get_or_404(db: Session, merchant_id: int):
    merchant = merchant_repository.get(db, merchant_id)
    if not merchant:
        raise AppError("Merchant not found", 404)
    return merchant


def my_profile(db: Session, user):
    merchant = merchant_repository.get_by_user(db, user.id)
    if not merchant:
        raise AppError("Create your merchant profile first", 404)
    return merchant


def list_all(db: Session):
    return merchant_repository.list_all(db)
