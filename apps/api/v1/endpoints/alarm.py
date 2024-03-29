from typing import Any, List, Optional, Dict, Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import crud
from core.security import oauth2_scheme
from database.session import get_db
from schemas import alarm as alarm_schemas
from models import user as user_models
from models import alarm as alarm_models

router = APIRouter()


@router.get("/alarms/{user_id}", response_model=alarm_schemas.AlarmListResponse)
def get_all_alarms_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    """
    user_id의 알람 목록
    """
    check_user = crud.get_object_or_404(db=db, model=user_models.User, obj_id=user_id)

    alarms, total_count = crud.alarm.get_multi_with_user_id(
        db=db, user_id=user_id, skip=skip, limit=limit
    )
    return {"alarms": alarms, "total_count": total_count}


@router.put("/alarm/{alarm_id}", response_model=alarm_schemas.AlarmReponse)
def read_alarm(
    alarm_id: int,
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    """
    알람 읽음 처리
    """
    check_alarm = crud.get_object_or_404(
        db=db, model=alarm_models.Alarm, obj_id=alarm_id
    )

    alarm_obj = crud.alarm.read_alarm(db=db, alarm_id=alarm_id)
    return alarm_obj
