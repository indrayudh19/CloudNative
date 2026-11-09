from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Issue, Book, Fine
from services.userservice.repository import UserRepository
from services.userservice.user_logic import UserLogic
from utils.helpers import validate_email

router = APIRouter(prefix="/users", tags=["Users"])

class UserRegisterRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = ""
    address: Optional[str] = ""

class UserLoginRequest(BaseModel):
    user_id: str
    password: Optional[str] = ""

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None

@router.post("/register")
def register_member(req: UserRegisterRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    logic = UserLogic(repo)
    try:
        res = logic.register_member(req.name, req.email, req.phone, req.address)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login_user(req: UserLoginRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    logic = UserLogic(repo)
    try:
        res = logic.login(req.user_id, req.password)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
def list_users(role: Optional[str] = None, search: Optional[str] = None, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    users = repo.get_all(role=role, search=search)
    return [
        {
            "user_id": u.user_id,
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "address": u.address,
            "role": u.role,
            "status": u.status,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]

@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    logic = UserLogic(repo)
    try:
        return logic.get_user_profile(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{user_id}")
def update_user(user_id: str, req: UserUpdateRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    logic = UserLogic(repo)
    try:
        return logic.update_user(user_id, req.dict(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}/history")
def get_user_history(user_id: str, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    issues = (
        db.query(Issue)
        .filter(Issue.user_id == user_id)
        .order_by(Issue.issue_date.desc())
        .all()
    )

    history = []
    for iss in issues:
        book = db.query(Book).filter(Book.book_id == iss.book_id).first()
        fine = db.query(Fine).filter(Fine.issue_id == iss.issue_id).first()
        history.append({
            "issue_id": iss.issue_id,
            "book_id": iss.book_id,
            "book_title": book.title if book else "Unknown",
            "author": book.author if book else "Unknown",
            "isbn": book.isbn if book else "-",
            "issue_date": str(iss.issue_date),
            "due_date": str(iss.due_date),
            "return_date": str(iss.return_date) if iss.return_date else None,
            "status": iss.status,
            "fine_amount": fine.amount if fine else 0.0,
            "fine_status": fine.status if fine else "none"
        })
    return history
