from datetime import date
from pydantic import EmailStr, BaseModel
from enum import Enum
from typing import Optional
from fastapi import UploadFile

from schemas.base import CoreSchema


class genderEum(str, Enum):
    MALE = "male"
    FEMALE = "female"


class LanguageLevel(Enum):
    BEGINNER = "초보"
    BASIC = "기초"
    INTERMEDIATE = "중급"
    ADVANCED = "고급"
    PROFICIENT = "능숙"


class ProfileBase(CoreSchema):
    nick_name: Optional[str] = None
    profile_photo: Optional[str] = None


# 프로필 생성을 위한 스키마
class ProfileCreate(BaseModel):
    nick_name: Optional[str] = None
    profile_photo: Optional[UploadFile] = None


class ProfileUpdate(ProfileCreate):
    pass


class ProfileResponse(ProfileBase):
    id: int = None

    class Config:
        orm_mode = True


class ProfilePhoto(BaseModel):
    profile_photo: str


class AvailableLanguageBase(CoreSchema):
    level: Optional[str] = None
    language_id: Optional[int] = None
    user_id: Optional[int] = None


class AvailableLanguageCreate(BaseModel):
    level: str
    language_id: int
    user_id: int
