from schemas.base import CoreSchema
from datetime import date
from pydantic import EmailStr, BaseModel
from enum import Enum
from typing import Optional


class genderEum(str, Enum):
    MALE = "male"
    FEMALE = "female"


class ProfileBase(CoreSchema):
    first_name: str
    last_name: str
    nick_name: Optional[str] = None
    birth: Optional[date] = None
    nationality: Optional[bool] = None
    gender: genderEum
    is_graduated: bool
    university: Optional[str] = None
    department: Optional[str] = None
    profile_photo: Optional[str] = None  # 이미지 URL 저장


# 프로필 생성을 위한 스키마
class ProfileCreate(BaseModel):
    first_name: str
    last_name: str
    nick_name: Optional[str] = None
    birth: Optional[date] = None
    nationality: Optional[str] = None
    gender: genderEum
    is_graduated: Optional[bool] = None
    university: Optional[str] = None
    department: Optional[str] = None


# 프로필 업데이트를 위한 스키마
class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nick_name: Optional[str] = None
    birth: Optional[date] = None
    nationality: Optional[str] = None
    gender: genderEum
    is_graduated: Optional[bool] = None
    university: Optional[str] = None
    department: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: int  # 프로필에 대한 고유 ID를 가정

    class Config:
        orm_mode = True
