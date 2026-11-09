from database.models import User
from database.connection import SessionLocal

def authenticate_user(user_id: str, password: str = ""):
    """
    Dummy authentication mechanism per specification:
    Checks if user_id exists and status is active. Password is accepted without verification.
    """
    if not user_id:
        return None
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id.strip()).first()
        if user and user.status == "active":
            return {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "status": user.status
            }
        return None
    finally:
        db.close()

