from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, Header
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

import crud
from database.session import get_db
from models.user import User
from models.profile import Profile
from schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse, ProfileBase

router = APIRouter()


@router.post("/profile/", response_model=ProfileBase)
def create_profile(
    profile: ProfileCreate,
    user_id: int,  # 사용자 ID를 추가로 받습니다.
    db: Session = Depends(get_db),
):
    # 유저 존재 확인
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 사용자에게 이미 프로필이 있는지 확인
    if user.profile:
        raise HTTPException(
            status_code=400, detail="Profile already exists for the user"
        )

    new_profile = ProfileCreate(
        first_name=profile.first_name,
        last_name=profile.last_name,
        birth=profile.birth,
        nationality=profile.nationality,
        gender=profile.gender,
        is_graduated=profile.is_graduated,
        university=profile.university,
        department=profile.department,
        user_id=user_id,  # 프로필의 user_id 설정
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
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
