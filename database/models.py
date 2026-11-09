from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Date,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.orm import relationship
from database.connection import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    role = Column(String, nullable=False, default="member")  # member / admin
    status = Column(String, nullable=False, default="active")  # active / inactive
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    issues = relationship("Issue", back_populates="user", foreign_keys="Issue.user_id")
    fines = relationship("Fine", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    isbn = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    publisher = Column(String, nullable=True)
    publication_year = Column(Integer, nullable=True)
    total_copies = Column(Integer, nullable=False, default=1)
    available_copies = Column(Integer, nullable=False, default=1)
    status = Column(String, nullable=False, default="active")  # active / inactive

    __table_args__ = (
        CheckConstraint("available_copies >= 0", name="check_available_non_negative"),
        CheckConstraint("available_copies <= total_copies", name="check_available_lte_total"),
    )

    # Relationships
    issues = relationship("Issue", back_populates="book")


class Issue(Base):
    __tablename__ = "issues"

    issue_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False, index=True)
    issued_by = Column(String, ForeignKey("users.user_id"), nullable=False)
    issue_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)
    status = Column(String, nullable=False, default="issued")  # issued / returned

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="issues")
    issuer = relationship("User", foreign_keys=[issued_by])
    book = relationship("Book", back_populates="issues")
    fine = relationship("Fine", back_populates="issue", uselist=False)


class Fine(Base):
    __tablename__ = "fines"

    fine_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.issue_id"), nullable=False, unique=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    amount = Column(Float, nullable=False, default=0.0)
    paid_amount = Column(Float, nullable=False, default=0.0)
    outstanding_amount = Column(Float, nullable=False, default=0.0)
    status = Column(String, nullable=False, default="unpaid")  # unpaid / partial / paid
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("paid_amount >= 0", name="check_paid_non_negative"),
        CheckConstraint("paid_amount <= amount", name="check_paid_lte_amount"),
        CheckConstraint("outstanding_amount >= 0", name="check_outstanding_non_negative"),
    )

    # Relationships
    issue = relationship("Issue", back_populates="fine")
    user = relationship("User", back_populates="fines")
    payments = relationship("Payment", back_populates="fine")


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    fine_id = Column(Integer, ForeignKey("fines.fine_id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    payment_method = Column(String, nullable=False, default="UPI")  # Cash / UPI / Card
    status = Column(String, nullable=False, default="successful")  # successful / failed
    transaction_reference = Column(String, unique=True, nullable=False, index=True)

    # Relationships
    fine = relationship("Fine", back_populates="payments")
    user = relationship("User", back_populates="payments")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=True, index=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)  # Book / User / Issue / Payment
    entity_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

