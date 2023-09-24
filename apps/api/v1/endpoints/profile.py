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
    Form,
    Path,
)
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session, joinedload

import crud
from database.session import get_db
from core.config import settings
from models.user import User
from models.profile import Profile, AvailableLanguage, Introduction
from schemas.profile import (
    ProfileCreate,
    ProfileResponse,
    ProfileBase,
    AvailableLanguageCreate,
    LanguageLevel,
    CreateProfileSchema,
    IntroductionCreate,
    UpdateProfileSchema,
)
from log import log_error

router = APIRouter()


@router.get("/profile/{user_id}/", response_model=ProfileResponse)
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
    profile: CreateProfileSchema,
    # profile_photo: UploadFile = None,
    db: Session = Depends(get_db),
):
    """
    사용자 프로필 생성 API

    해당 API는 주어진 사용자 ID에 대한 프로필을 생성합니다.
    사용자 ID가 존재하지 않거나 이미 프로필이 있는 경우에는 오류를 반환합니다.
    nick_name에 특수문자가 포함된 경우 오류를 반환합니다.

    Parameters:
    - profile.nick_name (str): 사용자의 닉네임입니다. 특수 문자를 포함할 수 없습니다.
    - profile.user_id (int): 프로필을 생성할 사용자의 ID입니다.
    - profile.profile_photo (Optional[UploadFile]): 사용자의 프로필 사진입니다.
    - profile.languages (List[ProfileCreateLanguage]): 사용자가 아는 언어의 목록입니다. 각 언어는 level과 language_id로 표시됩니다.
        - level (Optional[str]): 사용자의 해당 언어에 대한 숙련도입니다.
        - language_id (Optional[int]): 언어의 ID입니다.
    - profile.introduction (List[IntroductCreateLanguage]): 소개글 목록입니다.
        - keyword (Optional[str]): 소개글과 관련된 키워드입니다.
        - context (Optional[str]): 소개글의 내용이나 추가 정보입니다.

    Returns:
    - 생성된 프로필 정보.
    """
    new_profile = None
    user_languages = []
    user_introduction = []

    user = crud.user.get(db=db, id=profile.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 사용자에게 이미 프로필이 있는지 확인
    if user.profile:
        raise HTTPException(
            status_code=409, detail="Profile already exists for the user"
        )

    if re.search(r"[~!@#$%^&*()_+{}[\]:;<>,.?~]", profile.nick_name):
        raise HTTPException(
            status_code=400, detail="Nick_name contains special characters."
        )

    if not profile.introduction:
        raise HTTPException(status_code=400, detail="Need introduction.")

    if not profile.languages:
        raise HTTPException(status_code=400, detail="Need Available Language")

    try:
        obj_in = ProfileCreate(
            nick_name=profile.nick_name, profile_photo=profile.profile_photo
        )
        new_profile = crud.profile.create(db=db, obj_in=obj_in, user_id=profile.user_id)
        user_languages = profile.languages
        for lang in user_languages:
            available_language = AvailableLanguageCreate(
                level=lang.level,
                language_id=int(lang.language_id),
                profile_id=new_profile.id,
            )
            available_language_obj = crud.profile.create_ava_lan(
                db=db, obj_in=available_language
            )

        # introduction을 Introduction로 변환 및 추가
        user_introduction = profile.introduction
        for intro in user_introduction:
            introduction = IntroductionCreate(
                keyword=intro.keyword,
                context=intro.context,
                profile_id=new_profile.id,
            )
            introduction_obj = crud.profile.create_introduction(
                db=db, obj_in=introduction
            )

    except Exception as e:
        if new_profile:
            crud.profile.remove(db=db, id=new_profile.id)
        if user_languages:
            crud.profile.remove_ava_lan(db=db, profile_id=new_profile.id)
        if user_introduction:
            crud.profile.remove_introduction(db=db, profile_id=new_profile.id)

        print(e)
        log_error(e)
        raise HTTPException(status_code=500, detail=f"error about : {e}")

    return new_profile


@router.put("/profile/{user_id}/", response_model=ProfileResponse)
def update_profile(
    user_id: int,
    profile: UpdateProfileSchema,
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

    if profile.nick_name and re.search(
        r"[~!@#$%^&*()_+{}[\]:;<>,.?~]", profile.nick_name
    ):
        raise HTTPException(
            status_code=400, detail="Nick_name contains special characters."
        )

    # TODO: Additional update logic for languages, introduction, and verification
    # This will involve updating the relationships and possibly adding or removing records.

    # Update the existing profile with the provided data
    updated_profile_data = existing_profile.dict()
    update_data = profile.dict(exclude_unset=True)
    updated_profile_data.update(update_data)

    obj_in = ProfileCreate(**updated_profile_data)
    updated_profile = crud.profile.update(db=db, db_obj=existing_profile, obj_in=obj_in)

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

    return {"status": "Nick_name is available."}


@router.post("/profile/language", response_model=AvailableLanguageCreate)
async def create_available_language(
    level: LanguageLevel = Form(...),
    language_id: int = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
):
    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    lang = crud.utility.get(db=db, language_id=language_id)
    if not lang:
        raise HTTPException(status_code=404, detail="Languag not found")

    obj = AvailableLanguageCreate(
        level=level.value, language_id=language_id, user_id=user_id
    )
    new_ava = crud.profile.create_ava_lan(db=db, obj_in=obj)

    return new_ava


@router.get("/profile/random-nickname")
async def get_random_nickname():
    async with httpx.AsyncClient() as client:
        response = await client.get(settings.NICKNAME_API)

        # API 요청이 성공했는지 확인
        if response.status_code != 200:
            raise HTTPException(
                status_code=503,
                detail="Nickname API service unavailable",
            )

        data = response.json()

        kr_nick_name = data.get("words")[0]
        # TODO : random english nickname
        en_nick_name = data.get("en_nick_name")

    return {"kr_nick_name": kr_nick_name, "en_nick_name": en_nick_name}
