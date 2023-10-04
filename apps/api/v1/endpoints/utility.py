from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc

import crud
from database.session import get_db
from schemas.utility import LanguageBase, UniversityBase, NationalityBase
from models.utility import Language, University, Nationality, OsLanguage


router = APIRouter()


@router.get("/languages", response_model=List[LanguageBase])
def get_languages(
    os_language: OsLanguage = None,
    search: str = None,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 0,
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

    if skip and limit:
        languages = query.offset(skip).limit(limit).all()
    else:
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
    limit: int = 0,
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

    if skip and limit:
        universities = query.offset(skip).limit(limit).all()
    else:
        universities = query.all()

    return universities


@router.get("/nationality", response_model=List[NationalityBase])
def get_countries(
    os_language: OsLanguage = None,
    search: str = None,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 0,
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

    if skip and limit:
        countries = query.offset(skip).limit(limit).all()
    else:
        countries = query.all()

    return [NationalityBase.from_orm(country) for country in countries]
