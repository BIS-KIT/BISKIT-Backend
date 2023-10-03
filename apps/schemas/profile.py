from datetime import date
from pydantic import EmailStr, BaseModel
from enum import Enum
from typing import Optional, List, Union
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


class StudentVerificationBase(CoreSchema):
    profile_id: Optional[int] = None
    student_card: Optional[Union[str, UploadFile]] = None
    verification_status: Optional[str] = VerificationStatus.UNVERIFIED.value

    class Config:
        orm_mode = True


class StudentVerificationReponse(BaseModel):
    id: Optional[int] = None
    student_card: Optional[Union[str, UploadFile]] = None
    verification_status: str = VerificationStatus.UNVERIFIED.value

    class Config:
        orm_mode = True


class StudentVerificationCreate(BaseModel):
    profile_id: Optional[int] = None
    student_card: Optional[Union[str, UploadFile]] = None
    verification_status: str = VerificationStatus.UNVERIFIED.value


class StudentVerificationIn(BaseModel):
    student_card: Optional[Union[str, UploadFile]] = None
    verification_status: str = VerificationStatus.UNVERIFIED.value


class StudentVerificationUpdate(BaseModel):
    verification_status: Optional[str] = VerificationStatus.UNVERIFIED.value


class ProfileBase(CoreSchema):
    nick_name: Optional[str] = None
    profile_photo: Optional[Union[str, UploadFile]] = None
    user_id: Optional[int] = None


# 프로필 생성을 위한 스키마
class ProfileCreate(ProfileBase):
    class Config:
        orm_mode = True


class ProfilePhoto(BaseModel):
    profile_photo: str


class AvailableLanguageBase(CoreSchema):
    level: Optional[str] = None
    language: Optional[LanguageBase] = None
    profile_id: Optional[int] = None


class AvailableLanguageCreate(BaseModel):
    level: str
    language_id: int
    profile_id: Optional[int] = None


class AvailableLanguageIn(BaseModel):
    level: Optional[str] = None
    language_id: Optional[int] = None


class AvailableLanguageUpdate(BaseModel):
    level: Optional[str] = None
    language_id: Optional[int] = None


class AvailableLanguageResponse(AvailableLanguageBase):
    class Config:
        orm_mode = True


class IntroductionBase(CoreSchema):
    keyword: Optional[str] = None
    context: Optional[str] = None
    profile_id: int


class IntroductionResponse(IntroductionBase):
    class Config:
        orm_mode = True


class IntroductionCreate(BaseModel):
    keyword: Optional[str] = None
    context: Optional[str] = None
    profile_id: Optional[int] = None


class IntroductionIn(BaseModel):
    keyword: Optional[str] = None
    context: Optional[str] = None


class IntroductionUpdate(BaseModel):
    keyword: Optional[str] = None
    context: Optional[str] = None


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


class ProfileResponse(BaseModel):
    id: int = None
    user_id: int
    nick_name: Optional[str] = None
    profile_photo: Optional[str] = None
    available_languages: Optional[List[AvailableLanguageResponse]]
    introductions: Optional[List[IntroductionResponse]]
    student_verification: Optional[StudentVerificationReponse] = None

    class Config:
        orm_mode = True


class ProfileRegister(BaseModel):
    nick_name: Optional[str] = None
    profile_photo: Optional[str] = None
    available_languages: Optional[List[AvailableLanguageIn]]
    introductions: Optional[List[IntroductionIn]]
    student_card: Optional[StudentVerificationIn] = None


class ProfileUpdate(BaseModel):
    nick_name: Optional[str] = None
    profile_photo: Optional[str] = None
    # available_languages: Optional[List[AvailableLanguageIn]] = None
    # introductions: Optional[List[IntroductionIn]] = None
    # student_card: Optional[StudentVerificationIn] = None
