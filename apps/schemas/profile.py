from datetime import date
from pydantic import EmailStr, BaseModel
from enum import Enum
from typing import Optional
from fastapi import UploadFile

from schemas.base import CoreSchema


class genderEum(str, Enum):
    MALE = "male"
    FEMALE = "female"


class ProfileBase(CoreSchema):
    nick_name: Optional[str] = None
    profile_photo: Optional[UploadFile] = None


# 프로필 생성을 위한 스키마
class ProfileCreate(BaseModel):
    nick_name: Optional[str] = None
    profile_photo: Optional[UploadFile] = None


class ProfileUpdate(ProfileCreate):
    pass


class ProfileResponse(ProfileBase):
    id: int  # 프로필에 대한 고유 ID를 가정

    class Config:
        orm_mode = True


class ProfilePhoto(BaseModel):
    profile_photo: str
