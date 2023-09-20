from schemas.base import CoreSchema
from pydantic import EmailStr, BaseModel
from datetime import date
from typing import Optional


class LanguageBase(CoreSchema):
    name: str


class UniversityBase(CoreSchema):
    name: str


class NationalityBase(CoreSchema):
    name: str
    code: str
