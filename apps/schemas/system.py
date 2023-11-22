from pydantic import BaseModel
from typing import Optional, List

from schemas.base import CoreSchema
from schemas.user import UserSimpleResponse
from schemas.enum import ReultStatusEnum


class ReportBase(BaseModel):
    reason: str
    report_type: str
    status: str = ReultStatusEnum.PENDING.value


class ReportCreate(ReportBase):
    target_id: int
    reporter_id: int


class ReportUpdate(ReportBase):
    target_id: int


class ReportResponse(BaseModel):
    target: UserSimpleResponse
    reporter: UserSimpleResponse


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
    reporter_id: int


class BanCreate(BanBase):
    pass


class BanUpdate(BanBase):
    pass


class BanResponse(CoreSchema, BaseModel):
    target: UserSimpleResponse
    reporter: UserSimpleResponse


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
