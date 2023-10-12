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
    Query,
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
    AvailableLanguageResponse,
    ProfileUpdate,
    ProfileBase,
    AvailableLanguageCreate,
    AvailableLanguageBase,
    IntroductionCreate,
    IntroductionResponse,
    IntroductionUpdate,
    AvailableLanguageUpdate,
    ProfileRegister,
    StudentVerificationUpdate,
    VerificationStatus,
    StudentVerificationBase,
    StudentVerificationCreate,
)
from log import log_error

router = APIRouter()

@router.get("/profile/photos")
def get_profile_photos(user_ids: List[str] = Query(None), db: Session = Depends(get_db)):
    """
    user_ids 받아서 해당 user의 photo, nick-name return

    - ex) /profiles/photos?user_ids=1&user_ids=2&user_ids=3
    """
    return_list = []
    for id in user_ids:
        profile = crud.profile.get_by_user_id(db=db, user_id=id)
        if not profile:
            continue
        photo_dict = {"user_id":id, "profile_photo":profile.profile_photo, "nick_name":profile.nick_name}
        return_list.append(photo_dict)
    return return_list

@router.post("/profile/photo")
def update_profile_photo(
    is_profile: bool, photo: UploadFile, db: Session = Depends(get_db)
):
    """
    photo upload API

    - is_profile = True : /profile_photo 저장
    - is_profile = False : /student_card 저장
    """
    file_path = None
    if is_profile:
        file_path = f"profile_photo/{crud.generate_random_string()}_{photo.filename}"
    else:
        file_path = f"student_card/{crud.generate_random_string()}_{photo.filename}"

    try:
        image_url = crud.save_upload_file(upload_file=photo, destination=file_path)
    except Exception as e:  # 어떤 예외든지 캐치합니다.
        log_error(e)
        # 클라이언트에게 에러 메시지와 상태 코드를 반환합니다.
        raise HTTPException(status_code=500)
    return {"image_url": image_url}

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

        kr_nick_name = data.get("words")[0].split(" ")[:-1] + [" 비스킷"]
        kr_nick_name = "".join(kr_nick_name)
        # TODO : random english nickname
        en_nick_name = data.get("en_nick_name")

    return {"kr_nick_name": kr_nick_name, "en_nick_name": en_nick_name}

@router.post("/profile/introduction", response_model=List[IntroductionResponse])
def create_introduction(
    introduction: List[IntroductionCreate],
    db: Session = Depends(get_db),
):
    """
    사용자 소개 생성 API.

    이 API는 주어진 사용자 소개 정보로 새로운 사용자 소개를 생성합니다.

    매개변수:
    - introduction (List[IntroductionCreate]): 사용자 소개 목록.
    - db (Session): 데이터베이스 세션.

    반환값:
    - List[IntroductionResponse]: 생성된 사용자 소개 목록.
    """
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
    사용자의 사용 가능 언어 생성 API.

    매개변수:
    - available_language (List[AvailableLanguageCreate]): 사용자의 사용 가능 언어 목록.
    - db (Session): 데이터베이스 세션.

    반환값:
    - List[AvailableLanguageBase]: 생성된 사용 가능 언어 목록.
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
    """
    사용자의 사용 가능 언어 업데이트 API.

    매개변수:
    - ava_lang_id (int): 업데이트할 사용 가능 언어의 ID.
    - available_language (AvailableLanguageUpdate): 업데이트할 사용 가능 언어 정보.
    - db (Session): 데이터베이스 세션.

    반환값:
    - AvailableLanguageBase: 업데이트된 사용 가능 언어 정보.
    """
    existing_ava_lang = crud.profile.get_ava_lan(db=db, id=ava_lang_id)
    if not existing_ava_lang:
        raise HTTPException(status_code=404, detail="Introduction not found")

    update_introdu = crud.profile.update_ava_lan(
        db=db, db_obj=existing_ava_lang, obj_in=available_language
    )
    return update_introdu

