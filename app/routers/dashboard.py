from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Literal
from app.database import get_db
from app.models import FinancialRecord
from app.dependencies import get_current_user, require_role
from app.enums import Role, TransactionType
from app.models import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])



@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    base = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    total_income = base.filter(
        FinancialRecord.type == TransactionType.income
    ).with_entities(func.sum(FinancialRecord.amount)).scalar() or 0

    total_expenses = base.filter(
        FinancialRecord.type == TransactionType.expense
    ).with_entities(func.sum(FinancialRecord.amount)).scalar() or 0

    net_balance = total_income - total_expenses

    category_breakdown = (
        base
        .with_entities(FinancialRecord.category, func.sum(FinancialRecord.amount))
        .group_by(FinancialRecord.category)
        .all()
    )

    recent_activity = (
        base
        .order_by(FinancialRecord.date.desc())
        .limit(5)
        .all()
    )

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": net_balance,
        "category_breakdown": {cat: float(amt) for cat, amt in category_breakdown},
        "recent_activity": [
            {
                "id": r.id,
                "amount": float(r.amount),
                "type": r.type,
                "category": r.category,
                "date": r.date
            }
            for r in recent_activity
        ]
    }



@router.get("/trends")
def get_trends(
    period: Literal["monthly", "weekly"] = Query("monthly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([Role.analyst, Role.admin]))
):
    base = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    if period == "monthly":
        trunc = func.date_trunc("month", FinancialRecord.date)
    else:
        trunc = func.date_trunc("week", FinancialRecord.date)

    income_data = (
        base
        .filter(FinancialRecord.type == TransactionType.income)
        .with_entities(trunc.label("period"), func.sum(FinancialRecord.amount).label("total"))
        .group_by(trunc)
        .order_by(trunc)
        .all()
    )

    expense_data = (
        base
        .filter(FinancialRecord.type == TransactionType.expense)
        .with_entities(trunc.label("period"), func.sum(FinancialRecord.amount).label("total"))
        .group_by(trunc)
        .order_by(trunc)
        .all()
    )

   
    income_map = {str(r.period): float(r.total) for r in income_data}
    expense_map = {str(r.period): float(r.total) for r in expense_data}
    all_periods = sorted(set(income_map) | set(expense_map))

    trends = [
        {
            "period": p,
            "income": income_map.get(p, 0),
            "expenses": expense_map.get(p, 0),
            "net": income_map.get(p, 0) - expense_map.get(p, 0)
        }
        for p in all_periods
    ]

    return {"period": period, "data": trends}