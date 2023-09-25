from pydantic import EmailStr, BaseModel
from datetime import date
from typing import Optional

from schemas.base import CoreSchema
from models.utility import Nationality


class LanguageBase(CoreSchema):
    kr_name: Optional[str]
    en_name: Optional[str]


class UniversityBase(CoreSchema):
    kr_name: Optional[str]
    en_name: Optional[str]


class NationalityBase(CoreSchema):
    kr_name: Optional[str]
    en_name: Optional[str]

    code: Optional[str]

    @classmethod
    def from_orm(cls, nationality: Nationality):
        return cls(
            id=nationality.id,
            kr_name=nationality.kr_name,
            en_name=nationality.en_name,
            code=nationality.code.lower(),  # 이 부분에서 소문자로 변환합니다.
        )
