from schemas.base import CoreSchema
from pydantic import EmailStr, BaseModel
from datetime import date
from typing import Optional


class LanguageBase(CoreSchema):
    name: Optional[str]


class UniversityBase(CoreSchema):
    name: Optional[str]


class NationalityBase(CoreSchema):
    name: Optional[str]
    code: Optional[str]
