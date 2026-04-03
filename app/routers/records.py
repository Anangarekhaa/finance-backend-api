from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date
from app.database import get_db
from app.models import FinancialRecord, User
from app.schemas import RecordCreate, RecordUpdate, RecordResponse, PaginatedRecords
from app.dependencies import get_current_user, require_role
from app.enums import Role, TransactionType

router = APIRouter(prefix="/records", tags=["records"])



@router.get("/", response_model=PaginatedRecords)
def get_records(
    type: Optional[TransactionType] = Query(None),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    # pagination
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([Role.analyst, Role.admin]))
):
    


    query = db.query(FinancialRecord).join(User, FinancialRecord.created_by == User.id).filter(FinancialRecord.is_deleted == False)

    
    if current_user.role in [Role.analyst, Role.admin]:
        if type:
            query = query.filter(FinancialRecord.type == type)
        if category:
            query = query.filter(FinancialRecord.category == category)
        if start_date:
            query = query.filter(FinancialRecord.date >= start_date)
        if end_date:
            query = query.filter(FinancialRecord.date <= end_date)
        if search:
            query = query.filter(
                User.name.ilike(f"%{search}%") |
                User.email.ilike(f"%{search}%")
            )

    total = query.with_entities(func.count(FinancialRecord.id)).scalar()

    records = (
        query
        .order_by(FinancialRecord.date.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": records
    }



@router.get("/{record_id}", response_model=RecordResponse)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([Role.analyst, Role.admin]))
):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record



@router.post("/", response_model=RecordResponse)
def create_record(
    data: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([Role.admin]))
):
    record = FinancialRecord(**data.model_dump(), created_by=current_user.id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: int,
    data: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([Role.admin]))
):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found or already deleted")

    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record



@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([Role.admin]))
):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found or already deleted")

    record.is_deleted = True
    db.commit()
    return {"detail": "Record deleted"}
