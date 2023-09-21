from datetime import date
from pydantic import EmailStr, BaseModel
from enum import Enum
from typing import Optional, List

from schemas.base import CoreSchema
from schemas.profile import (
    ProfileResponse,
    AvailableLanguageBase,
)


class UserBase(CoreSchema):
    email: EmailStr
    password: str
    name: str
    birth: date
    gender: str
    is_graduated: bool


class UserWithStatus(UserBase):
    is_active: bool = True
    is_admin: bool = False


# 유저 생성을 위한 스키마
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    birth: date
    nationality: str
    university: str
    department: str
    gender: str
    is_graduated: bool


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    birth: date
    nationality: str
    university: str
    department: str
    gender: str
    is_graduated: bool

    terms_mandatory: Optional[bool] = True
    terms_optional: Optional[bool] = False
    terms_push: Optional[bool] = False


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# 유저 업데이트를 위한 스키마
class UserUpdate(BaseModel):
    name: str
    birth: date
    nationality: str
    university: str
    department: str
    gender: str
    is_graduated: bool


class PasswordChange(CoreSchema):
    old_password: str
    new_password: str
    new_password_check: str


class PasswordUpdate(BaseModel):
    password: str


class ConsentBase(CoreSchema):
    terms_mandatory: Optional[bool] = False
    terms_optional: Optional[bool] = False
    terms_push: Optional[bool] = False
    user_id: Optional[int] = False


# 동의 생성을 위한 스키마
class ConsentCreate(BaseModel):
    terms_mandatory: Optional[bool]
    terms_optional: Optional[bool] = False
    terms_push: Optional[bool]
    user_id: int


# 동의 응답을 위한 스키마
class ConsentResponse(ConsentBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    UNVERIFIED = "unverified"


class StudentVerificationSchema(CoreSchema):
    user_id: Optional[int] = None
    student_card_image: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED.value


class FirebaseAuthBase(BaseModel):
    provider_id: Optional[str]
    uid: str
    firebase_token: Optional[str]


class FirebaseAuthCreate(FirebaseAuthBase):
    pass


class FirebaseAuthUpdate(FirebaseAuthBase):
    provider_id: Optional[str] = None
    firebase_token: Optional[str] = None


class FirebaseAuthResponse(FirebaseAuthBase):
    user_id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    email: str = None


class EmailCertificationIn(BaseModel):
    email: str


class EmailCertificationCheck(BaseModel):
    email: str
    certification: str


class UserUniversityBase(CoreSchema):
    department: Optional[str] = None
    user_university_id: Optional[int] = None
    user_id: Optional[int] = None


class UserNationalityBase(CoreSchema):
    nationality_id: Optional[int] = None
    user_id: Optional[int] = None


class UserResponse(BaseModel):
    email: str
    password: str
    name: str
    birth: date
    gender: str
    is_graduated: bool
    is_active: bool
    is_admin: bool

    profile: Optional[ProfileResponse] = None
    consents: Optional[ConsentResponse] = None
    verification: Optional[StudentVerificationSchema] = None
    available_language: Optional[List[AvailableLanguageBase]] = None
    user_university: Optional[UserUniversityBase] = None
    user_nationality: Optional[List[UserNationalityBase]] = None
