from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from schemas.base import CoreSchema
from schemas.user import UserSimpleResponse
from schemas.enum import ReultStatusEnum


class ReportBase(BaseModel):
    reason: str


class ReportCreate(ReportBase):
    target_id: int
    reporter_id: int


class ReportCreateIn(ReportCreate):
    status: str = ReultStatusEnum.PENDING.value


class ReportUpdate(ReportBase):
    target_id: int


class ReportResponse(CoreSchema, BaseModel):
    created_time: datetime
    target: UserSimpleResponse
    reporter: UserSimpleResponse
    status: Optional[str]


class ReportListResponse(BaseModel):
    reports: List[ReportResponse]
    total_count: int


class SystemBase(BaseModel):
    system_language: str = "kr"
    main_alarm: bool = True
    etc_alarm: bool = True


class SystemCreate(SystemBase):
    user_id: int


class SystemUpdate(SystemBase):
    pass


class SystemReponse(CoreSchema, SystemBase):
    user: UserSimpleResponse


class BanBase(BaseModel):
    target_id: int


class BanCreate(BanBase):
    reporter_id: int


class BanUpdate(BanBase):
    pass


class BanResponse(CoreSchema, BaseModel):
    target: UserSimpleResponse


class BanListReponse(BaseModel):
    ban_list: List[BanResponse]
    total_count: int


class NoticeBase(BaseModel):
    title: str = None
    content: str = None


class NoticeCreate(NoticeBase):
    user_id: int


class NoticeUpdate(NoticeBase):
    pass


class NoticeResponse(CoreSchema, NoticeBase):
    user: UserSimpleResponse


class NoticeListResponse(BaseModel):
    notices: List[NoticeResponse]
    total_count: int


class ContactBase(BaseModel):
    content: str


class ContactCreate(ContactBase):
    user_id: int


class ContactResponse(ContactBase):
    user: UserSimpleResponse


class ContactListResponse(BaseModel):
    total_count: int
    contacts: List[ContactResponse]
