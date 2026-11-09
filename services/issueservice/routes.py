from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Book, User, Fine
from services.issueservice.repository import IssueRepository
from services.issueservice.issue_logic import IssueLogic

router = APIRouter(prefix="/issues", tags=["Issues"])

class IssueBookRequest(BaseModel):
    user_id: str
    book_id: int
    issued_by: Optional[str] = "ADMIN001"

class ReturnBookRequest(BaseModel):
    issue_id: int
    return_date: Optional[date] = None

@router.post("/issue-book")
def issue_book_endpoint(req: IssueBookRequest, db: Session = Depends(get_db)):
    repo = IssueRepository(db)
    logic = IssueLogic(db, repo)
    try:
        iss = logic.issue_book(req.user_id, req.book_id, req.issued_by)
        book = db.query(Book).filter(Book.book_id == iss.book_id).first()
        return {
            "issue_id": iss.issue_id,
            "user_id": iss.user_id,
            "book_id": iss.book_id,
            "book_title": book.title if book else "",
            "issue_date": str(iss.issue_date),
            "due_date": str(iss.due_date),
            "status": iss.status,
            "message": "Book issued successfully."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/return-book")
def return_book_endpoint(req: ReturnBookRequest, db: Session = Depends(get_db)):
    repo = IssueRepository(db)
    logic = IssueLogic(db, repo)
    try:
        res = logic.return_book(req.issue_id, req.return_date)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
def list_issues(status: Optional[str] = None, user_id: Optional[str] = None, db: Session = Depends(get_db)):
    repo = IssueRepository(db)
    issues = repo.get_all(status=status, user_id=user_id)
    today = date.today()
    result = []
    for iss in issues:
        book = db.query(Book).filter(Book.book_id == iss.book_id).first()
        user = db.query(User).filter(User.user_id == iss.user_id).first()
        fine = db.query(Fine).filter(Fine.issue_id == iss.issue_id).first()
        is_overdue = iss.status == "issued" and iss.due_date < today
        result.append({
            "issue_id": iss.issue_id,
            "user_id": iss.user_id,
            "user_name": user.name if user else "Unknown",
            "book_id": iss.book_id,
            "book_title": book.title if book else "Unknown",
            "author": book.author if book else "Unknown",
            "issued_by": iss.issued_by,
            "issue_date": str(iss.issue_date),
            "due_date": str(iss.due_date),
            "return_date": str(iss.return_date) if iss.return_date else None,
            "status": "overdue" if is_overdue else iss.status,
            "fine_amount": fine.amount if fine else 0.0,
            "fine_outstanding": fine.outstanding_amount if fine else 0.0,
            "fine_status": fine.status if fine else "none"
        })
    return result

@router.get("/overdue")
def get_overdue_issues(db: Session = Depends(get_db)):
    repo = IssueRepository(db)
    issues = repo.get_overdue_issues()
    today = date.today()
    result = []
    for iss in issues:
        book = db.query(Book).filter(Book.book_id == iss.book_id).first()
        user = db.query(User).filter(User.user_id == iss.user_id).first()
        overdue_days = (today - iss.due_date).days
        result.append({
            "issue_id": iss.issue_id,
            "user_id": iss.user_id,
            "user_name": user.name if user else "Unknown",
            "book_id": iss.book_id,
            "book_title": book.title if book else "Unknown",
            "issue_date": str(iss.issue_date),
            "due_date": str(iss.due_date),
            "overdue_days": overdue_days,
            "estimated_fine": overdue_days * 5.0
        })
    return result

@router.get("/member/{user_id}")
def get_member_issues(user_id: str, db: Session = Depends(get_db)):
    repo = IssueRepository(db)
    issues = repo.get_all(user_id=user_id)
    today = date.today()
    result = []
    for iss in issues:
        book = db.query(Book).filter(Book.book_id == iss.book_id).first()
        fine = db.query(Fine).filter(Fine.issue_id == iss.issue_id).first()
        is_overdue = iss.status == "issued" and iss.due_date < today
        result.append({
            "issue_id": iss.issue_id,
            "book_id": iss.book_id,
            "book_title": book.title if book else "Unknown",
            "author": book.author if book else "Unknown",
            "issue_date": str(iss.issue_date),
            "due_date": str(iss.due_date),
            "return_date": str(iss.return_date) if iss.return_date else None,
            "status": "overdue" if is_overdue else iss.status,
            "fine_amount": fine.amount if fine else 0.0,
            "fine_outstanding": fine.outstanding_amount if fine else 0.0
        })
    return result

@router.get("/{issue_id}")
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    repo = IssueRepository(db)
    iss = repo.get_by_id(issue_id)
    if not iss:
        raise HTTPException(status_code=404, detail="Issue record not found")
    book = db.query(Book).filter(Book.book_id == iss.book_id).first()
    user = db.query(User).filter(User.user_id == iss.user_id).first()
    fine = db.query(Fine).filter(Fine.issue_id == iss.issue_id).first()
    return {
        "issue_id": iss.issue_id,
        "user_id": iss.user_id,
        "user_name": user.name if user else "Unknown",
        "book_id": iss.book_id,
        "book_title": book.title if book else "Unknown",
        "author": book.author if book else "Unknown",
        "issued_by": iss.issued_by,
        "issue_date": str(iss.issue_date),
        "due_date": str(iss.due_date),
        "return_date": str(iss.return_date) if iss.return_date else None,
        "status": iss.status,
        "fine": {
            "fine_id": fine.fine_id,
            "amount": fine.amount,
            "paid_amount": fine.paid_amount,
            "outstanding_amount": fine.outstanding_amount,
            "status": fine.status
        } if fine else None
    }

