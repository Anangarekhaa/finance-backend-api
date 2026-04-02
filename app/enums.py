from enum import Enum

class Role(str, Enum):
    viewer = "viewer"
    analyst = "analyst"
    admin = "admin"

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"