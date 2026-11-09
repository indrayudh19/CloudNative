from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import User, Book, Issue, Fine, Payment, AuditLog

class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_metrics(self) -> dict:
        today = date.today()

        total_members = self.db.query(User).filter(User.role == "member").count()
        active_members = self.db.query(User).filter(User.role == "member", User.status == "active").count()

        total_unique_books = self.db.query(Book).filter(Book.status == "active").count()
        total_copies = self.db.query(func.sum(Book.total_copies)).filter(Book.status == "active").scalar() or 0
        available_copies = self.db.query(func.sum(Book.available_copies)).filter(Book.status == "active").scalar() or 0

        total_issued_books = self.db.query(Issue).filter(Issue.status == "issued").count()
        total_overdue = self.db.query(Issue).filter(Issue.status == "issued", Issue.due_date < today).count()

        fines_sum = self.db.query(func.sum(Fine.amount)).scalar() or 0.0
        fines_collected = self.db.query(func.sum(Fine.paid_amount)).scalar() or 0.0
        fines_outstanding = self.db.query(func.sum(Fine.outstanding_amount)).scalar() or 0.0

        return {
            "total_registered_members": total_members,
            "active_members": active_members,
            "total_unique_books": total_unique_books,
            "total_book_copies": total_copies,
            "total_available_copies": available_copies,
            "total_currently_issued": total_issued_books,
            "total_overdue_books": total_overdue,
            "total_fines_generated": fines_sum,
            "total_fines_collected": fines_collected,
            "total_fines_outstanding": fines_outstanding,
        }

    def get_audit_logs(self, limit: int = 50):
        return (
            self.db.query(AuditLog)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )

