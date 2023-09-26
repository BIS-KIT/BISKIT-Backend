from datetime import date
from pydantic import EmailStr, BaseModel
from enum import Enum
from typing import Optional, List, Union

from schemas.base import CoreSchema
from schemas.profile import (
    ProfileResponse,
    AvailableLanguageBase,
)
from schemas.utility import UniversityBase, NationalityBase

from fastapi import UploadFile


class EducationStatus(str, Enum):
    UNDERGRADUATE = "학부"
    GRADUATE = "대학원"
    EXCHANGE_STUDENT = "교환학생"
    LANGUAGE_INSTITUTE = "어학당"


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    UNVERIFIED = "unverified"


class UserBase(CoreSchema):
    email: EmailStr
    password: str
    name: str
    birth: date
    gender: str


class UserWithStatus(UserBase):
    is_active: bool = True
    is_admin: bool = False


# 유저 생성을 위한 스키마
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    birth: date
    gender: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    birth: date
    gender: str

    nationality_ids: List[int] = None

    university_id: Optional[int] = None
    department: Optional[str] = None
    education_status: Optional[str] = None

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


class PasswordChange(CoreSchema):
    old_password: str
    new_password: str
    new_password_check: str


class PasswordUpdate(BaseModel):
    password: str


class ConsentBase(CoreSchema):
    terms_mandatory: Optional[bool] = True
    terms_optional: Optional[bool] = False
    terms_push: Optional[bool] = False
    user_id: Optional[int] = None


# 동의 생성을 위한 스키마
class ConsentCreate(ConsentBase):
    pass


# 동의 응답을 위한 스키마
class ConsentResponse(ConsentBase):
    pass

    class Config:
        orm_mode = True


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
    education_status: Optional[str] = None

    university: Optional[UniversityBase] = None
    user_id: Optional[int] = None

    class Config:
        orm_mode = True


class UserUniversityUpdate(BaseModel):
    department: Optional[str] = None
    education_status: Optional[str] = None
    university_id: Optional[int] = 0
    user_id: Optional[int] = 0


class UserUniversityCreate(BaseModel):
    department: Optional[str] = None
    education_status: Optional[str] = None
    university_id: Optional[int]
    user_id: Optional[int]


class UserNationalityBase(CoreSchema):
    nationality: Optional[NationalityBase]
    # nationality_id: Optional[int]
    user_id: Optional[int]

    class Config:
        orm_mode = True


class UserNationalityResponse(BaseModel):
    user_id: Optional[int]
    nationality: Optional[NationalityBase]

    class Config:
        orm_mode = True


class UserNationalityCreate(BaseModel):
    nationality_id: Optional[int]
    user_id: Optional[int]


class UserNationalityUpdate(BaseModel):
    nationality_id: Optional[int]


class StudentVerificationBase(CoreSchema):
    user_id: Optional[int] = None
    student_card: Optional[Union[str, UploadFile]] = None
    verification_status: Optional[str] = VerificationStatus.UNVERIFIED.value

    class Config:
        orm_mode = True


class StudentVerificationCreate(BaseModel):
    user_id: Optional[int] = None
    verification_status: str = VerificationStatus.UNVERIFIED.value


class StudentVerificationUpdate(BaseModel):
    verification_status: Optional[str] = VerificationStatus.UNVERIFIED.value


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    birth: date
    gender: str
    is_active: bool
    is_admin: bool

    profile: Optional[ProfileResponse] = None
    consents: Optional[List[ConsentResponse]] = None
    user_university: Optional[List[UserUniversityBase]] = None
    user_nationality: Optional[List[UserNationalityBase]] = None

    class Config:
        orm_mode = True
