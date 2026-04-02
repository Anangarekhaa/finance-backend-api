from pydantic import BaseModel, EmailStr
from app.enums import Role
from decimal import Decimal
from app.enums import TransactionType,Role
from datetime import date, datetime
from typing import Optional
from pydantic import field_validator

# Auth
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# User
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role = Role.viewer

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    is_active: bool

    class Config:
        from_attributes = True


class RecordCreate(BaseModel):
    amount: Decimal
    type: TransactionType
    category: str
    date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator("category")
    @classmethod
    def category_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Category cannot be empty")
        return v.strip()

class RecordUpdate(BaseModel):
    amount: Optional[Decimal] = None
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

class RecordResponse(BaseModel):
    id: int
    amount: Decimal
    type: TransactionType
    category: str
    date: date
    notes: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class PaginatedRecords(BaseModel):
    total: int
    page: int
    limit: int
    data: list[RecordResponse]
