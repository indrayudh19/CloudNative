from datetime import date
from sqlalchemy.orm import Session
from database.models import Issue, Book, User, Fine

class IssueRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, issue_id: int) -> Issue:
        return self.db.query(Issue).filter(Issue.issue_id == issue_id).first()

    def get_all(self, status: str = None, user_id: str = None):
        query = self.db.query(Issue)
        if status:
            query = query.filter(Issue.status == status)
        if user_id:
            query = query.filter(Issue.user_id == user_id)
        return query.order_by(Issue.issue_date.desc()).all()

    def get_active_count_by_user(self, user_id: str) -> int:
        return self.db.query(Issue).filter(Issue.user_id == user_id, Issue.status == "issued").count()

    def get_overdue_issues(self):
        today = date.today()
        return self.db.query(Issue).filter(
            Issue.status == "issued",
            Issue.due_date < today
        ).all()

    def create_issue(self, issue: Issue, book: Book) -> Issue:
        # Atomic transaction: add issue and decrement available copies
        self.db.add(issue)
        book.available_copies -= 1
        self.db.commit()
        self.db.refresh(issue)
        return issue

    def return_issue(self, issue: Issue, book: Book, fine: Fine = None):
        # Atomic transaction: update issue status, return date, increment available copies, add fine if applicable
        issue.status = "returned"
        book.available_copies += 1
        if fine:
            self.db.add(fine)
        self.db.commit()
        self.db.refresh(issue)
        return issue

