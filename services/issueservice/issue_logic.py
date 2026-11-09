from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from config import MAX_BOOKS_PER_MEMBER, LOAN_PERIOD_DAYS, FINE_PER_DAY
from database.models import Issue, Book, User, Fine, AuditLog
from services.issueservice.repository import IssueRepository

class IssueLogic:
    def __init__(self, db: Session, repo: IssueRepository):
        self.db = db
        self.repo = repo

    def issue_book(self, user_id: str, book_id: int, issued_by: str = "ADMIN001") -> Issue:
        # 1. Verify User exists and is active
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError(f"Member with ID '{user_id}' does not exist.")
        if user.status != "active":
            raise ValueError(f"Member {user.name} ({user_id}) is inactive. Cannot issue book.")

        # 2. Check unpaid fines balance
        outstanding_fine = (
            self.db.query(Fine)
            .filter(Fine.user_id == user_id, Fine.status.in_(["unpaid", "partial"]))
            .first()
        )
        if outstanding_fine and outstanding_fine.outstanding_amount > 0:
            raise ValueError(
                f"Member has outstanding unpaid fine of ₹{outstanding_fine.outstanding_amount:.2f}. "
                "Borrowing restricted until settled."
            )

        # 3. Check member borrowing limit
        active_count = self.repo.get_active_count_by_user(user_id)
        if active_count >= MAX_BOOKS_PER_MEMBER:
            raise ValueError(
                f"Member has reached maximum limit of {MAX_BOOKS_PER_MEMBER} active borrowed books."
            )

        # 4. Check book exists, is active, and has available inventory
        book = self.db.query(Book).filter(Book.book_id == book_id).first()
        if not book:
            raise ValueError(f"Book with ID {book_id} not found.")
        if book.status != "active":
            raise ValueError(f"Book '{book.title}' is inactive/archived and cannot be issued.")
        if book.available_copies <= 0:
            raise ValueError(f"No copies available for '{book.title}'. (Available: 0)")

        # 5. Create issue transaction
        issue_date = date.today()
        due_date = issue_date + timedelta(days=LOAN_PERIOD_DAYS)

        new_issue = Issue(
            user_id=user_id,
            book_id=book_id,
            issued_by=issued_by,
            issue_date=issue_date,
            due_date=due_date,
            status="issued"
        )

        created_issue = self.repo.create_issue(new_issue, book)

        # Record audit log
        log = AuditLog(
            user_id=issued_by,
            action=f"Issued book '{book.title}' (ID: {book.book_id}) to member {user.name} ({user.user_id})",
            entity_type="Issue",
            entity_id=str(created_issue.issue_id),
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()

        return created_issue

    def return_book(self, issue_id: int, return_date_input: date = None) -> dict:
        issue = self.repo.get_by_id(issue_id)
        if not issue:
            raise ValueError(f"Issue record with ID {issue_id} not found.")
        if issue.status == "returned":
            raise ValueError("This book has already been returned.")

        book = self.db.query(Book).filter(Book.book_id == issue.book_id).first()
        if not book:
            raise ValueError("Associated book record not found.")

        actual_return_date = return_date_input or date.today()
        issue.return_date = actual_return_date

        # Overdue fine calculation
        overdue_days = (actual_return_date - issue.due_date).days
        fine_record = None
        fine_amount = 0.0

        if overdue_days > 0:
            fine_amount = overdue_days * FINE_PER_DAY
            # Check if fine record already generated (e.g. during overdue batch)
            existing_fine = self.db.query(Fine).filter(Fine.issue_id == issue.issue_id).first()
            if existing_fine:
                existing_fine.amount = fine_amount
                existing_fine.outstanding_amount = max(0.0, fine_amount - existing_fine.paid_amount)
                if existing_fine.outstanding_amount == 0.0 and existing_fine.paid_amount > 0:
                    existing_fine.status = "paid"
                elif existing_fine.paid_amount > 0:
                    existing_fine.status = "partial"
                fine_record = None
            else:
                fine_record = Fine(
                    issue_id=issue.issue_id,
                    user_id=issue.user_id,
                    amount=fine_amount,
                    paid_amount=0.0,
                    outstanding_amount=fine_amount,
                    status="unpaid",
                    created_at=datetime.utcnow()
                )

        self.repo.return_issue(issue, book, fine_record)

        # Record audit log
        log = AuditLog(
            user_id=issue.issued_by or "ADMIN001",
            action=f"Returned book '{book.title}' for issue #{issue.issue_id}. Overdue: {max(0, overdue_days)} days, Fine: ₹{fine_amount:.2f}",
            entity_type="Issue",
            entity_id=str(issue.issue_id),
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()

        return {
            "issue_id": issue.issue_id,
            "book_title": book.title,
            "return_date": str(actual_return_date),
            "overdue_days": max(0, overdue_days),
            "fine_amount": fine_amount,
            "status": "returned",
            "message": f"Book '{book.title}' returned successfully." + (f" Overdue fine: ₹{fine_amount:.2f}" if fine_amount > 0 else "")
        }

