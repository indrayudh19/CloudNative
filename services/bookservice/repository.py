from sqlalchemy.orm import Session
from database.models import Book, Issue

class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, book_id: int) -> Book:
        return self.db.query(Book).filter(Book.book_id == book_id).first()

    def get_by_isbn(self, isbn: str) -> Book:
        return self.db.query(Book).filter(Book.isbn == isbn.strip()).first()

    def get_all(self, search: str = None, category: str = None, available_only: bool = False, include_inactive: bool = False):
        query = self.db.query(Book)
        if not include_inactive:
            query = query.filter(Book.status == "active")
        if search:
            s = f"%{search}%"
            query = query.filter((Book.title.ilike(s)) | (Book.author.ilike(s)) | (Book.isbn.ilike(s)))
        if category:
            query = query.filter(Book.category.ilike(category))
        if available_only:
            query = query.filter(Book.available_copies > 0)
        return query.order_by(Book.title.asc()).all()

    def has_active_issues(self, book_id: int) -> bool:
        count = self.db.query(Issue).filter(Issue.book_id == book_id, Issue.status == "issued").count()
        return count > 0

    def create(self, book: Book) -> Book:
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def update(self, book: Book) -> Book:
        self.db.commit()
        self.db.refresh(book)
        return book

