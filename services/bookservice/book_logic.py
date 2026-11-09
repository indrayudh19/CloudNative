from services.bookservice.repository import BookRepository
from database.models import Book

class BookLogic:
    def __init__(self, repo: BookRepository):
        self.repo = repo

    def add_book(self, data: dict) -> Book:
        isbn = str(data.get("isbn", "")).strip()
        title = data.get("title", "").strip()
        author = data.get("author", "").strip()
        category = data.get("category", "").strip()
        total_copies = int(data.get("total_copies", 1))

        if not isbn or not title or not author or not category:
            raise ValueError("ISBN, Title, Author, and Category are required.")

        if total_copies < 1:
            raise ValueError("Total copies must be at least 1.")

        existing = self.repo.get_by_isbn(isbn)
        if existing:
            raise ValueError(f"Book with ISBN {isbn} already exists.")

        book = Book(
            isbn=isbn,
            title=title,
            author=author,
            category=category,
            publisher=data.get("publisher", "").strip(),
            publication_year=int(data.get("publication_year", 2024)) if data.get("publication_year") else None,
            total_copies=total_copies,
            available_copies=total_copies,
            status="active"
        )
        return self.repo.create(book)

    def update_book(self, book_id: int, data: dict) -> Book:
        book = self.repo.get_by_id(book_id)
        if not book:
            raise ValueError("Book not found.")

        if "title" in data and data["title"]:
            book.title = data["title"].strip()
        if "author" in data and data["author"]:
            book.author = data["author"].strip()
        if "category" in data and data["category"]:
            book.category = data["category"].strip()
        if "publisher" in data:
            book.publisher = data["publisher"].strip()
        if "publication_year" in data and data["publication_year"]:
            book.publication_year = int(data["publication_year"])

        if "total_copies" in data and data["total_copies"] is not None:
            new_total = int(data["total_copies"])
            issued_copies = book.total_copies - book.available_copies
            if new_total < issued_copies:
                raise ValueError(f"Cannot set total copies to {new_total}. {issued_copies} copies are currently issued.")
            diff = new_total - book.total_copies
            book.total_copies = new_total
            book.available_copies = max(0, book.available_copies + diff)

        if "status" in data and data["status"] in ["active", "inactive"]:
            book.status = data["status"]

        return self.repo.update(book)

    def remove_book(self, book_id: int) -> dict:
        book = self.repo.get_by_id(book_id)
        if not book:
            raise ValueError("Book not found.")

        # Prevent deletion of books with active borrowing transactions
        if self.repo.has_active_issues(book_id):
            raise ValueError("Cannot delete or deactivate book with active borrowing transactions.")

        # Soft delete per specification
        book.status = "inactive"
        self.repo.update(book)
        return {"message": f"Book '{book.title}' has been archived and removed from active circulation."}

