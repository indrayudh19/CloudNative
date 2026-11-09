from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import User, Issue, Fine

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> User:
        return self.db.query(User).filter(User.user_id == user_id).first()

    def get_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email.ilike(email)).first()

    def get_all(self, role: str = None, search: str = None):
        query = self.db.query(User)
        if role:
            query = query.filter(User.role == role)
        if search:
            search_str = f"%{search}%"
            query = query.filter((User.name.ilike(search_str)) | (User.user_id.ilike(search_str)) | (User.email.ilike(search_str)))
        return query.order_by(User.created_at.desc()).all()

    def generate_next_member_id(self) -> str:
        # Format: MEM0001, MEM0002...
        members = self.db.query(User.user_id).filter(User.user_id.like("MEM%")).all()
        max_num = 0
        for (uid,) in members:
            num_part = uid[3:]
            if num_part.isdigit():
                max_num = max(max_num, int(num_part))
        next_num = max_num + 1
        return f"MEM{next_num:04d}"

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

