from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import crud
from database.session import get_db
from schemas import alarm as alarm_schemas
from models import user as user_models

router = APIRouter()


@router.get("/alarms/{user_id}", response_model=alarm_schemas.AlarmListResponse)
def get_all_alarms_by_user(
    user_id: int, db: Session = Depends(get_db), skip: int = 0, limit: int = 10
):
    """
    user_id의 알람 목록
    """
    check_user = crud.get_object_or_404(db=db, model=user_models.User, obj_id=user_id)

    alarms, total_count = crud.alarm.get_multi_with_user_id(
        db=db, user_id=user_id, skip=skip, limit=limit
    )
    return {"alarms": alarms, "total_count": total_count}
