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
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    name: str
    birth: date
    gender: str
    sns_type: Optional[str] = None
    sns_id: Optional[str] = None
    fcm_token: Optional[str] = None


class UserRegister(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    name: str
    birth: date
    gender: str

    sns_type: Optional[str] = None
    sns_id: Optional[str] = None
    fcm_token: Optional[str] = None

    nationality_ids: List[int] = None

    university_id: Optional[int] = None
    department: Optional[str] = None
    education_status: Optional[str] = None

    terms_mandatory: Optional[bool] = True
    terms_optional: Optional[bool] = False
    terms_push: Optional[bool] = False


class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    sns_type: Optional[str] = None
    sns_id: Optional[str] = None
    fcm_token: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    birth: Optional[date] = None
    gender: Optional[str] = None
    nationality_ids: Optional[List[int]] = None
    university_id: Optional[int] = None
    department: Optional[str] = None
    education_status: Optional[str] = None


class UserBaseUpdate(BaseModel):
    name: Optional[str]
    birth: Optional[date]
    gender: Optional[str]


class PasswordChange(BaseModel):
    new_password: str


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
    email: Optional[EmailStr] = None


class EmailCertificationIn(BaseModel):
    email: Optional[EmailStr] = None


class EmailCertificationCheck(BaseModel):
    email: Optional[EmailStr] = None
    certification: Union[str, int]


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
    university_id: Optional[int] = None
    user_id: Optional[int] = None


class UserUniversityUpdateIn(BaseModel):
    department: Optional[str] = None
    education_status: Optional[str] = None
    university_id: Optional[int] = None


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


class UserResponse(BaseModel):
    id: int
    email: Optional[EmailStr] = None
    name: str = None
    birth: date = None
    gender: str = None
    is_active: bool = None
    is_admin: bool = None
    sns_type: Optional[str] = None
    # sns_id: Optional[str] = None
    fcm_token: Optional[str] = None

    profile: Optional[ProfileResponse] = None
    consents: Optional[List[ConsentResponse]] = None
    user_university: Optional[List[UserUniversityBase]] = None
    user_nationality: Optional[List[UserNationalityBase]] = None

    class Config:
        orm_mode = True


class UserSimpleResponse(CoreSchema):
    email: Optional[EmailStr]
    name: Optional[str]
    birth: Optional[date]
    gender: Optional[str]
    user_nationality: Optional[List[UserNationalityBase]] = None

    class Config:
        orm_mode = True
