from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.connection import get_db
from services.bookservice.repository import BookRepository
from services.bookservice.book_logic import BookLogic

router = APIRouter(prefix="/books", tags=["Books"])

class BookCreateRequest(BaseModel):
    isbn: str
    title: str
    author: str
    category: str
    publisher: Optional[str] = ""
    publication_year: Optional[int] = None
    total_copies: int = 1

class BookUpdateRequest(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    total_copies: Optional[int] = None
    status: Optional[str] = None

@router.get("")
def list_books(
    search: Optional[str] = None,
    category: Optional[str] = None,
    available_only: bool = False,
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    repo = BookRepository(db)
    books = repo.get_all(search=search, category=category, available_only=available_only, include_inactive=include_inactive)
    return [
        {
            "book_id": b.book_id,
            "isbn": b.isbn,
            "title": b.title,
            "author": b.author,
            "category": b.category,
            "publisher": b.publisher,
            "publication_year": b.publication_year,
            "total_copies": b.total_copies,
            "available_copies": b.available_copies,
            "status": b.status
        }
        for b in books
    ]

@router.get("/search")
def search_books(
    q: Optional[str] = Query(None, description="Search term for title, author, isbn"),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    repo = BookRepository(db)
    books = repo.get_all(search=q, category=category)
    return [
        {
            "book_id": b.book_id,
            "isbn": b.isbn,
            "title": b.title,
            "author": b.author,
            "category": b.category,
            "publisher": b.publisher,
            "publication_year": b.publication_year,
            "total_copies": b.total_copies,
            "available_copies": b.available_copies,
            "status": b.status
        }
        for b in books
    ]

@router.get("/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db)):
    repo = BookRepository(db)
    book = repo.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {
        "book_id": book.book_id,
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
        "category": book.category,
        "publisher": book.publisher,
        "publication_year": book.publication_year,
        "total_copies": book.total_copies,
        "available_copies": book.available_copies,
        "status": book.status
    }

@router.post("")
def add_book(req: BookCreateRequest, db: Session = Depends(get_db)):
    repo = BookRepository(db)
    logic = BookLogic(repo)
    try:
        book = logic.add_book(req.dict())
        return {
            "book_id": book.book_id,
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "category": book.category,
            "total_copies": book.total_copies,
            "available_copies": book.available_copies,
            "status": book.status,
            "message": "Book added successfully."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{book_id}")
def update_book(book_id: int, req: BookUpdateRequest, db: Session = Depends(get_db)):
    repo = BookRepository(db)
    logic = BookLogic(repo)
    try:
        book = logic.update_book(book_id, req.dict(exclude_unset=True))
        return {
            "book_id": book.book_id,
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "category": book.category,
            "total_copies": book.total_copies,
            "available_copies": book.available_copies,
            "status": book.status,
            "message": "Book updated successfully."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    repo = BookRepository(db)
    logic = BookLogic(repo)
    try:
        return logic.remove_book(book_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

