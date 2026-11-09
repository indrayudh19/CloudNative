from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User, Book, Issue, Fine, Payment
from services.adminservice.repository import AdminRepository
from services.adminservice.admin_logic import AdminLogic

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
def get_admin_dashboard(db: Session = Depends(get_db)):
    repo = AdminRepository(db)
    logic = AdminLogic(db, repo)
    return logic.get_dashboard_summary()

@router.get("/members")
def get_all_members(db: Session = Depends(get_db)):
    members = db.query(User).filter(User.role == "member").order_by(User.user_id.asc()).all()
    res = []
    for m in members:
        active_issues = db.query(Issue).filter(Issue.user_id == m.user_id, Issue.status == "issued").count()
        unpaid_fines = db.query(Fine).filter(Fine.user_id == m.user_id, Fine.status.in_(["unpaid", "partial"])).all()
        outstanding = sum(f.outstanding_amount for f in unpaid_fines)
        res.append({
            "user_id": m.user_id,
            "name": m.name,
            "email": m.email,
            "phone": m.phone,
            "address": m.address,
            "status": m.status,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "active_issues_count": active_issues,
            "outstanding_fine": outstanding
        })
    return res

@router.get("/books")
def get_admin_books(db: Session = Depends(get_db)):
    books = db.query(Book).order_by(Book.book_id.asc()).all()
    res = []
    for b in books:
        issued_count = b.total_copies - b.available_copies
        res.append({
            "book_id": b.book_id,
            "isbn": b.isbn,
            "title": b.title,
            "author": b.author,
            "category": b.category,
            "publisher": b.publisher,
            "publication_year": b.publication_year,
            "total_copies": b.total_copies,
            "available_copies": b.available_copies,
            "issued_copies": max(0, issued_count),
            "status": b.status
        })
    return res

@router.get("/reports/issues")
def get_issue_reports(db: Session = Depends(get_db)):
    issues = db.query(Issue).order_by(Issue.issue_date.desc()).all()
    res = []
    today = date.today()
    for iss in issues:
        book = db.query(Book).filter(Book.book_id == iss.book_id).first()
        user = db.query(User).filter(User.user_id == iss.user_id).first()
        is_overdue = iss.status == "issued" and iss.due_date < today
        res.append({
            "issue_id": iss.issue_id,
            "user_id": iss.user_id,
            "user_name": user.name if user else "Unknown",
            "book_id": iss.book_id,
            "book_title": book.title if book else "Unknown",
            "issue_date": str(iss.issue_date),
            "due_date": str(iss.due_date),
            "return_date": str(iss.return_date) if iss.return_date else "-",
            "status": "overdue" if is_overdue else iss.status
        })
    return res

@router.get("/reports/payments")
def get_payment_reports(db: Session = Depends(get_db)):
    payments = db.query(Payment).order_by(Payment.payment_date.desc()).all()
    res = []
    for p in payments:
        user = db.query(User).filter(User.user_id == p.user_id).first()
        res.append({
            "payment_id": p.payment_id,
            "user_id": p.user_id,
            "user_name": user.name if user else "Unknown",
            "amount": p.amount,
            "payment_method": p.payment_method,
            "status": p.status,
            "transaction_reference": p.transaction_reference,
            "payment_date": p.payment_date.isoformat() if p.payment_date else None
        })
    return res

@router.get("/reports/overdue")
def get_overdue_reports(db: Session = Depends(get_db)):
    today = date.today()
    overdue_issues = db.query(Issue).filter(Issue.status == "issued", Issue.due_date < today).all()
    res = []
    for iss in overdue_issues:
        book = db.query(Book).filter(Book.book_id == iss.book_id).first()
        user = db.query(User).filter(User.user_id == iss.user_id).first()
        overdue_days = (today - iss.due_date).days
        res.append({
            "issue_id": iss.issue_id,
            "user_id": iss.user_id,
            "user_name": user.name if user else "Unknown",
            "book_id": iss.book_id,
            "book_title": book.title if book else "Unknown",
            "due_date": str(iss.due_date),
            "overdue_days": overdue_days,
            "estimated_fine": overdue_days * 5.0
        })
    return res

@router.get("/audit-logs")
def get_audit_logs(db: Session = Depends(get_db)):
    repo = AdminRepository(db)
    logs = repo.get_audit_logs(limit=50)
    return [
        {
            "log_id": l.log_id,
            "user_id": l.user_id,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None
        }
        for l in logs
    ]

