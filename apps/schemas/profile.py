from schemas.base import CoreSchema
from datetime import date
from pydantic import EmailStr, BaseModel
from enum import Enum
from typing import Optional


class ProfileBase(CoreSchema):
    first_name: str
    last_name: str
    birth: date
    nationality: str
    gender: str
    is_graduated: bool
    university: Optional[str] = None
    department: Optional[str] = None
    profile_photo: Optional[str] = None  # 이미지 URL 저장



# 프로필 생성을 위한 스키마
class ProfileCreate(ProfileBase):
    pass


# 프로필 업데이트를 위한 스키마
class ProfileUpdate(ProfileBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth: Optional[date] = None
    nationality: Optional[str] = None
    gender: Optional[str] = None
    is_graduated: Optional[bool] = None
    university: Optional[str] = None
    department: Optional[str] = None
    profile_photo: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: int  # 프로필에 대한 고유 ID를 가정

    class Config:
        orm_mode = True
