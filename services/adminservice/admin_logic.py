from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import Issue, Book, Payment, Fine
from services.adminservice.repository import AdminRepository

class AdminLogic:
    def __init__(self, db: Session, repo: AdminRepository):
        self.db = db
        self.repo = repo

    def get_dashboard_summary(self) -> dict:
        metrics = self.repo.get_dashboard_metrics()

        # Top borrowed books
        top_books_query = (
            self.db.query(Book.title, func.count(Issue.issue_id).label("borrow_count"))
            .join(Issue, Book.book_id == Issue.book_id)
            .group_by(Book.book_id)
            .order_by(func.count(Issue.issue_id).desc())
            .limit(5)
            .all()
        )
        top_books = [{"title": t, "count": c} for t, c in top_books_query]

        # Issues over time (by date)
        issues_timeline = (
            self.db.query(Issue.issue_date, func.count(Issue.issue_id))
            .group_by(Issue.issue_date)
            .order_by(Issue.issue_date.asc())
            .all()
        )
        timeline = [{"date": str(d), "count": c} for d, c in issues_timeline]

        metrics["top_borrowed_books"] = top_books
        metrics["issues_timeline"] = timeline
        return metrics

