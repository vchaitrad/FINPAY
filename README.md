# 💳 FinPay – Student Wallet, Payments & Cashback

FinPay is a campus payment application where **students** top up a wallet and pay **merchants** (canteen, bookstore, etc.), earn **cashback** on payments, and an **admin** runs a **monthly reconciliation** report.

Built with **Python + FastAPI + SQLAlchemy (SQLite)** using **Layered Architecture**, with a simple web UI served by the same server.

---

## Table of Contents
1. [Features](#features)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Database Design](#database-design)
6. [Roles & Permissions](#roles--permissions)
7. [Business Rules](#business-rules)
8. [Payment Flow](#payment-flow)
9. [Monthly Reconciliation](#monthly-reconciliation)
10. [API Reference](#api-reference)
11. [Web Screens](#web-screens)
12. [How to Run](#how-to-run)
13. [Demo Walkthrough](#demo-walkthrough)
14. [Testing](#testing)
15. [Configuration](#configuration)
16. [Error Handling](#error-handling)
17. [Limitations & Future Work](#limitations--future-work)

---

## Features

| Area | What it does |
|---|---|
| **Authentication** | Register and login with email + password, JWT tokens, role-based access (student / merchant / admin) |
| **Student wallet** | Every student gets a wallet automatically. Top up, check balance, view full wallet history |
| **Payment processing** | Student pays a merchant. Amount and balance are validated, wallet is debited, transaction is stored |
| **Cashback calculation** | Cashback is calculated on every eligible payment and credited back to the student's wallet |
| **Merchant management** | Merchant accounts create a business profile, students see the list of merchants, merchants see payments received |
| **Monthly reconciliation** | Admin report with total sales, total cashback, per-merchant settlement and a wallet-vs-ledger consistency check |
| **Web UI** | Login/register page plus separate dashboards for student, merchant and admin |

---

## Architecture

FinPay uses **Layered Architecture**. The application is divided into layers, and each layer has one responsibility. A request flows **downward only**:

```
Client (browser / Swagger)
        ↓
Router        →  receives the HTTP request, checks the user's role
        ↓
Service       →  all business rules (validation, cashback, reconciliation)
        ↓
Repository    →  only database queries, no business rules
        ↓
Model         →  table definitions (data structure)
        ↓
Database      →  SQLite (finpay.db)
```

### What each layer does

| Layer | Folder | Responsibility | Must NOT |
|---|---|---|---|
| **Router / API** | `app/routers` | Accept requests, validate input shape, check role, call a service, return the response | contain business rules or touch the database |
| **Service / Business Logic** | `app/services` | Business rules: payment validation, cashback, atomic commit, reconciliation | write SQL or know about HTTP |
| **Repository / Data Access** | `app/repositories` | Create, read and query records | contain business rules or commit transactions |
| **Model / Data** | `app/models` | Define tables and columns | contain logic |
| **Database** | `finpay.db` | Stores the data | – |

### Dependency rules followed
- Routers call **services only**, never repositories.
- Services call **repositories** (and other services at the same level, e.g. payment → wallet / cashback).
- Repositories use **models** only and hold **no business rules**.
- Services control the **commit**, so one payment is saved atomically.

### Why Layered for FinPay
- Money handling needs strong consistency. A payment (debit + transaction + cashback) must succeed or fail as one unit, which is simple inside one application and one database.
- Business rules like cashback live in **one place** (`cashback_service.py`). A rule change touches only the service layer.
- It is easy to know where any new code belongs.
- Simple to build, run and demo compared with microservices or event-driven designs.

### Other architectures considered
Monolithic, MVC, Modular Monolith, Microservices and Event-Driven were considered. Layered was chosen because FinPay is mainly a REST API (so MVC's View layer doesn't map directly), and microservices/event-driven add distributed-system complexity that isn't needed for this scope.

### Limitation of this approach
Layering only works while the dependency rules are respected. If routers start calling repositories directly, or services start containing queries, responsibilities get mixed again.

---

## Tech Stack

| Part | Technology |
|---|---|
| Language | Python 3.10+ |
| Web framework | FastAPI |
| Server | Uvicorn |
| ORM | SQLAlchemy |
| Database | SQLite |
| Auth | JWT (PyJWT), passwords hashed with PBKDF2-SHA256 + salt |
| Frontend | Plain HTML, CSS and JavaScript (single page, served by FastAPI) |
| Testing | pytest + FastAPI TestClient |

---

## Project Structure

```
finpay/
├── app/
│   ├── main.py                     # app entry point, registers routers, serves the UI
│   ├── schemas.py                  # request/response models (Pydantic)
│   ├── core/
│   │   ├── database.py             # engine, session, Base
│   │   ├── security.py             # password hashing, JWT, role checks
│   │   ├── errors.py               # AppError (business errors)
│   │   └── utils.py                # helpers
│   ├── routers/                    # LAYER 1 – API
│   │   ├── auth_router.py
│   │   ├── wallet_router.py
│   │   ├── merchant_router.py
│   │   ├── payment_router.py
│   │   ├── cashback_router.py
│   │   └── reconciliation_router.py
│   ├── services/                   # LAYER 2 – business logic
│   │   ├── auth_service.py
│   │   ├── wallet_service.py
│   │   ├── merchant_service.py
│   │   ├── payment_service.py
│   │   ├── cashback_service.py
│   │   └── reconciliation_service.py
│   ├── repositories/               # LAYER 3 – data access
│   │   ├── user_repository.py
│   │   ├── wallet_repository.py
│   │   ├── merchant_repository.py
│   │   ├── transaction_repository.py
│   │   └── cashback_repository.py
│   ├── models/                     # LAYER 4 – data models
│   │   ├── user.py
│   │   ├── wallet.py               # Wallet + WalletLedger
│   │   ├── merchant.py
│   │   ├── transaction.py
│   │   └── cashback.py
│   └── static/
│       └── index.html              # web UI
├── tests/
│   └── test_flow.py                # end-to-end tests
├── requirements.txt
└── README.md
```

---

## Database Design

| Table | Key columns | Purpose |
|---|---|---|
| `users` | id, name, email (unique), password_hash, role, created_at | All accounts (student / merchant / admin) |
| `wallets` | id, user_id (unique), balance | One wallet per student |
| `wallet_ledger` | id, user_id, entry_type, amount (signed), reference, created_at | Every balance change: `TOPUP` (+), `PAYMENT` (−), `CASHBACK` (+) |
| `merchants` | id, user_id (unique), business_name, category | Merchant profile for a merchant account |
| `transactions` | id, student_id, merchant_id, amount, cashback, status, created_at | Each payment (`PENDING` → `SUCCESS`) |
| `cashback_records` | id, student_id, transaction_id (unique), amount, rate, created_at | Cashback given per transaction |

Relationships: a student has one wallet and many ledger entries and transactions. A merchant account has one merchant profile that receives many transactions. Each successful eligible transaction has one cashback record.

The `wallet_ledger` table is what makes reconciliation possible: a wallet's balance must equal the sum of its ledger entries.

---

## Roles & Permissions

| Action | Student | Merchant | Admin |
|---|:---:|:---:|:---:|
| Register / login | ✅ | ✅ | ✅ |
| Top up, view balance and wallet history | ✅ | – | – |
| Pay a merchant, view own payments | ✅ | – | – |
| View cashback history | ✅ | – | – |
| Create merchant profile, view payments received | – | ✅ | – |
| View list of merchants and cashback rules | ✅ | ✅ | ✅ |
| Monthly reconciliation report | – | – | ✅ |

---

## Business Rules

**Wallet**
- A wallet is created automatically when a student registers.
- Top-up amount must be greater than 0, with a maximum of **₹50,000 per top-up**.
- A payment is rejected if the balance is lower than the amount.

**Cashback** (edit the constants in `app/services/cashback_service.py`)

| Rule | Value |
|---|---|
| Cashback rate | **2%** of the payment |
| Minimum payment to earn cashback | **₹100** |
| Maximum cashback per payment | **₹50** |

Examples: ₹500 payment → ₹10 cashback. ₹50 payment → ₹0 (below minimum). ₹5000 payment → ₹50 (capped, not ₹100).

**Accounts**
- Email must be unique. Password must be at least 6 characters.
- A merchant account can create only one merchant profile.

---

## Payment Flow

`POST /payments` for ₹500 to a merchant:

```
payment_router      receives request, confirms the user is a student
   ↓
payment_service     validates amount, checks merchant exists, creates a PENDING transaction
   ↓
wallet_service      checks balance and debits the wallet, adds a PAYMENT ledger entry
   ↓
cashback_service    calculates cashback, credits the wallet, adds a CASHBACK ledger entry
   ↓
repositories        save transaction, ledger entries, cashback record
   ↓
payment_service     marks the transaction SUCCESS and commits once
```

**Atomic:** the debit, transaction and cashback are committed together. If any step fails (for example insufficient balance), everything is rolled back and nothing is saved.

---

## Monthly Reconciliation

Admin-only report for one month. It returns:
- **Total transactions, total sales and total cashback** for the month
- **Per-merchant settlement:** number of transactions, gross sales, cashback given and the **settlement due** (the amount to pay that merchant)
- **Wallet consistency check:** for every wallet, the balance is compared with the sum of its ledger entries
- **Status:** `BALANCED` if every wallet matches, otherwise `MISMATCH_FOUND` with the list of mismatching wallets

---

## API Reference

Interactive docs: **`/docs`** (Swagger). Use **Authorize** and paste the token from `/auth/login`.

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST | `/auth/register` | public | Create an account |
| POST | `/auth/login` | public | Returns a JWT access token |
| GET | `/auth/me` | any | Current user |
| GET | `/wallet/balance` | student | Wallet balance |
| POST | `/wallet/topup` | student | Add money to the wallet |
| GET | `/wallet/history` | student | Ledger entries (topups, payments, cashback) |
| POST | `/merchants` | merchant | Create merchant profile |
| GET | `/merchants` | any | List all merchants |
| GET | `/merchants/me` | merchant | Own merchant profile |
| POST | `/payments` | student | Pay a merchant |
| GET | `/payments/history` | student | Own payments |
| GET | `/payments/received` | merchant | Payments received by the merchant |
| GET | `/cashback/rules` | any | Current cashback rules |
| GET | `/cashback/history` | student | Cashback earned |
| GET | `/reconciliation/monthly?year=&month=` | admin | Monthly report |
| GET | `/health` | public | Health check |

### Sample requests

Register:
```json
POST /auth/register
{"name": "Chaitra", "email": "student@kle.edu", "password": "secret123", "role": "student"}
```

Login response:
```json
{"access_token": "<jwt>", "token_type": "bearer", "role": "student"}
```

Top up:
```json
POST /wallet/topup
{"amount": 1000}
```

Pay a merchant:
```json
POST /payments
{"merchant_id": 1, "amount": 500}
```
Response:
```json
{"id": 1, "student_id": 1, "merchant_id": 1, "amount": 500.0, "cashback": 10.0, "status": "SUCCESS", "created_at": "..."}
```

---

## Web Screens

Open the root URL in a browser. The page changes based on who is logged in.

| Screen | Contents |
|---|---|
| **Login / Register** | Two tabs. Register lets you choose Student, Merchant or Admin |
| **Student dashboard** | Wallet balance and cashback rules, add money, pay a merchant (dropdown + amount), my payments with cashback, wallet history |
| **Merchant dashboard** | Create business profile (first time), then total received, payment count and payments received table |
| **Admin dashboard** | Pick year and month, summary cards (period, sales, cashback, wallet check badge), per-merchant settlement table |

---

## How to Run

### 1. Requirements
Python 3.10 or newer.

### 2. Install
```bash
cd finpay
pip install -r requirements.txt
```

### 3. Start the server
```bash
python -m uvicorn app.main:app --reload
```
To use a different port (for example if 8000 is busy):
```bash
python -m uvicorn app.main:app --reload --port 8001
```

### 4. Open
| What | URL (port 8000) |
|---|---|
| Web app | http://127.0.0.1:8000/ |
| API docs (Swagger) | http://127.0.0.1:8000/docs |

The database file `finpay.db` is created automatically on first run. Delete it to start fresh.

---

## Demo Walkthrough

1. **Merchant:** open the app → Register → role **Merchant** → create the business profile (e.g. "KLE Canteen", category food).
2. **Student:** Logout → Register → role **Student** → add ₹1000 → pay the merchant ₹500 → cashback of ₹10 is added → balance becomes ₹510.
3. **Try a failure:** pay more than the balance and see the "Insufficient wallet balance" message (nothing is saved).
4. **Admin:** Logout → Register → role **Admin** → open the monthly report → total sales ₹500, cashback ₹10, status **BALANCED**.
5. **Merchant again:** log in as the merchant to see the payment under "Payments received".

Use **Logout** to switch between users.

---

## Testing

```bash
python -m pytest -q
```

The end-to-end test uses a temporary database and checks: registration and login for all three roles, merchant profile creation, top-up, payment with 2% cashback, no cashback below ₹100, rejection of an over-balance payment (balance unchanged), role protection (a student cannot open the admin report), the monthly report values with `BALANCED` status, and that the web UI is served.

---

## Configuration

| Environment variable | Default | Purpose |
|---|---|---|
| `FINPAY_DB` | `sqlite:///./finpay.db` | Database connection URL |
| `FINPAY_SECRET` | built-in development key | Secret used to sign JWT tokens. **Change it outside development** |

PowerShell example:
```powershell
$env:FINPAY_SECRET = "my-long-random-secret"
python -m uvicorn app.main:app --reload --port 8001
```

---

## Error Handling

Business errors are raised in the service layer as `AppError` and returned as JSON like `{"detail": "message"}`.

| Status | Meaning | Example |
|---|---|---|
| 400 | Business rule failed | Insufficient wallet balance, email already registered |
| 401 | Not logged in / bad token or credentials | Invalid email or password |
| 403 | Role not allowed | A student calling the admin report |
| 404 | Not found | Merchant or wallet not found |
| 422 | Invalid request body | Negative amount, missing field |

---

## Limitations & Future Work

- **Admin sign-up is open** so the demo is easy to run. In production, admin accounts would be created only by an existing admin.
- **Money uses floating-point rounding to 2 decimals.** A production system would use `Decimal` or store amounts in paise.
- **Settlement due** is calculated from gross sales. Merchant wallets, payouts and fees are not modelled.
- **SQLite** is used for simplicity. For production, switch to PostgreSQL (change `FINPAY_DB`).
- Possible additions: refunds, transaction PDF statements, pagination, rate limiting, password reset.


