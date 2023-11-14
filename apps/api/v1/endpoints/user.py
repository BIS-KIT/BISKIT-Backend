from typing import Any, List, Optional, Dict
import re, traceback

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.exc import IntegrityError

import crud
from log import log_error
from schemas.user import (
    UserResponse,
    UserNationalityResponse,
    ConsentResponse,
    UserUniversityBase,
    UserUniversityUpdate,
    UserUniversityUpdateIn,
    UserUpdate,
    UserBaseUpdate,
)
from models.user import User
from core.security import (
    get_current_user,
)
from database.session import get_db
from core.config import settings

router = APIRouter()


@router.get("/users/me", response_model=UserResponse)
async def read_current_user(current_user=Depends(get_current_user)):
    """
    현재 사용자의 정보를 반환합니다.

    **인자:**
    - current_user (User): 현재 인증된 사용자.

    **반환값:**
    - dict: 인증된 사용자의 정보.
    """
    return current_user


@router.get("/users", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    사용자 목록을 반환합니다.

    **파라미터**

    * `skip`: 건너뛸 항목의 수
    * `limit`: 반환할 최대 항목 수

    **반환**

    * 사용자 목록
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    if users is None:
        raise HTTPException(status_code=404, detail="Users not found")
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    특정 사용자의 정보를 조회합니다.

    **파라미터**

    * `user_id`: 조회하려는 사용자의 ID

    **반환값**

    * 조회된 사용자의 정보
    """
    users = crud.user.get(db=db, id=user_id)
    if users is None:
        raise HTTPException(status_code=404, detail="Users not found")
    return users


@router.delete("/user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    특정 사용자를 삭제합니다.

    **파라미터**

    * `user_id`: 삭제하려는 사용자의 ID

    **반환값**

    * 삭제된 사용자의 정보
    """

    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    delete_obj = crud.user.remove(db, id=user_id)
    return status.HTTP_204_NO_CONTENT


@router.put("/user/{user_id}", response_model=UserResponse)
def update_user(
    user_in: UserUpdate,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Update user details using email address as identifier.

    Returns:
    - dict: Updated user details.
    """
    user_university = user_in.university_id
    new_nationality_ids = user_in.nationality_ids

    db_user = crud.user.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Ensure that the provided details are valid
    if user_university:
        university = crud.utility.get(db=db, university_id=user_in.university_id)
        if not university:
            raise HTTPException(status_code=400, detail="University Not Found")

    if new_nationality_ids:
        for id in user_in.nationality_ids:
            nation = crud.utility.get(db=db, nationality_id=id)
            if not nation:
                raise HTTPException(status_code=400, detail="Nationality Not Found")

    try:
        # Update user details in the database
        if user_in.name or user_in.birth or user_in.gender:
            user_base_in = UserBaseUpdate(
                name=user_in.name, birth=user_in.birth, gender=user_in.gender
            )
            update_user = crud.user.update(db=db, db_obj=db_user, obj_in=user_base_in)

        if user_university:
            current_university = crud.user.get_university(db=db, user_id=user_id)
            update_university_in = UserUniversityUpdate(
                university_id=user_in.university_id,
                department=user_in.department,
                education_status=user_in.education_status,
            )
            crud.user.update_university(
                db=db, db_obj=current_university, obj_in=update_university_in
            )

        if new_nationality_ids:
            crud.user.update_user_nationalities(
                db=db, user_id=user_id, new_nationality_ids=new_nationality_ids
            )

    except Exception as e:
        print(e, traceback.format_exc())
        log_error(e)
        raise HTTPException(status_code=500)

    return db_user


@router.get("/user/{user_id}/consent", response_model=ConsentResponse)
def get_user_consent(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 동의 정보를 반환합니다.

    **인자:**
    - user_id (int): 사용자 ID.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - ConsentResponse: 사용자의 동의 정보.
    """
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    consent = crud.user.get_consent(db=db, user_id=user_id)
    if not consent:
        raise HTTPException(status_code=400, detail="Consent not found")
    return consent


@router.delete("/user/{user_id}/consent")
def delete_user_consent(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 동의 정보를 삭제합니다.

    **인자:**
    - user_id (int): 사용자 ID.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - ConsentResponse: 삭제된 동의 정보.
    """
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    consent = crud.user.get_consent(db=db, user_id=user_id)
    if not consent:
        raise HTTPException(status_code=400, detail="Consent not found")

    db_obj = crud.user.remove_consent(db=db, id=consent.id)
    return status.HTTP_204_NO_CONTENT


@router.get("/user/{user_id}/university", response_model=UserUniversityBase)
def get_user_university(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 대학 정보를 반환합니다.

    **인자:**
    - user_id (int): 사용자 ID.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - UserUniversityBase: 사용자의 대학 정보.
    """
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user_university = crud.user.get_university(db=db, user_id=user_id)
    if not user_university:
        raise HTTPException(status_code=400, detail="user_university not found")
    return user_university


@router.delete("/user/{user_id}/university")
def delete_user_university(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 대학 정보를 삭제합니다.

    **인자:**
    - user_id (int): 사용자 ID.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - UserUniversityBase: 삭제된 대학 정보.
    """
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user_university = crud.user.get_university(db=db, user_id=user_id)
    if not user_university:
        raise HTTPException(status_code=400, detail="user_university not found")

    db_obj = crud.user.remove_university(db=db, id=user_university.id)
    return status.HTTP_204_NO_CONTENT


@router.put("/user/{user_id}/university", response_model=UserUniversityBase)
def update_user_university(
    user_id: int,
    user_univeristy: UserUniversityUpdateIn,
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 대학 정보를 업데이트합니다.

    **인자:**
    - user_id (int): 사용자 ID.
    - user_university (UserUniversityUpdate): 업데이트할 대학 정보.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - UserUniversityBase: 업데이트된 대학 정보.
    """
    exsisting_user_university = crud.user.get_university(db=db, user_id=user_id)
    if not exsisting_user_university:
        raise HTTPException(status_code=404, detail="UserUniversity not found")

    update_user_univer = crud.user.update_university(
        db=db, db_obj=exsisting_user_university, obj_in=user_univeristy
    )
    return update_user_univer


@router.get("/user/{user_id}/nationality", response_model=UserNationalityResponse)
def get_user_nationality(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 국적 정보를 반환합니다.

    **인자:**
    - user_id (int): 사용자 ID.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - UserNationalityResponse: 사용자의 국적 정보.
    """
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user_nationality = crud.user.get_nationality(db=db, user_id=user_id)
    if not user_nationality:
        raise HTTPException(status_code=400, detail="user_nationality not found")
    return user_nationality


@router.delete("/user/{user_id}/nationality")
def delete_user_nationality(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 국적 정보를 삭제합니다.

    **인자:**
    - user_id (int): 사용자 ID.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - UserNationalityResponse: 삭제된 국적 정보.
    """
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user_nationality = crud.user.get_nationality(db=db, user_id=user_id)
    if not user_nationality:
        raise HTTPException(status_code=400, detail="user_nationality not found")

    db_obj = crud.user.remove_nationality(db=db, id=user_nationality.id)
    return status.HTTP_204_NO_CONTENT
