from typing import Any, List, Optional, Dict, Annotated

from fastapi import APIRouter, Body, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc

import crud
from core.security import oauth2_scheme
from log import log_error
from database.session import get_db
from schemas.utility import (
    LanguageBase,
    UniversityBase,
    NationalityBase,
    TagResponse,
    TopicResponse,
)
from schemas.enum import ImageSourceEnum
from models.utility import Language, University, Nationality, OsLanguage
from core.redis_driver import redis_driver

router = APIRouter()


@router.get("/languages", response_model=List[LanguageBase])
def get_languages(
    os_language: OsLanguage = None,
    search: str = None,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: Optional[int] = None,
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    """
    데이터베이스에서 언어 목록을 검색하여 반환합니다.

    매개변수:
    - os_language (OsLanguage, 선택사항): EN / KR
    - search (str, 선택사항): 영어 또는 한국어 이름으로 언어를 필터링하기 위한 키워드입니다.
    - db (Session): FastAPI의 의존성 주입을 통해 제공되는 데이터베이스 세션입니다.

    반환값:
    - List[LanguageBase]: 지정된 조건에 맞는 언어 객체의 목록입니다.
    """

    if search:
        query = db.query(Language).filter(
            or_(
                Language.en_name.ilike(f"%{search}%"),
                Language.kr_name.ilike(f"%{search}%"),
            )
        )
    else:
        query = db.query(Language)

    query = query.offset(skip)

    if limit is not None:
        query = query.limit(limit)

    languages = query.all()

    if os_language and os_language.value == OsLanguage.EN:
        # Extract the objects for id=1 and id=2
        id1_obj = next((lang for lang in languages if lang.id == 1), None)
        id2_obj = next((lang for lang in languages if lang.id == 2), None)

        # If both objects are found, swap their positions
        if id1_obj and id2_obj:
            index_id1 = languages.index(id1_obj)
            index_id2 = languages.index(id2_obj)
            languages[index_id1], languages[index_id2] = id2_obj, id1_obj

    return languages


@router.get("/universty", response_model=List[UniversityBase])
def get_universities(
    os_language: OsLanguage = None,
    search: str = None,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: Optional[int] = None,
):
    if search:
        query = db.query(University).filter(
            or_(
                University.en_name.ilike(f"%{search}%"),
                University.kr_name.ilike(f"%{search}%"),
            )
        )
    else:
        query = db.query(University)

    query = query.offset(skip)

    if limit is not None:
        query = query.limit(limit)

    universities = query.all()

    return universities


@router.get("/nationality", response_model=List[NationalityBase])
def get_countries(
    os_language: OsLanguage = None,
    search: str = None,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: Optional[int] = None,
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    if search:
        query = db.query(Nationality).filter(
            or_(
                Nationality.en_name.ilike(f"%{search}%"),
                Nationality.kr_name.ilike(f"%{search}%"),
            )
        )
    else:
        query = db.query(Nationality)

    if os_language and os_language.value == OsLanguage.EN:
        query = query.order_by(Nationality.en_name)
    else:
        query = query.order_by(Nationality.id)

    query = query.offset(skip)

    if limit is not None:
        query = query.limit(limit)

    countries = query.all()

    return [NationalityBase.from_orm(country) for country in countries]


@router.get("/tags", response_model=List[TagResponse])
def read_tags(
    is_custom: bool = None,
    is_home: bool = False,
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    """
    is_costem == None : 모든 tag
    is_costem == True : 사용자가 생성한 tag
    is_costem == False : 고정 tag

    is_home == True : home 화면에서 보여지는 tag 리스트
    is_home == False : default, 영향 x
    """

    return crud.utility.read_tags(db=db, is_custom=is_custom, is_home=is_home)


@router.get("/topics", response_model=List[TopicResponse])
def read_topics(
    is_custom: bool = None,
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    """
    is_costem == None : 모든 tag
    is_costem == True : 사용자가 생성한 tag
    is_costem == False : 고정 tag
    """

    return crud.utility.read_topics(db=db, is_custom=is_custom)


@router.post("/upload/image")
def upload_image_to_s3(
    image_source: ImageSourceEnum,
    photo: UploadFile,
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    """
    s3 upload

    - **image_source**
        - PROFILE : /profile_photo 저장
        - STUDENT_CARD : /student_card 저장
        - REVIEW : /review 저장
        - CHATTING : /chat_file 저장

    ** Return **
    - image_url : image 주소
    """
    file_path = None
    if image_source == ImageSourceEnum.PROFILE.value:
        file_path = f"profile_photo/{crud.generate_random_string()}_{photo.filename}"
    elif image_source == ImageSourceEnum.STUDENT_CARD.value:
        file_path = f"student_card/{crud.generate_random_string()}_{photo.filename}"
    elif image_source == ImageSourceEnum.REVIEW.value:
        file_path = f"review/{crud.generate_random_string()}_{photo.filename}"
    elif image_source == ImageSourceEnum.CHATTING.value:
        file_path = f"chat_file/{crud.generate_random_string()}_{photo.filename}"

    try:
        image_url = crud.save_upload_file(upload_file=photo, destination=file_path)
    except Exception as e:  # 어떤 예외든지 캐치합니다.
        log_error(e)
        # 클라이언트에게 에러 메시지와 상태 코드를 반환합니다.
        raise HTTPException(status_code=500)
    return {"image_url": image_url}


@router.get("/icon/setting")
def set_icon(
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    crud.utility.set_default_icon(db=db)


@router.get("/icon/png")
def set_png(
    db: Session = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
):
    crud.utility.png_to_svg(db=db)


@router.get("/check-cache/{key}")
async def get_value(key: str):
    """
    Cache에 저장된 값 확인
    """
    if not redis_driver.redis_client:
        raise HTTPException(status_code=503, detail="Redis connection not initialized")
    value = await redis_driver.redis_client.get(key, encoding="utf-8")
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "value": value}
