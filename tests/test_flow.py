import os, tempfile
os.environ["FINPAY_DB"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "test.db")

from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def signup_login(name, email, role):
    client.post("/auth/register", json={"name": name, "email": email, "password": "secret123", "role": role})
    token = client.post("/auth/login", json={"email": email, "password": "secret123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_full_flow():
    student = signup_login("Chaitra", "s@kle.edu", "student")
    shop = signup_login("Canteen", "m@kle.edu", "merchant")
    admin = signup_login("Admin", "a@kle.edu", "admin")

    assert client.post("/merchants", json={"business_name": "KLE Canteen"}, headers=shop).status_code == 201
    merchant_id = client.get("/merchants", headers=student).json()[0]["id"]

    assert client.post("/wallet/topup", json={"amount": 1000}, headers=student).json()["balance"] == 1000

    r = client.post("/payments", json={"merchant_id": merchant_id, "amount": 500}, headers=student)
    assert r.status_code == 201 and r.json()["cashback"] == 10.0          # 2% of 500
    assert client.get("/wallet/balance", headers=student).json()["balance"] == 510.0

    r = client.post("/payments", json={"merchant_id": merchant_id, "amount": 50}, headers=student)
    assert r.json()["cashback"] == 0.0                                      # below minimum

    r = client.post("/payments", json={"merchant_id": merchant_id, "amount": 99999}, headers=student)
    assert r.status_code == 400                                             # insufficient balance
    assert client.get("/wallet/balance", headers=student).json()["balance"] == 460.0  # unchanged

    assert client.get("/payments/received", headers=shop).status_code == 200
    assert client.get("/reconciliation/monthly?year=2026&month=1", headers=student).status_code == 403

    now = datetime.utcnow()
    rep = client.get(f"/reconciliation/monthly?year={now.year}&month={now.month}", headers=admin).json()
    assert rep["total_transactions"] == 2 and rep["total_sales"] == 550.0
    assert rep["total_cashback"] == 10.0 and rep["status"] == "BALANCED"


def test_ui_served():
    r = client.get("/")
    assert r.status_code == 200 and "FinPay" in r.text
