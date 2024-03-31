from datetime import date
from pydantic import ConfigDict, BaseModel, computed_field, Field

from typing import Optional, List, Union
from fastapi import UploadFile

from schemas.base import CoreSchema
from schemas.utility import LanguageBase, UniversityBase
from schemas.enum import ReultStatusEnum, LanguageLevelEnum


class StudentVerificationBase(CoreSchema):
    profile_id: Optional[int] = None
    student_card: Optional[Union[str, UploadFile]] = None
    verification_status: Optional[str] = ReultStatusEnum.UNVERIFIED.value

    model_config = ConfigDict(from_attributes=True)


class StudentVerificationReponse(BaseModel):
    id: Optional[int] = None
    student_card: Optional[Union[str, UploadFile]] = None
    verification_status: str = ReultStatusEnum.UNVERIFIED.value

    model_config = ConfigDict(from_attributes=True)


class StudentVerificationCreate(BaseModel):
    profile_id: Optional[int] = None
    student_card: Optional[Union[str, UploadFile]] = None
    verification_status: str = ReultStatusEnum.UNVERIFIED.value


class StudentVerificationIn(BaseModel):
    student_card: Optional[Union[str, UploadFile]] = None
    verification_status: str = ReultStatusEnum.UNVERIFIED.value


class StudentVerificationUpdate(BaseModel):
    verification_status: Optional[str] = ReultStatusEnum.PENDING.value


class ProfileBase(CoreSchema):
    nick_name: Optional[str] = None
    profile_photo: Optional[Union[str, UploadFile]] = None
    user_id: Optional[int] = None
    is_default_photo: bool = False


# 프로필 생성을 위한 스키마
class ProfileCreate(ProfileBase):
    model_config = ConfigDict(from_attributes=True)


class ProfilePhoto(BaseModel):
    profile_photo: str


class AvailableLanguageBase(CoreSchema):
    level: Optional[str] = None
    language: Optional[LanguageBase] = None
    # profile_id: Optional[int] = None


class AvailableLanguageCreate(BaseModel):
    level: str
    language_id: int
    profile_id: Optional[int] = None

    class Meta:
        from_attributes = True


class AvailableLanguageIn(BaseModel):
    level: Optional[str] = None
    language_id: Optional[int] = None


class AvailableLanguageUpdate(BaseModel):
    level: Optional[str] = None
    language_id: Optional[int] = None


class AvailableLanguageResponse(AvailableLanguageBase):
    model_config = ConfigDict(from_attributes=True)


class IntroductionBase(CoreSchema):
    keyword: Optional[str] = None
    context: Optional[str] = None
    profile_id: int


class IntroductionResponse(IntroductionBase):
    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class IntroductCreateLanguage(BaseModel):
    keyword: Optional[str] = None
    context: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProfileUniversityBase(BaseModel):
    department: Optional[str] = None
    education_status: Optional[str] = None

    class Meta:
        from_attributes = True


class ProfileUniversityUpdate(ProfileUniversityBase):
    pass


class ProfileUniversityResponse(ProfileUniversityBase):
    university: Optional[UniversityBase] = None

    class Meta:
        from_attributes = True


class ProfileResponse(BaseModel):
    id: int = None
    user_id: int = None
    nick_name: Optional[str] = None
    is_default_photo: Optional[bool] = None
    context: Optional[str] = None
    profile_photo: Optional[str] = None
    available_language_list: Optional[List[AvailableLanguageResponse]] = Field(
        ..., exclude=True
    )
    introductions: Optional[List[IntroductionResponse]] = None
    student_verification: Optional[StudentVerificationReponse] = None
    user_university: Optional[ProfileUniversityResponse] = None

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def available_languages(self) -> List[AvailableLanguageResponse]:
        if self.available_language_list:
            return_obj = sorted(
                self.available_language_list,
                key=lambda lang: LanguageLevelEnum[lang.level].value,
                reverse=False,  # 내림차순 정렬을 원할 경우 True로 설정
            )
            return return_obj
        return []


class ProfileRegister(BaseModel):
    nick_name: Optional[str] = None
    profile_photo: Optional[str] = None
    is_default_photo: Optional[bool] = False
    available_languages: Optional[List[AvailableLanguageIn]]
    introductions: Optional[List[IntroductionIn]] = None
    student_card: Optional[StudentVerificationIn] = None


class ProfileUpdate(BaseModel):
    nick_name: Optional[str] = None
    context: Optional[str] = None
    profile_photo: Optional[str] = None
    is_default_photo: Optional[bool] = None
    available_languages: Optional[List[AvailableLanguageIn]] = None
    introductions: Optional[List[IntroductionIn]] = None
    university_info: Optional[ProfileUniversityUpdate] = None
