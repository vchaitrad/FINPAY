from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
import os

from app.core.database import Base, engine
from app.core.errors import AppError
import app.models  # noqa: F401  (registers tables)
from app.routers import (auth_router, wallet_router, merchant_router,
                         payment_router, cashback_router, reconciliation_router)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinPay - Student Wallet & Payments (Layered Architecture)")


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


for r in (auth_router, wallet_router, merchant_router, payment_router, cashback_router, reconciliation_router):
    app.include_router(r.router)


@app.get("/", include_in_schema=False)
def ui():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))


@app.get("/health", tags=["Health"])
def health():
    return {"app": "FinPay", "architecture": "Layered (Router -> Service -> Repository -> Model -> Database)", "docs": "/docs"}
