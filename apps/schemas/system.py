from pydantic import BaseModel
from typing import Optional, List

from schemas.base import CoreSchema
from schemas.user import UserSimpleResponse
from schemas.enum import ReultStatusEnum


class ReportBase(BaseModel):
    reason: str
    report_type: str
    status: str


class ReportCreate(ReportBase):
    target_id: int
    reporter_id: int


class ReportUpdate(ReportBase):
    target_id: int


class ReportResponse(BaseModel):
    target: UserSimpleResponse
    reporter: UserSimpleResponse


class SystemBase(BaseModel):
    system_language: str
    main_alarm: bool
    etc_alarm: bool


class SystemCreate(SystemBase):
    user_id: int


class SystemUpdate(SystemBase):
    pass


class SystemReponse(SystemBase):
    user: UserSimpleResponse


class NoticeBase(BaseModel):
    title: str
    content: str


class NoticeCreate(NoticeBase):
    user_id: int


class NoticeUpdate(NoticeBase):
    pass


class NoticeResponse(NoticeBase):
    user: UserSimpleResponse
