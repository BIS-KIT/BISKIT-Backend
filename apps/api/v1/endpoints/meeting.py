from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
from database.session import get_db
from schemas.meeting import (
    MeetingResponse,
    MeetingCreateUpdate,
    MeetingDetailResponse,
    MeetingOrderingEnum,
    MeetingListResponse,
)
from log import log_error

router = APIRouter()


@router.post("/meeting/create", response_model=MeetingResponse)
def create_meeting(obj_in: MeetingCreateUpdate, db: Session = Depends(get_db)):
    """
    # 새로운 모임 생성

    ## 아래에 설명된 어트리뷰트들만 신경쓰면됨
    ## creator_id는 차후 토큰 적용하게 되면 토큰에서 추출할 것.

    - **name**: 모임의 이름
    - **location**: 모임 장소
    - **description**: 모임에 대한 설명 (Not Required)
    - **meeting_time**: 모임 예정 시간
    - **max_participants**: 모임에 참가 가능한 최대 인원
    - **image_url**: 모임 이미지의 URL (Not Required)
    - **is_active**: 모임이 활성 상태인지 여부 (Default = True)
    - **custom_tags**: 사용자가 추가하고자하는 태그 목록.
    - **custom_topics**: 사용자가 추가하고자하는 토픽 목록.
    - **creator_id**: 모임을 생성하는 사용자의 ID.
    - **tag_ids**: 미리 정의된 태그에 해당하는 ID의 목록.
    - **topic_ids**: 미리 정의된 토픽에 해당하는 ID의 목록.
    - **language_ids**: 모임에서 사용되는 언어에 해당하는 ID의 목록.

    반환값:
        모임 객체
    """
    try:
        meeting = crud.meeting.create(db=db, obj_in=obj_in)
    except Exception as e:
        print(e)
        log_error(e)
        raise HTTPException(status_code=500)
    return meeting


@router.get("/meeting/{meeting_id}", response_model=MeetingDetailResponse)
def get_meeting_detail(meeting_id, db: Session = Depends(get_db)):
    """
    특정 모임의 상세 정보를 조회합니다.

    - **meeting_id**: 조회할 모임의 ID

    - **name**: 모임의 이름
    - **location**: 모임 장소
    - **description**: 모임에 대한 설명 (Not Required)
    - **meeting_time**: 모임 예정 시간
    - **max_participants**: 모임에 참가 가능한 최대 인원
    - **image_url**: 모임 이미지의 URL (Not Required)
    - **is_active**: 모임이 활성 상태인지 여부 (Default = True)

    - **current_participants**: 현재 참가 중인 인원 (Default = 1)
    - **korean_count**: 한국 참가자 수 (Default = 0)
    - **foreign_count**: 외국 참가자 수 (Default = 0)

    - **creator**: 모임을 생성한 사용자 정보

    - **participants_status**: 한국인 모집 or 외국인 모집

    - **tags**: 모임과 연결된 태그 목록. 각 태그에는 다음 정보가 포함됩니다:
        - **kr_name**: 태그의 한국어 이름 (Not Required)
        - **en_name**: 태그의 영어 이름 (Not Required)
        - **is_custom**: 고정값인지, 사용자가 생성한 값인지 (Default = False)

    - **topics**: 모임과 연결된 주제 목록.

    - **languages**: 모임과 연결된 언어 목록.

    반환값:
        위의 세부 정보를 포함한 특정 모임의 상세 정보
    """
    try:
        meeting = crud.meeting.get(db=db, id=meeting_id)
    except Exception as e:
        print(e)
        log_error(e)
        raise HTTPException(status_code=500)
    return meeting


@router.get("/meetings", response_model=MeetingListResponse)
def get_meeting(
    db: Session = Depends(get_db),
    order_by: MeetingOrderingEnum = MeetingOrderingEnum.CREATED_TIME,
    skip: int = 0,
    limit: int = 10,
):
    """
    모임 목록을 조회합니다.

    - **name**: 모임의 이름
    - **location**: 모임 장소
    - **description**: 모임에 대한 설명 (Not Required)
    - **meeting_time**: 모임 예정 시간
    - **max_participants**: 모임에 참가 가능한 최대 인원
    - **image_url**: 모임 이미지의 URL (Not Required)
    - **is_active**: 모임이 활성 상태인지 여부 (Default = True)

    - **current_participants**: 현재 참가 중인 인원 (Default = 1)
    - **korean_count**: 한국 참가자 수 (Default = 0)
    - **foreign_count**: 외국 참가자 수 (Default = 0)

    - **creator**: 모임을 생성한 사용자 정보

    - **participants_status**: 한국인 모집 or 외국인 모집

    - **tags**: 모임과 연결된 태그 목록. 각 태그에는 다음 정보가 포함됩니다:
        - **kr_name**: 태그의 한국어 이름 (Not Required)
        - **en_name**: 태그의 영어 이름 (Not Required)
        - **is_custom**: 고정값인지, 사용자가 생성한 값인지 (Default = False)

    - **order_by**: 모임과 연결된 태그 목록. 각 태그에는 다음 정보가 포함됩니다:
        - **CREATED_TIME**: 모임 생성 날짜 순 정렬
        - **MEETING_TIME**: 모임 일시 날짜 순 정렬
        - **DEADLINE_SOON**: 마감임박순 정렬

    반환값:
        위의 세부 정보를 포함한 모임 목록
    """
    meetings, total_count = crud.meeting.get_multi(
        db=db, order_by=order_by, skip=skip, limit=limit
    )
    return {"meetings": meetings, "total_count": total_count}


@router.get("/fix-item")
def create_fix_item(db: Session = Depends(get_db)):
    """
    고정 값 생성
    """
    crud.utility.create_fix_items(db=db)
    return
