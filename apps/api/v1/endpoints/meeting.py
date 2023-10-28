from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

import crud
from database.session import get_db
from schemas.meeting import MeetingResponse, MeetingCreateUpdate

router = APIRouter()

@router.post("/meeting/create", response_model=MeetingResponse)
def create_meeting(obj_in:MeetingCreateUpdate ,db: Session = Depends(get_db)):
    """
    새로운 모임 생성하기.

    creator_id는 차후 토큰 적용하게 되면 토큰에서 추출할 것.

    - **name**: 모임 이름 또는 제목.
    - **location**: 모임 장소.
    - **description**: 모임  설명.
    - **meeting_time**: 모임 예정 날짜.
    - **max_participants**: 모임에 허용된 최대 참가자 수.
    - **image_url**: 모임 icon url.
    - **custom_tags**: 사용자가 추가하고자하는 태그 목록.
    - **custom_topics**: 사용자가 추가하고자하는 토픽 목록.
    - **creator_id**: 모임을 생성하는 사용자의 ID.
    - **tag_ids**: 미리 정의된 태그에 해당하는 ID의 목록.
    - **topic_ids**: 미리 정의된 토픽에 해당하는 ID의 목록.
    - **language_ids**: 모임에서 사용되는 언어에 해당하는 ID의 목록.

    반환값:
        모임 객체
    """
    meeting = crud.meeting.create(db=db, obj_in=obj_in)
    return meeting


@router.get("/meeting/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id,db: Session = Depends(get_db)):
    meeting = crud.meeting.get(db=db, id=meeting_id)
    return meeting


@router.get("/meetings", response_model=MeetingResponse)
def get_meeting(meeting_id,db: Session = Depends(get_db)):
    meeting = crud.meeting.get_multi(db=db, id=meeting_id)
    return meeting

