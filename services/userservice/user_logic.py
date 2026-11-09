from datetime import datetime
from services.userservice.repository import UserRepository
from database.models import User, Issue, Fine

class UserLogic:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def register_member(self, name: str, email: str, phone: str = None, address: str = None) -> dict:
        if not name or not email:
            raise ValueError("Name and Email are required.")

        existing = self.repo.get_by_email(email)
        if existing:
            raise ValueError(f"Email {email} is already registered.")

        new_id = self.repo.generate_next_member_id()
        user = User(
            user_id=new_id,
            name=name.strip(),
            email=email.strip().lower(),
            phone=phone.strip() if phone else "",
            address=address.strip() if address else "",
            role="member",
            status="active",
            created_at=datetime.utcnow()
        )
        created_user = self.repo.create(user)
        return {
            "user_id": created_user.user_id,
            "name": created_user.name,
            "email": created_user.email,
            "phone": created_user.phone,
            "address": created_user.address,
            "role": created_user.role,
            "status": created_user.status,
            "message": f"Registration successful! Your Member ID is {created_user.user_id}. Use this ID to log in."
        }

    def login(self, user_id: str, password: str = "") -> dict:
        if not user_id:
            raise ValueError("User ID cannot be empty.")
        user = self.repo.get_by_id(user_id.strip())
        if not user:
            raise ValueError("Invalid User ID. Please check your ID or register as a new member.")
        if user.status != "active":
            raise ValueError("User account is deactivated. Please contact the administrator.")
        return {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "status": user.status
        }

    def get_user_profile(self, user_id: str) -> dict:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        return {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "address": user.address,
            "role": user.role,
            "status": user.status,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }

    def update_user(self, user_id: str, update_data: dict) -> dict:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        
        if "name" in update_data and update_data["name"]:
            user.name = update_data["name"]
        if "phone" in update_data:
            user.phone = update_data["phone"]
        if "address" in update_data:
            user.address = update_data["address"]
        if "status" in update_data and update_data["status"] in ["active", "inactive"]:
            user.status = update_data["status"]

        updated = self.repo.update(user)
        return {
            "user_id": updated.user_id,
            "name": updated.name,
            "email": updated.email,
            "phone": updated.phone,
            "address": updated.address,
            "role": updated.role,
            "status": updated.status
        }

