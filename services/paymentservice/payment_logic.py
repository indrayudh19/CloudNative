from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Fine, Payment, AuditLog
from services.paymentservice.repository import PaymentRepository
from utils.helpers import generate_transaction_ref

class PaymentLogic:
    def __init__(self, db: Session, repo: PaymentRepository):
        self.db = db
        self.repo = repo

    def pay_fine(self, fine_id: int, user_id: str, amount: float, payment_method: str = "UPI") -> dict:
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        fine = self.repo.get_fine_by_id(fine_id)
        if not fine:
            raise ValueError(f"Fine record #{fine_id} not found.")

        if fine.user_id != user_id:
            raise ValueError("Access denied: You can only pay your own fines.")

        if fine.outstanding_amount <= 0:
            raise ValueError("This fine has already been fully paid.")

        if amount > fine.outstanding_amount:
            raise ValueError(
                f"Payment amount (₹{amount:.2f}) cannot exceed outstanding fine balance (₹{fine.outstanding_amount:.2f})."
            )

        txn_ref = generate_transaction_ref("PAY")
        payment = Payment(
            fine_id=fine.fine_id,
            user_id=user_id,
            amount=amount,
            payment_date=datetime.utcnow(),
            payment_method=payment_method,
            status="successful",
            transaction_reference=txn_ref
        )

        completed_payment = self.repo.process_payment(payment, fine)

        # Audit log
        log = AuditLog(
            user_id=user_id,
            action=f"Fine payment of ₹{amount:.2f} processed via {payment_method}. Txn: {txn_ref}",
            entity_type="Payment",
            entity_id=str(completed_payment.payment_id),
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()

        return {
            "payment_id": completed_payment.payment_id,
            "fine_id": fine.fine_id,
            "user_id": user_id,
            "amount_paid": amount,
            "remaining_balance": fine.outstanding_amount,
            "fine_status": fine.status,
            "transaction_reference": txn_ref,
            "payment_date": completed_payment.payment_date.isoformat(),
            "message": f"Payment of ₹{amount:.2f} successful! Remaining balance: ₹{fine.outstanding_amount:.2f}"
        }

