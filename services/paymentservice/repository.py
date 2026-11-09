from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import Fine, Payment, User, Issue

class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_fine_by_id(self, fine_id: int) -> Fine:
        return self.db.query(Fine).filter(Fine.fine_id == fine_id).first()

    def get_fines_by_user(self, user_id: str):
        return self.db.query(Fine).filter(Fine.user_id == user_id).order_by(Fine.created_at.desc()).all()

    def get_payments_by_user(self, user_id: str):
        return self.db.query(Payment).filter(Payment.user_id == user_id).order_by(Payment.payment_date.desc()).all()

    def get_all_payments(self):
        return self.db.query(Payment).order_by(Payment.payment_date.desc()).all()

    def get_all_fines(self):
        return self.db.query(Fine).order_by(Fine.created_at.desc()).all()

    def process_payment(self, payment: Payment, fine: Fine) -> Payment:
        # Atomic transaction
        self.db.add(payment)
        fine.paid_amount += payment.amount
        fine.outstanding_amount = max(0.0, fine.amount - fine.paid_amount)
        if fine.outstanding_amount == 0.0:
            fine.status = "paid"
        else:
            fine.status = "partial"
        self.db.commit()
        self.db.refresh(payment)
        self.db.refresh(fine)
        return payment

