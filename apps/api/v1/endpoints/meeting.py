from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import crud
from database.session import get_db
from schemas.meeting import (
    MeetingResponse,
    MeetingCreateUpdate,
    MeetingDetailResponse,
    MeetingOrderingEnum,
    MeetingListResponse,
    TimeFilterEnum,
    MeetingUserCreate,
    MeetingUserResponse,
    ReviewResponse,
    ReviewCreate,
    ReviewUpdate,
    ReviewIn,
    ReviewUpdateIn,
    ReviewListReponse,
    MeetingUserListResponse,
)
from models.meeting import Meeting, MeetingUser, Review
from models.user import User
from schemas.enum import CreatorNationalityEnum
from log import log_error

router = APIRouter()


@router.post("/meeting/create", response_model=MeetingResponse)
def create_meeting(obj_in: MeetingCreateUpdate, db: Session = Depends(get_db)):
    """
    새로운 모임 생성

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
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        log_error(e)
        raise HTTPException(status_code=500)
    return meeting


@router.get("/meetings/{meeting_id}/requests", response_model=MeetingUserListResponse)
def get_meeting_requests(
    meeting_id: int, db: Session = Depends(get_db), skip: int = 0, limit: int = 10
):
    """
    모임 참가 신청 리스트
    """
    check_obj = crud.get_object_or_404(db=db, model=Meeting, obj_id=meeting_id)

    requests, total_count = crud.meeting.get_requests(
        db=db, meeting_id=meeting_id, skip=skip, limit=limit
    )
    return {"requests": requests, "total_count": total_count}


@router.post("/meeting/join/request")
def join_meeting_request(obj_in: MeetingUserCreate, db: Session = Depends(get_db)):
    """
    모임 참가 요청
    (user_id는 차후 token에서 추출할것)
    """

    check_obj = crud.get_object_or_404(db=db, model=Meeting, obj_id=obj_in.meeting_id)

    try:
        meeting = crud.meeting.join_request(db=db, obj_in=obj_in)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        log_error(e)
        raise HTTPException(status_code=500)
    return status.HTTP_201_CREATED


@router.post("/meeting/join/approve")
def join_meeting_approve(obj_id: int, db: Session = Depends(get_db)):
    """
    모임 참가 요청 승인
    """
    check_obj = crud.get_object_or_404(db=db, model=MeetingUser, obj_id=obj_id)

    try:
        meeting = crud.meeting.join_request_approve(db=db, obj_id=obj_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        log_error(e)
        raise HTTPException(status_code=500)
    return status.HTTP_201_CREATED


@router.post("/meeting/join/reject")
def join_meeting_approve(obj_id: int, db: Session = Depends(get_db)):
    check_obj = crud.get_object_or_404(db=db, model=MeetingUser, obj_id=obj_id)
    """
    모임 참가 요청 거절
    """
    try:
        meeting = crud.meeting.join_request_reject(db=db, obj_id=obj_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        log_error(e)
        raise HTTPException(status_code=500)
    return status.HTTP_201_CREATED


@router.get("/meeting/{user_id}/universty", response_model=MeetingListResponse)
def get_meetings_by_user_university(
    user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """
    특정 유저의 학교에서 모집중인 모임 조회
    """
    check_obj = crud.get_object_or_404(db=db, model=User, obj_id=user_id)
    try:
        meetings, total_count = crud.meeting.get_meetings_by_university(
            db=db, user_id=user_id, skip=skip, limit=limit
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        log_error(e)
        raise HTTPException(status_code=500)
    return {"meetings": meetings, "total_count": total_count}


@router.get("/meeting/{meeting_id}", response_model=MeetingDetailResponse)
def get_meeting_detail(meeting_id: int, db: Session = Depends(get_db)):
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

    - **users_languages** : 모임에 참가한 유저들의 언어 목록(level 포함)

    반환값:
        위의 세부 정보를 포함한 특정 모임의 상세 정보
    """
    check_obj = crud.get_object_or_404(db=db, model=Meeting, obj_id=meeting_id)

    try:
        meeting = crud.meeting.get(db=db, id=meeting_id)
    except HTTPException as e:
        raise e
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
    tags_ids: List[int] = Query(None),
    topics_ids: List[int] = Query(None),
    time_filters: List[str] = Query(None),
    is_count_only: bool = False,
    creator_nationality: CreatorNationalityEnum = CreatorNationalityEnum.ALL.value,
    search_word: str = None,
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

    - **tags**: 모임과 연결된 태그 목록. 각 태그에는 다음 정보가 포함됩니다
        - '기타' 로 검색시 고정값 외 모든 모임
        - **kr_name**: 태그의 한국어 이름 (Not Required)
        - **en_name**: 태그의 영어 이름 (Not Required)
        - **is_custom**: 고정값인지, 사용자가 생성한 값인지 (Default = False)

    - **order_by**: 모임과 연결된 태그 목록. 각 태그에는 다음 정보가 포함됩니다:
        - **CREATED_TIME**: 모임 생성 날짜 순 정렬
        - **MEETING_TIME**: 모임 일시 날짜 순 정렬
        - **DEADLINE_SOON**: 마감임박순 정렬

    - **time_filters**: 아래 string으로 요청 해주세요
        - ex) /meetings?order_by=created_time&skip=0&limit=10&time_filters=NEXT_WEEK&time_filters=AFTERNOON
            - **TODAY**
            - **TOMORROW**
            - **THIS_WEEK**
            - **NEXT_WEEK**
            - **MORNING**
            - **AFTERNOON**
            - **EVENING**
            - **MONDAY**
            - **TUESDAY**
            - **WEDNESDAY**
            - **THURSDAY**
            - **FRIDAY**
            - **SATURDAY**
            - **SUNDAY**

    - **is_count_only**
        - True : count만 리턴
        - False : Default

    - **creator_nationality** : 주최자 국적
        - "KOREAN", "FOREIGNER", "ALL"

    - **search_word** : 검색 단어(주제, 제목, 사용언어, 모임소개, 모임태그, 참가자 국적, 언어레벨에 검색됨)

    반환값:
        위의 세부 정보를 포함한 모임 목록
    """
    meetings, total_count = crud.meeting.get_multi(
        db=db,
        order_by=order_by,
        skip=skip,
        limit=limit,
        tags_ids=tags_ids,
        topics_ids=topics_ids,
        time_filters=time_filters,
        is_count_only=is_count_only,
        creator_nationality=creator_nationality,
        search_word=search_word,
    )

    return {"meetings": meetings, "total_count": total_count}


@router.get("/meeting/reviews/{user_id}", response_model=ReviewListReponse)
def get_meeting_all_review(
    user_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
):
    """
    User의 모든 Review
    """
    check_obj = crud.get_object_or_404(db=db, model=User, obj_id=user_id)

    reviews, total_count = (
        crud.review.get_multi(db=db, skip=skip, limit=limit, user_id=user_id) or []
    )
    return {"reviews": reviews, "total_count": total_count}


@router.post("/meeting/{meeting_id}/reviews")
def create_review(
    meeting_id: int,
    obj_in: ReviewIn,
    db: Session = Depends(get_db),
):
    """
    Meeting에 리뷰 작성

    - **obj_in**
        - context : 리뷰 내용
        - image_url : 리뷰 사진(mvp단계에선 1장)
        - creator_id : 리뷰 작성자(후에 token에서 추출)
    """
    check_obj = crud.get_object_or_404(db=db, model=Meeting, obj_id=meeting_id)
    check_user_obj = crud.get_object_or_404(db=db, model=User, obj_id=obj_in.creator_id)
    obj_in_data = ReviewCreate(**obj_in.model_dump(), meeting_id=meeting_id)
    try:
        create_obj = crud.review.create(db=db, obj_in=obj_in_data)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
    return create_obj


@router.put("/review/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    obj_in: ReviewUpdateIn,
    db: Session = Depends(get_db),
):
    """
    Review 수정

    - **obj_in**
        - context : 리뷰 내용
        - image_url : 리뷰 사진(mvp단계에선 1장)
    """
    check_obj = crud.get_object_or_404(db=db, model=Review, obj_id=review_id)
    obj_in_data = ReviewUpdate(**obj_in.model_dump())
    try:
        update_obj = crud.review.update(db=db, db_obj=check_obj, obj_in=obj_in_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
    return update_obj


@router.delete("/review/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    check_obj = crud.get_object_or_404(db=db, model=Review, obj_id=review_id)
    try:
        delete_obj = crud.review.remove(db=db, id=review_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
    return status.HTTP_204_NO_CONTENT


@router.get("/review/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    check_obj = crud.get_object_or_404(db=db, model=Review, obj_id=review_id)
    try:
        obj = crud.review.get(db=db, id=review_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
    return obj


@router.get("/fix-item")
def create_fix_item(db: Session = Depends(get_db)):
    """
    고정 값 생성
    """
    crud.utility.create_fix_items(db=db)
    return
