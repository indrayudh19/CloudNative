from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Fine, Payment, Issue, Book, User
from services.paymentservice.repository import PaymentRepository
from services.paymentservice.payment_logic import PaymentLogic

router = APIRouter(prefix="/payments", tags=["Payments"])

class PayFineRequest(BaseModel):
    fine_id: int
    user_id: str
    amount: float
    payment_method: Optional[str] = "UPI"

@router.get("/fines/{user_id}")
def get_user_fines(user_id: str, db: Session = Depends(get_db)):
    repo = PaymentRepository(db)
    fines = repo.get_fines_by_user(user_id)
    result = []
    for f in fines:
        iss = db.query(Issue).filter(Issue.issue_id == f.issue_id).first()
        book = db.query(Book).filter(Book.book_id == iss.book_id).first() if iss else None
        result.append({
            "fine_id": f.fine_id,
            "issue_id": f.issue_id,
            "book_title": book.title if book else "Unknown",
            "amount": f.amount,
            "paid_amount": f.paid_amount,
            "outstanding_amount": f.outstanding_amount,
            "status": f.status,
            "created_at": f.created_at.isoformat() if f.created_at else None
        })
    return result

@router.post("/pay")
def pay_fine_endpoint(req: PayFineRequest, db: Session = Depends(get_db)):
    repo = PaymentRepository(db)
    logic = PaymentLogic(db, repo)
    try:
        return logic.pay_fine(req.fine_id, req.user_id, req.amount, req.payment_method)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history/{user_id}")
def get_payment_history(user_id: str, db: Session = Depends(get_db)):
    repo = PaymentRepository(db)
    payments = repo.get_payments_by_user(user_id)
    result = []
    for p in payments:
        result.append({
            "payment_id": p.payment_id,
            "fine_id": p.fine_id,
            "amount": p.amount,
            "payment_method": p.payment_method,
            "payment_date": p.payment_date.isoformat() if p.payment_date else None,
            "status": p.status,
            "transaction_reference": p.transaction_reference
        })
    return result

@router.get("/all")
def get_all_payments(db: Session = Depends(get_db)):
    repo = PaymentRepository(db)
    payments = repo.get_all_payments()
    result = []
    for p in payments:
        user = db.query(User).filter(User.user_id == p.user_id).first()
        result.append({
            "payment_id": p.payment_id,
            "fine_id": p.fine_id,
            "user_id": p.user_id,
            "user_name": user.name if user else "Unknown",
            "amount": p.amount,
            "payment_method": p.payment_method,
            "payment_date": p.payment_date.isoformat() if p.payment_date else None,
            "status": p.status,
            "transaction_reference": p.transaction_reference
        })
    return result

@router.get("/summary")
def get_payment_summary(db: Session = Depends(get_db)):
    repo = PaymentRepository(db)
    fines = repo.get_all_fines()
    total_fines = sum(f.amount for f in fines)
    total_paid = sum(f.paid_amount for f in fines)
    total_outstanding = sum(f.outstanding_amount for f in fines)
    payments_count = len(repo.get_all_payments())

    return {
        "total_fine_amount": total_fines,
        "total_collected": total_paid,
        "total_outstanding": total_outstanding,
        "total_payment_transactions": payments_count
    }