@router.post("/student-card", response_model=StudentVerificationBase)
def student_varification(
    student_card: str,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    학생증 인증 정보를 제출합니다.

    **인자:**
    - student_card (UploadFile): 업로드된 학생증 이미지 파일.
    - user_id (int): 사용자 ID.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - StudentVerificationBase: 학생증 인증 정보.
    """
    user = crud.user.get(db=db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")

    profile = crud.profile.get_by_user_id(db=db,user_id=user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="profile not found")

    obj_in = StudentVerificationCreate(
        student_card=student_card,
        profile_id=profile.id,
    )

    try:
        user_verification = crud.profile.create_verification(db=db, obj_in=obj_in)
    except Exception as e:
        log_error(e)
        raise HTTPException(status_code=500)
    return user_verification


@router.get("/student-card/{user_id}", response_model=StudentVerificationBase)
def student_varification(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 학생증 인증 정보를 조회합니다.

    **인자:**
    - user_id (int): 사용자 ID.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - StudentVerificationBase: 학생증 인증 정보.
    """
    user = crud.user.get(db=db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    
    profile = crud.profile.get_by_user_id(db=db,user_id=user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="profile not found")

    db_obj = crud.profile.get_verification(db=db, profile_id=profile.id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="StudentVerification not found")
    return db_obj


@router.post("/student-card/{user_id}/approve")
def approve_varification(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    특정 사용자의 학생증 인증을 승인합니다.

    **인자:**
    - user_id (int): 사용자 ID.
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - dict: 인증 승인 결과.
    """
    user = crud.user.get(db=db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    
    profile = crud.profile.get_by_user_id(db=db,user_id=user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="profile not found")

    verification = crud.profile.get_verification(db=db, profile_id=profile.id)
    if verification is None:
        raise HTTPException(status_code=404, detail="StudentVerification not found")

    obj_in = StudentVerificationUpdate(
        verification_status=VerificationStatus.VERIFIED.value
    )
    update_verification = crud.profile.update_verification(
        db=db, db_obj=verification, obj_in=obj_in
    )
    return update_verification


@router.get("/student-cards", response_model=List[StudentVerificationBase])
def read_student_cards(db: Session = Depends(get_db)):
    """
    학생증 인증을 대기 중인 목록을 반환합니다.

    **인자:**
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - List[StudentVerificationBase]: 학생증 인증 대기 중인 목록.
    """
    obj_list = crud.profile.list_verification(db=db)
    return obj_list

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
    사용자 프로필 사진 삭제 API.

    매개변수:
    - user_id (int): 사용자 ID.
    - db (Session): 데이터베이스 세션.

    반환값:
    - 메시지: 프로필 사진 삭제 성공 메시지.
    """
    profile = crud.profile.get_by_user_id(db, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.profile.remove_profile_photo(db=db, user_id=user_id)

@router.get("/profile/{user_id}", response_model=ProfileResponse)
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

@router.post("/profile", response_model=ProfileResponse)
def create_profile(
    profile: ProfileRegister,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Profile 생성 API

        - nick_name : str
        - profile_photo : str : file_path
        - available_languages
            - level : 언어수준 ["BEGINNER","BASIC","INTERMEDIATE","ADVANCED","PROFICIENT"]
            - language_id : 언어 id
        - introductions
            - keyword : 키워드
            - context : 자기소개
        - student_verification
            - student_card : file_path
            - verification_status : 인증 상태 ["PENDING","VERIFIED","REJECTED","UNVERIFIED"]
    """
    new_profile = None
    ava_list = []
    intro_list = []

    available_language: List[AvailableLanguageCreate] = profile.available_languages
    Introductions: List[IntroductionCreate] = profile.introductions
    student_card = profile.student_card

    user = crud.user.get(db=db, id=user_id)
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

    if not re.match("^[a-zA-Z0-9ㄱ-ㅎㅏ-ㅣ가-힣]{2,12}$", profile.nick_name):
        raise HTTPException(status_code=400, detail="Invalid nickname.")

    if len(available_language) >= 5:
        raise HTTPException(status_code=409, detail="Only up to 5 can be created.")

    for ava_lang in available_language:
        lang = crud.utility.get(db=db, language_id=ava_lang.language_id)

        if not lang:
            raise HTTPException(status_code=404, detail="Languag not found")

    try:
        obj_in = ProfileCreate(
            nick_name=profile.nick_name,
            profile_photo=profile.profile_photo,
            user_id=user_id,
        )
        new_profile = crud.profile.create(db=db, obj_in=obj_in)
    except Exception as e:
        if new_profile:
            crud.profile.remove(db=db, id=new_profile.id)
        log_error(e)
        raise HTTPException(status_code=500)

    try:
        for ava_lang in available_language:
            obj_in = AvailableLanguageCreate(
                level=ava_lang.level,
                language_id=ava_lang.language_id,
                profile_id=new_profile.id,
            )
            new_ava = crud.profile.create_ava_lan(db=db, obj_in=obj_in)
            ava_list.append(new_ava)
    except Exception as e:
        if available_language:
            for ava in ava_list:
                crud.profile.remove_ava_lan(db=db, id=ava.id)
        log_error(e)
        raise HTTPException(status_code=500)

    try:
        for intro in Introductions:
            obj_in = IntroductionCreate(
                keyword=intro.keyword, context=intro.context, profile_id=new_profile.id
            )
            new_introduction = crud.profile.create_introduction(db=db, obj_in=obj_in)
            intro_list.append(new_introduction)
    except Exception as e:
        if available_language:
            for ava in ava_list:
                crud.profile.remove_ava_lan(db=db, id=ava.id)
        log_error(e)
        raise HTTPException(status_code=500)
    if student_card:
        try:
            obj_in = StudentVerificationCreate(
                student_card=student_card.student_card,
                verification_status=student_card.verification_status,
                profile_id=new_profile.id,
            )

            crud.profile.create_verification(db=db, obj_in=obj_in)
        except Exception as e:
            log_error(e)

    return new_profile

@router.put("/profile/{profile_id}", response_model=ProfileResponse)
def update_profile(
    profile_id: int,
    profile_in: ProfileUpdate,
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
    new_profile = None
    # 프로필 존재 확인
    existing_profile = crud.profile.get(db=db, id=profile_id)
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    new_nickname = profile_in.nick_name
    new_photo = profile_in.profile_photo
    if new_nickname:
        if re.search(r"[~!@#$%^&*()_+{}[\]:;<>,.?~]", new_nickname):
            raise HTTPException(
                status_code=400, detail="Nick_name contains special characters."
            )
        check_exists_nickname = crud.profile.get_by_nick_name(
            db=db, nick_name=new_nickname
        )
        if check_exists_nickname:
            raise HTTPException(status_code=409, detail="nick_name already used")

    if new_photo:
        if existing_profile.profile_photo:
            crud.profile.delete_file_from_s3(file_url=existing_profile.profile_photo)
    try:
        new_profile = crud.profile.update(
            db=db, db_obj=existing_profile, obj_in=profile_in
        )
    except Exception as e:
        log_error(e)
        raise HTTPException(status_code=500, detail="Error updating profile")
    return new_profile