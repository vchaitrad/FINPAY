# FinPay - Student Wallet, Payments & Cashback (Layered Architecture)

Python + FastAPI + SQLAlchemy (SQLite). Architecture: **Router -> Service -> Repository -> Model -> Database**

## Run
```
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/ for the web app (screens). API docs: /docs

## Test
```
pytest -q
```

## Layers (what goes where)
| Layer | Folder | Job |
|---|---|---|
| Router / API | `app/routers` | HTTP only: receive request, check role, call service |
| Service | `app/services` | All business rules (validation, cashback, atomic payment, reconciliation) |
| Repository | `app/repositories` | Only database queries, no rules |
| Model | `app/models` | Table definitions (User, Wallet, WalletLedger, Merchant, Transaction, CashbackRecord) |
| Database | `finpay.db` | SQLite |

Dependencies only go downward. Routers never touch repositories; repositories never contain business rules.

## Payment flow (example)
`POST /payments` -> payment_router -> payment_service.pay -> wallet_service.debit + cashback_service.apply -> repositories -> DB.
Debit, transaction and cashback are committed together; if anything fails, everything rolls back.

## Roles
- student: wallet top-up, pay merchants, history, cashback history
- merchant: create merchant profile, see received payments
- admin: monthly reconciliation report

## Cashback rules (edit in `app/services/cashback_service.py`)
2% cashback, only if payment >= 100, capped at 50 per payment.

## Monthly reconciliation
`GET /reconciliation/monthly?year=2026&month=11` (admin) gives total sales, total cashback, per-merchant settlement due,
and checks every wallet balance equals the sum of its ledger entries (status BALANCED / MISMATCH_FOUND).

## Quick demo order
1. register student, merchant, admin (`/auth/register`, role field) and login
2. merchant: `POST /merchants`
3. student: `POST /wallet/topup`, `GET /merchants`, `POST /payments`
4. admin: `GET /reconciliation/monthly`
