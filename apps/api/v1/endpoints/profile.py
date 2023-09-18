import httpx, shutil, re
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
from schemas.profile import ProfileCreate, ProfileResponse, ProfileBase

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


@router.post("/profile/", response_model=ProfileResponse)
def create_profile(
    profile: ProfileCreate,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    사용자 프로필 생성 API

    해당 API는 주어진 사용자 ID에 대한 프로필을 생성합니다.
    사용자 ID가 존재하지 않거나 이미 프로필이 있는 경우에는 오류를 반환합니다.

    Parameters:
    - profile: Profile 생성을 위한 정보.
    - user_id: 프로필을 생성하려는 사용자의 ID.

    Returns:
    - 생성된 프로필 정보.
    """
    # 유저 존재 확인
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 사용자에게 이미 프로필이 있는지 확인
    if user.profile:
        raise HTTPException(
            status_code=409, detail="Profile already exists for the user"
        )

    new_profile = crud.profile.create(db=db, obj_in=profile, user_id=user_id)
    return new_profile


@router.put("/profile/{user_id}/", response_model=ProfileResponse)
def update_profile(
    user_id: int,
    profile: ProfileCreate,
    db: Session = Depends(get_db),
):
    """
    사용자 프로필 업데이트 API

    이 API는 주어진 사용자 ID에 대한 프로필 정보를 업데이트합니다.
    프로필이 존재하지 않는 경우 오류를 반환합니다.

    Parameters:
    - user_id: 업데이트하려는 프로필의 사용자 ID.
    - profile: 업데이트를 위한 프로필 정보.

    Returns:
    - 업데이트된 프로필 정보.
    """
    # 프로필 존재 확인
    existing_profile = crud.profile.get_by_user_id(db=db, user_id=user_id)
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    updated_profile = crud.profile.update(
        db=db, db_obj=existing_profile, obj_in=profile
    )

    return updated_profile


@router.delete("/profile/{profile_id}", response_model=ProfileResponse)
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    """
    프로필 삭제 API

    해당 API는 주어진 프로필 ID로 프로필을 삭제합니다.
    프로필이 존재하지 않는 경우 오류를 반환합니다.

    Parameters:
    - profile_id: 삭제하려는 프로필의 ID.

    Returns:
    - 삭제된 프로필의 정보.
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


@router.delete("/profile/{user_id}/photo")
async def delete_profile_photo(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 프로필 사진 삭제 API

    해당 API는 주어진 사용자 ID에 대한 프로필 사진을 삭제합니다.
    사용자 프로필이 존재하지 않는 경우 오류를 반환합니다.

    Parameters:
    - user_id: 사진을 삭제하려는 사용자의 ID.

    Returns:
    - 삭제 처리 결과.
    """
    profile = crud.profile.get_by_user_id(db, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.profile.remove_profile_photo(db=db, user_id=user_id)


@router.get("/profile/nick-name")
async def check_nick_name(nick_name: str, db: Session = Depends(get_db)):
    """
    닉네임 사용 가능 여부 확인 API

    이 API는 주어진 닉네임의 사용 가능 여부를 확인합니다.
    - 닉네임에 특수문자가 포함된 경우, 에러를 반환합니다.
    - 닉네임이 이미 사용 중인 경우, 에러를 반환합니다.

    Parameters:
    - nick_name: 사용 가능 여부를 확인하려는 닉네임.

    Returns:
    - 닉네임 사용 가능 여부에 대한 메시지.
    """

    # 닉네임에 특수문자 포함 여부 체크
    if re.search(r"[~!@#$%^&*()_+{}[\]:;<>,.?~]", nick_name):
        raise HTTPException(
            status_code=400, detail="Nick_name contains special characters."
        )

    exists_nick = crud.profile.get_by_nick_name(db=db, nick_name=nick_name)
    if exists_nick:
        raise HTTPException(status_code=409, detail="nick_name already used")

    return {"status": "Nick_name is available."} @ router.get("/profile/nick-name")


async def check_nick_name(nick_name: str, db: Session = Depends(get_db)):
    """
    닉네임 사용 가능 여부 확인 API

    이 API는 주어진 닉네임의 사용 가능 여부를 확인합니다.
    - 닉네임에 특수문자가 포함된 경우, 에러를 반환합니다.
    - 닉네임이 이미 사용 중인 경우, 에러를 반환합니다.

    Parameters:
    - nick_name: 사용 가능 여부를 확인하려는 닉네임.

    Returns:
    - 닉네임 사용 가능 여부에 대한 메시지.
    """

    # 닉네임에 특수문자 포함 여부 체크
    if re.search(r"[~!@#$%^&*()_+{}[\]:;<>,.?~]", nick_name):
        raise HTTPException(
            status_code=400, detail="Nick_name contains special characters."
        )

    exists_nick = crud.profile.get_by_nick_name(db=db, nick_name=nick_name)
    if exists_nick:
        raise HTTPException(status_code=409, detail="nick_name already used")

    return {"status": "Nick_name is available."}
