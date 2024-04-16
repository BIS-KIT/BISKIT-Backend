import httpx, shutil, re
from typing import Any, List, Optional, Dict, Annotated
import random
import asyncio

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
    Request,
    status,
)
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

import crud
from core.security import oauth2_scheme
from database.session import get_db
from core.config import settings
from schemas.profile import (
    ProfileResponse,
    ProfileUpdate,
    ProfileBase,
    AvailableLanguageCreate,
    ProfileRegister,
    StudentVerificationBase,
    StudentVerificationCreate,
)
from schemas.enum import MyMeetingEnum, MeetingOrderingEnum, ReultStatusEnum
from schemas.meeting import MeetingListResponse
from log import log_error

router = APIRouter()


@router.get("/profile/photos")
def get_profile_photos(
    user_ids: List[str] = Query(None),
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    """
    user_ids 받아서 해당 user의 photo, nick-name return

    - ex) /profiles/photos?user_ids=1&user_ids=2&user_ids=3
    """
    return_list = []
    for id in user_ids:
        national_list = []
        user = crud.user.get(db=db, id=id)
        if not user:
            continue
        profile = crud.profile.get_by_user_id(db=db, user_id=id)
        nationalites = crud.user.read_nationalities(db=db, user_id=id)
        if nationalites:
            for nan in nationalites:
                nationality = crud.utility.get(db=db, nationality_id=nan.nationality_id)
                national_list.append(nationality.to_dict())

        photo_dict = {
            "user_id": int(id),
            "profile_photo": profile.profile_photo if profile else None,
            "nick_name": profile.nick_name if profile else None,
            "nationalities": national_list,
        }
        return_list.append(photo_dict)
    return return_list


@router.post("/profile/photo")
def update_profile_photo(
    is_profile: bool,
    photo: UploadFile,
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
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
async def check_nick_name(
    nick_name: str,
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
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

    # 닉네임 유효성 검사 (특수문자 포함 여부 및 예약어 사용 여부)
    if (
        re.search(r"[~!@#$%^&*()_+{}[\]:;<>,.?~]", nick_name)
        or "admin" in nick_name.lower()
        or "관리자" in nick_name.lower()
    ):
        raise HTTPException(
            status_code=409,
            detail="Nick_name contains special characters or restricted keywords.",
        )

    exists_nick = crud.profile.get_by_nick_name(db=db, nick_name=nick_name)
    if exists_nick:
        raise HTTPException(status_code=409, detail="nick_name already used")

    return {"status": "Nick_name is available."}


@router.get("/profile/random-image")
def get_random_image():
    random_profile_images = [
        "/default_profile_photo/version=1.png",
        "/default_profile_photo/version=2.png",
        "/default_profile_photo/version=3.png",
        "/default_profile_photo/version=4.png",
        "/default_profile_photo/version=5.png",
    ]
    selected_image = random.choice(random_profile_images)
    image_url = settings.S3_URL + selected_image
    return {"image_url": image_url}


@router.get("/profile/random-nickname")
async def get_random_nickname(
    os_lang: str = "kr",
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    kr_nick_name, en_nick_name = None, None
    if os_lang == "kr":
        async with httpx.AsyncClient() as client:
            while True:
                response = await client.get(settings.NICKNAME_API)

                # API 요청이 성공했는지 확인
                if response.status_code != 200:
                    # 잠시 후에 다시 시도
                    await asyncio.sleep(3)  # 3초 대기
                    continue

                data = response.json()

                kr_nick_name = data.get("words")[0]

                check_exists = crud.profile.get_with_nick_name(
                    db=db, nick_name=kr_nick_name
                )

                # 중복되지 않은 닉네임이면 break
                if check_exists is None:
                    break

                # 중복된 경우, 잠시 대기 후 다시 시도
                await asyncio.sleep(2)  # 2초 대기
    elif os_lang == "en":
        # TODO : random english nickname
        en_nick_name = data.get("en_nick_name")

    return {"kr_nick_name": kr_nick_name, "en_nick_name": en_nick_name}


@router.post("/student-card", response_model=StudentVerificationBase)
def student_varification(
    student_card: str,
    user_id: int,
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
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

    profile = crud.profile.get_by_user_id(db=db, user_id=user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="profile not found")

    obj_in = StudentVerificationCreate(
        student_card=student_card,
        profile_id=profile.id,
        verification_status=ReultStatusEnum.PENDING.value,
    )

    try:
        user_verification = crud.profile.create_verification(db=db, obj_in=obj_in)
    except Exception as e:
        log_error(e)
        raise HTTPException(status_code=500)
    return user_verification


@router.get("/student-card/{user_id}", response_model=StudentVerificationBase)
def read_student_varification(
    user_id: int,
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
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

    profile = crud.profile.get_by_user_id(db=db, user_id=user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="profile not found")

    db_obj = crud.profile.get_verification(db=db, profile_id=profile.id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="StudentVerification not found")
    return db_obj


@router.get("/student-cards", response_model=List[StudentVerificationBase])
def read_student_cards(
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    """
    학생증 인증을 대기 중인 목록을 반환합니다.

    **인자:**
    - db (Session): 데이터베이스 세션.

    **반환값:**
    - List[StudentVerificationBase]: 학생증 인증 대기 중인 목록.
    """
    obj_list = crud.profile.list_verification(db=db)
    return obj_list


@router.delete("/profile/user/{user_id}")
def delete_profile_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    """
    사용자 ID를 기반으로 프로필 삭제 API
    """
    profile = crud.profile.get_by_user_id(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=404, detail="Profile not found for the given user_id"
        )
    delete_obj = crud.profile.remove(db, id=profile.id)
    return status.HTTP_204_NO_CONTENT


@router.delete("/profile/{user_id}/photo")
async def delete_profile_photo(
    user_id: int,
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
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

    delete_obj = crud.profile.remove_profile_photo(db=db, user_id=user_id)
    return status.HTTP_204_NO_CONTENT


@router.get("/profile/{user_id}", response_model=ProfileResponse)
def get_profile_by_user_id(
    user_id: int = Path(..., title="The ID of the user"),
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
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


@router.delete("/profile/{profile_id}")
def delete_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
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
    delete_obj = crud.profile.remove(db, id=profile_id)
    return status.HTTP_204_NO_CONTENT


@router.post("/profile", response_model=ProfileResponse)
def create_profile(
    profile: ProfileRegister,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
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
            - verification_status : 인증 상태 ["PENDING","APPROVE","REJECTED","UNVERIFIED"]
    """
    new_profile = None
    ava_list = []
    intro_list = []

    user = crud.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 사용자에게 이미 프로필이 있는지 확인
    if user.profile:
        raise HTTPException(
            status_code=409, detail="Profile already exists for the user"
        )

    available_language: List[AvailableLanguageCreate] = profile.available_languages
    if available_language:
        for ava_lang in available_language:
            lang = crud.utility.get(db=db, language_id=ava_lang.language_id)

            if not lang:
                raise HTTPException(status_code=404, detail="Languag not found")

    new_profile = crud.profile.create(db=db, obj_in=profile, user_id=user_id)
    return new_profile


@router.put(
    "/profile/{profile_id}",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
)
def update_profile(
    profile_id: int,
    profile_in: ProfileUpdate,
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
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

    try:
        new_profile = crud.profile.update(
            db=db, db_obj=existing_profile, obj_in=profile_in
        )
        return new_profile
    except Exception as e:
        log_error(e)
        raise HTTPException(status_code=500, detail="Error updating profile")


@router.get("/profile/{user_id}/meetings", response_model=MeetingListResponse)
def get_user_meetings(
    user_id: int,
    order_by: MeetingOrderingEnum = None,
    status: MyMeetingEnum = MyMeetingEnum.APPROVE.value,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    """
    User 모임 리스트

    - **status**
        - APPROVE : 승인 완료된 모임(현재 참여중인 모임)
        - Pending : 승인 대기중 모임
        - PAST : 과거 참여했던 모임
    """
    user = crud.user.get(db=db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")

    meetings, total_count = crud.profile.get_user_all_meetings(
        db=db, order_by=order_by, user_id=user_id, status=status, skip=skip, limit=limit
    )
    return {"meetings": meetings, "total_count": total_count}
