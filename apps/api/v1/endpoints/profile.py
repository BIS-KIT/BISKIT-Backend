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
    ProfileUpdate,
    ProfileBase,
    AvailableLanguageCreate,
    AvailableLanguageBase,
    IntroductionCreate,
    IntroductionResponse,
    IntroductionUpdate,
    AvailableLanguageUpdate,
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
    user_id: int,
    nick_name: str = None,
    profile_photo: UploadFile = None,
    db: Session = Depends(get_db),
):
    """ """
    new_profile = None

    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 사용자에게 이미 프로필이 있는지 확인
    if user.profile:
        raise HTTPException(
            status_code=409, detail="Profile already exists for the user"
        )

    if re.search(r"[~!@#$%^&*()_+{}[\]:;<>,.?~]", nick_name):
        raise HTTPException(
            status_code=400, detail="Nick_name contains special characters."
        )

    if not re.match("^[a-zA-Z0-9ㄱ-ㅎㅏ-ㅣ가-힣]{2,12}$", nick_name):
        raise HTTPException(status_code=400, detail="Invalid nickname.")

    try:
        obj_in = ProfileCreate(
            nick_name=nick_name, profile_photo=profile_photo, user_id=user_id
        )
    except Exception as e:
        log_error(e)
        print(e)
        raise HTTPException(status_code=500)
    new_profile = crud.profile.create(db=db, obj_in=obj_in)
    return new_profile


@router.put("/profile/{profile_id}/", response_model=ProfileResponse)
def update_profile(
    profile_id: int,
    nick_name: Optional[str] = None,
    profile_photo: UploadFile = None,
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
    existing_profile = crud.profile.get(db=db, id=profile_id)
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if nick_name and re.search(r"[~!@#$%^&*()_+{}[\]:;<>,.?~]", nick_name):
        raise HTTPException(
            status_code=400, detail="Nick_name contains special characters."
        )

    obj_in = ProfileUpdate(nick_name=nick_name, profile_photo=profile_photo)
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


@router.post("/profile/introduction", response_model=List[IntroductionResponse])
def create_introduction(
    introduction: List[IntroductionCreate],
    db: Session = Depends(get_db),
):
    created_introductions = []

    profile = crud.profile.get(db=db, id=introduction[0].profile_id)
    if not profile:
        raise HTTPException(status_code=400, detail="Profile not found")

    try:
        for intro in introduction:
            new_introduction = crud.profile.create_introduction(db=db, obj_in=intro)
            created_introductions.append(new_introduction)
    except Exception as e:
        log_error(e)
        print(e)
        if created_introductions:
            for intro in created_introductions:
                crud.profile.remove_introduction(db=db, profile_id=intro.profile_id)
        raise HTTPException(status_code=500)

    return created_introductions


@router.put(
    "/profile/introduction/{introduction_id}", response_model=IntroductionResponse
)
def update_introduction(
    introduction_id: int,
    introduction: IntroductionUpdate,
    db: Session = Depends(get_db),
):
    existing_introduction = crud.profile.get_introduction(db=db, id=introduction_id)
    if not existing_introduction:
        raise HTTPException(status_code=404, detail="Introduction not found")

    update_introdu = crud.profile.update_introduction(
        db=db, db_obj=existing_introduction, obj_in=introduction
    )
    return update_introdu


@router.get(
    "/profile/introduction/{introduction_id}", response_model=IntroductionResponse
)
def get_introduction(introduction_id: int, db: Session = Depends(get_db)):
    db_obj = crud.profile.get_introduction(db=db, id=introduction_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Introduction not found")
    return db_obj


@router.delete(
    "/profile/introduction/{introduction_id}", response_model=IntroductionResponse
)
def delete_introduction(introduction_id: int, db: Session = Depends(get_db)):
    db_obj = crud.profile.remove_introduction(db=db, id=introduction_id)
    return db_obj


@router.post("/profile/available-language", response_model=List[AvailableLanguageBase])
async def create_available_language(
    available_language: List[AvailableLanguageCreate],
    db: Session = Depends(get_db),
):
    """
    - BEGINNER = "초보"
    - BASIC = "기초"
    - INTERMEDIATE = "중급"
    - ADVANCED = "고급"
    - PROFICIENT = "능숙"

    """
    return_list = []

    if len(available_language) >= 5:
        raise HTTPException(status_code=409, detail="Only up to 5 can be created.")

    profile = crud.profile.get(db=db, id=available_language[0].profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="profile not found")

    for ava_lang in available_language:
        lang = crud.utility.get(db=db, language_id=ava_lang.language_id)

        if not lang:
            raise HTTPException(status_code=404, detail="Languag not found")

        obj = AvailableLanguageCreate(
            level=ava_lang.level,
            language_id=ava_lang.language_id,
            profile_id=ava_lang.profile_id,
        )
        new_ava = crud.profile.create_ava_lan(db=db, obj_in=obj)
        return_list.append(new_ava)

    return return_list


@router.get(
    "/profile/available-language/{ava_lang_id}", response_model=AvailableLanguageBase
)
async def get_available_language(ava_lang_id: int, db: Session = Depends(get_db)):
    db_obj = crud.profile.get_ava_lan(db=db, id=ava_lang_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="AvailableLanguage not found")
    return db_obj


@router.delete(
    "/profile/available-language/{ava_lang_id}", response_model=AvailableLanguageBase
)
async def delete_available_language(ava_lang_id: int, db: Session = Depends(get_db)):
    db_obj = crud.profile.remove_ava_lan(db=db, id=ava_lang_id)
    return db_obj


@router.put(
    "/profile/available-language/{ava_lang_id}", response_model=AvailableLanguageBase
)
async def update_available_language(
    ava_lang_id: int,
    available_language: AvailableLanguageUpdate,
    db: Session = Depends(get_db),
):
    existing_ava_lang = crud.profile.get_ava_lan(db=db, id=ava_lang_id)
    if not existing_ava_lang:
        raise HTTPException(status_code=404, detail="Introduction not found")

    update_introdu = crud.profile.update_ava_lan(
        db=db, db_obj=existing_ava_lang, obj_in=available_language
    )
    return update_introdu
