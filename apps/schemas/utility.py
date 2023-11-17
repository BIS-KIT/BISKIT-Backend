from pydantic import EmailStr, BaseModel
from datetime import date
from typing import Optional

from schemas.base import CoreSchema
from models.utility import Nationality


class LanguageBase(CoreSchema):
    kr_name: Optional[str] = None
    en_name: Optional[str] = None


class UniversityBase(CoreSchema):
    kr_name: Optional[str] = None
    en_name: Optional[str] = None


class NationalityBase(CoreSchema):
    kr_name: Optional[str] = None
    en_name: Optional[str] = None

    code: Optional[str] = None

    @classmethod
    def from_orm(cls, nationality: Nationality):
        return cls(
            id=nationality.id,
            kr_name=nationality.kr_name,
            en_name=nationality.en_name,
            code=nationality.code.lower(),  # 이 부분에서 소문자로 변환합니다.
        )


class TopicBase(BaseModel):
    kr_name: Optional[str] = None
    en_name: Optional[str] = None
    is_custom: Optional[bool] = True
    icon_url: Optional[str] = None


class TagBase(BaseModel):
    kr_name: Optional[str] = None
    en_name: Optional[str] = None
    is_custom: Optional[bool] = True
    icon_url: Optional[str] = None


class TopicCreate(TopicBase):
    pass


class TagCreate(TopicBase):
    pass


class TopicResponse(TopicBase, CoreSchema):
    class Config:
        orm_mode = True


class TagResponse(TagBase, CoreSchema):
    class Config:
        orm_mode = True
