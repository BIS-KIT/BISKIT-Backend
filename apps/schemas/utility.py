from schemas.base import CoreSchema
from pydantic import EmailStr, BaseModel
from datetime import date
from typing import Optional


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
