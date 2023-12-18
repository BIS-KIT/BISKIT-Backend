from datetime import date, datetime
from pydantic import BaseModel

from typing import Optional, List, Union

from schemas.base import CoreSchema


class AlarmBase(BaseModel):
    title: str
    content: str
    is_read: Optional[bool] = False


class AlarmCreate(AlarmBase):
    user_id: int


class AlarmReponse(CoreSchema, AlarmBase):
    created_time: datetime


class AlarmListResponse(BaseModel):
    total_count: int
    alarms: Optional[List[AlarmReponse]] = []
