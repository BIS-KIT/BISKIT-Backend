from schemas.base import CoreSchema
from datetime import date
from pydantic import EmailStr, BaseModel
from enum import Enum
from typing import Optional


class UserBase(CoreSchema):
    email: EmailStr
    password: str


class UserWithStatus(UserBase):
    is_active: bool = False
    is_admin: bool = False


# 유저 생성을 위한 스키마
class UserCreate(UserBase):
    pass


# 유저 업데이트를 위한 스키마
class UserUpdate(UserBase):
    email: Optional[EmailStr] = None


# 유저 응답을 위한 스키마
class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


class PasswordChange(CoreSchema):
    old_password: str
    new_password: str
    new_password_check: str


class ConsentBase(CoreSchema):
    terms_mandatory: Optional[bool]
    terms_optional: Optional[bool] = False
    terms_push: Optional[bool]
    user_id: int


# 동의 생성을 위한 스키마
class ConsentCreate(ConsentBase):
    pass


# 동의 응답을 위한 스키마
class ConsentResponse(ConsentBase):
    id: int

    class Config:
        orm_mode = True


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    UNVERIFIED = "unverified"


class StudentVerificationSchema(CoreSchema):
    user_id: int
    student_card_image: str
    verification_status: VerificationStatus


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
    token_type: str


class TokenData(BaseModel):
    email: str = None
