from datetime import date
from pydantic import EmailStr, BaseModel
from enum import Enum
from typing import Optional, List
from fastapi import UploadFile

from schemas.base import CoreSchema
from schemas.utility import LanguageBase


class genderEum(str, Enum):
    MALE = "male"
    FEMALE = "female"


class LanguageLevel(Enum):
    BEGINNER = "초보"
    BASIC = "기초"
    INTERMEDIATE = "중급"
    ADVANCED = "고급"
    PROFICIENT = "능숙"


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    UNVERIFIED = "unverified"


class ProfileBase(CoreSchema):
    nick_name: Optional[str] = None
    profile_photo: Optional[str] = None


class ProfileUpdate(BaseModel):
    pass


class ProfilePhoto(BaseModel):
    profile_photo: str


class AvailableLanguageBase(CoreSchema):
    level: Optional[str] = None
    language: Optional[LanguageBase] = None
    profile_id: Optional[int] = None


class AvailableLanguageCreate(BaseModel):
    level: str
    language_id: int
    profile_id: int


class LanguageLevelSchema(CoreSchema):
    language_id: Optional[int] = None
    level: Optional[str] = None

    class Config:
        orm_mode = True


class IntroductionBaseSchema(CoreSchema):
    keyword: Optional[str] = None
    context: Optional[str] = None

    class Config:
        orm_mode = True


class IntroductionCreate(BaseModel):
    keyword: Optional[str] = None
    context: Optional[str] = None
    profile_id: int


class ProfileCreateLanguage(BaseModel):
    level: Optional[str]
    language_id: Optional[int]

    class Config:
        orm_mode = True


class IntroductCreateLanguage(BaseModel):
    keyword: Optional[str] = None
    context: Optional[str] = None

    class Config:
        orm_mode = True


class VerificationBase(CoreSchema):
    profile_id: Optional[int] = None
    student_card_image: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED.value

    class Config:
        orm_mode = True


class VerificationCreate(BaseModel):
    profile_id: Optional[int] = None
    student_card_image: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED.value


# 프로필 생성을 위한 스키마
class ProfileCreate(BaseModel):
    nick_name: Optional[str] = None
    profile_photo: Optional[UploadFile] = None


class CreateProfileSchema(BaseModel):
    nick_name: str
    user_id: int
    profile_photo: Optional[UploadFile] = None
    languages: List[ProfileCreateLanguage]
    introduction: List[IntroductCreateLanguage]
    verification: List[VerificationCreate]

    class Config:
        orm_mode = True


class UpdateProfileSchema(BaseModel):
    nick_name: Optional[str] = None
    profile_photo: Optional[UploadFile] = None
    languages: Optional[List[ProfileCreateLanguage]] = None
    introduction: Optional[List[IntroductCreateLanguage]] = None
    # verification: Optional[List[VerificationCreate]] = None

    class Config:
        orm_mode = True


class ProfileResponse(BaseModel):
    id: int = None
    user_id: int
    nick_name: Optional[str] = None
    profile_photo: Optional[str] = None
    available_languages: Optional[List[LanguageLevelSchema]]
    introductions: Optional[List[IntroductionBaseSchema]]
    verification: Optional[VerificationBase]

    class Config:
        orm_mode = True
