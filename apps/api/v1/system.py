from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import crud
from database.session import get_db
from schemas.system import (
    SystemCreate,
    SystemUpdate,
    ReportCreate,
    ReportUpdate,
    NoticeCreate,
    NoticeUpdate,
)

router = APIRouter()


@router.get("/systems")
def read_systems(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    pass


@router.get("/system/{user_id}")
def get_systems(user_id: int, db: Session = Depends(get_db)):
    pass


@router.put("/system/{system_id}")
def update_system(system_id: int, obj_in: SystemUpdate, db: Session = Depends(get_db)):
    pass


@router.get("/reports")
def read_reports(
    user_id: int, db: Session = Depends(get_db), skip: int = 0, limit: int = 10
):
    pass


@router.get("/report/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    pass


@router.post("/report")
def create_reports(obj_in: ReportCreate, db: Session = Depends(get_db)):
    pass


@router.put("/report/{report_id}")
def update_report(report_id: int, obj_in: ReportUpdate, db: Session = Depends(get_db)):
    pass
