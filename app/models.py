from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, ForeignKey, Enum as SAEnum, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums import Role, TransactionType
from sqlalchemy import CheckConstraint


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    email         = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role          = Column(SAEnum(Role), nullable=False, default=Role.viewer)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    records       = relationship("FinancialRecord", back_populates="creator")


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id         = Column(Integer, primary_key=True, index=True)
    amount     = Column(Numeric(10, 2), nullable=False)
    type       = Column(SAEnum(TransactionType), nullable=False)
    category   = Column(String, nullable=False, index=True)
    date       = Column(Date, nullable=False, index=True)
    notes      = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator    = relationship("User", back_populates="records")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_amount_positive"),
        Index("ix_records_type_category", "type", "category"),
        Index("ix_records_date_deleted", "date", "is_deleted"),
    )