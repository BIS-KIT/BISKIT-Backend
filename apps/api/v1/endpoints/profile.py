import httpx, shutil
from typing import Any, List, Optional, Dict

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Header,
    File,
    UploadFile,
    Path,
)
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

import crud
from database.session import get_db
from core.config import settings
from models.user import User
from models.profile import Profile
from schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse, ProfileBase

router = APIRouter()


@router.get("/profile/{user_id}/", response_model=ProfileBase)
def get_profile_by_user_id(
    user_id: int = Path(..., title="The ID of the user"), db: Session = Depends(get_db)
):
    """
    user_id를 이용하여 프로필 정보를 가져옵니다.

    매개변수:
    - user_id (int): 프로필 정보를 검색할 사용자의 ID.
    - db (Session): 데이터베이스 세션.

    반환값:
    - ProfileBase: 지정된 user_id에 해당하는 사용자의 프로필 정보.
    """
    db_profile = crud.profile.get_by_user_id(db, user_id=user_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile


@router.post("/profile/", response_model=ProfileBase)
def create_profile(
    profile: ProfileCreate,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    사용자 프로필 생성 API

    해당 API는 주어진 사용자 ID에 대한 프로필을 생성합니다.
    사용자 ID가 존재하지 않거나 이미 프로필이 있는 경우에는 오류를 반환합니다.
    닉네임이 제공되지 않은 경우, 외부 API를 통해 닉네임을 자동으로 생성합니다.

    Required:
    - first_name
    - last_name
    - gender

    Parameters:
    - profile: Profile 생성을 위한 정보.
    - user_id: 프로필을 생성하려는 사용자의 ID.

    Returns:
    - 생성된 프로필 정보.
    """
    # 유저 존재 확인
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 사용자에게 이미 프로필이 있는지 확인
    if user.profile:
        raise HTTPException(
            status_code=400, detail="Profile already exists for the user"
        )

    nick_name = profile.nick_name
    if not nick_name:
        # 닉네임을 생성하기 위해 외부 API에 요청
        response = httpx.get(settings.nickname_api)
        response.raise_for_status()  # 오류가 발생하면 예외를 발생시킵니다.
        nick_name = response.json()["words"][0]

    obj_in = ProfileCreate(
        first_name=profile.first_name,
        last_name=profile.last_name,
        nick_name=nick_name,
        birth=profile.birth,
        nationality=profile.nationality,
        gender=profile.gender,
        is_graduated=profile.is_graduated,
        university=profile.university,
        department=profile.department,
    )

    new_profile = crud.profile.create(db=db, obj_in=obj_in, user_id=user_id)
    return new_profile


@router.put("/profile/{profile_id}/", response_model=ProfileUpdate)
def update_profile(
    profile_id: int,  # 업데이트할 프로필의 ID
    profile: ProfileUpdate,
    db: Session = Depends(get_db),
):
    # 프로필 존재 확인
    existing_profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # CRUD update 메서드 호출
    updated_profile = crud.profile.update(
        db=db, db_obj=existing_profile, obj_in=profile
    )

    return updated_profile


@router.delete("/profile/{profile_id}", response_model=ProfileResponse)
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    """
    프로필 삭제 API
    """
    profile = crud.profile.get(db, id=profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return crud.profile.remove(db, id=profile_id)


@router.delete("/profile/user/{user_id}", response_model=ProfileBase)
def delete_profile_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 ID를 기반으로 프로필 삭제 API
    """
    profile = crud.profile.get_by_user_id(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=404, detail="Profile not found for the given user_id"
        )
    return crud.profile.remove(db, id=profile.id)
