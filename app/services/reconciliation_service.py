from datetime import datetime
from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.repositories import transaction_repository, cashback_repository, merchant_repository
from app.services import wallet_service


def monthly_report(db: Session, year: int, month: int):
    if not 1 <= month <= 12:
        raise AppError("Month must be between 1 and 12")
    start = datetime(year, month, 1)
    end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

    txns = transaction_repository.list_between(db, start, end)
    cashbacks = cashback_repository.list_between(db, start, end)

    per_merchant = {}
    for t in txns:
        m = per_merchant.setdefault(t.merchant_id, {"merchant_id": t.merchant_id, "transactions": 0,
                                                    "gross_sales": 0.0, "cashback_given": 0.0})
        m["transactions"] += 1
        m["gross_sales"] = round(m["gross_sales"] + t.amount, 2)
        m["cashback_given"] = round(m["cashback_given"] + (t.cashback or 0), 2)
    for m in per_merchant.values():
        merchant = merchant_repository.get(db, m["merchant_id"])
        m["business_name"] = merchant.business_name if merchant else "unknown"
        m["settlement_due"] = round(m["gross_sales"], 2)  # amount to pay the merchant

    total_sales = round(sum(t.amount for t in txns), 2)
    total_cashback = round(sum(c.amount for c in cashbacks), 2)
    mismatches = wallet_service.verify_all_wallets(db)

    return {
        "period": f"{year}-{month:02d}",
        "total_transactions": len(txns),
        "total_sales": total_sales,
        "total_cashback": total_cashback,
        "merchants": list(per_merchant.values()),
        "wallet_mismatches": mismatches,
        "status": "BALANCED" if not mismatches else "MISMATCH_FOUND",
    }
