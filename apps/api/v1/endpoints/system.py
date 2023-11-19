from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import crud
from database.session import get_db
from schemas import system as system_schema
from models import system as system_model
from models import user as user_model


router = APIRouter()


@router.get("/systems")
def read_systems(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    systems, total_count = crud.system.get_multi(db=db, skip=skip, limit=limit)
    return systems, total_count


@router.get("/system/{user_id}", response_model=system_schema.SystemReponse)
def get_systems(user_id: int, db: Session = Depends(get_db)):
    check_obj = crud.get_object_or_404(db=db, model=user_model.User, obj_id=user_id)
    system = crud.system.get_by_user_id(db=db, user_id=user_id)
    return system


@router.put("/system/{system_id}", response_model=system_schema.SystemReponse)
def update_system(
    system_id: int, obj_in: system_schema.SystemUpdate, db: Session = Depends(get_db)
):
    check_obj = crud.get_object_or_404(
        db=db, model=system_model.System, obj_id=system_id
    )
    updated_system = crud.system.update(db=db, db_obj=check_obj, obj_in=obj_in)
    return updated_system


@router.get("/reports", response_model=system_schema.SystemReponse)
def read_reports(
    user_id: int, db: Session = Depends(get_db), skip: int = 0, limit: int = 10
):
    pass


@router.get("/report/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    pass


@router.post("/report")
def create_reports(obj_in: system_schema.ReportCreate, db: Session = Depends(get_db)):
    pass


@router.put("/report/{report_id}")
def update_report(
    report_id: int, obj_in: system_schema.ReportUpdate, db: Session = Depends(get_db)
):
    pass
