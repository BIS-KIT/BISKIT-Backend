from datetime import datetime
from pydantic import BaseModel, computed_field, Field
from enum import Enum
from typing import Optional, List, Union

from schemas.base import CoreSchema
from schemas.utility import TagResponse, TopicResponse, LanguageBase
from schemas.user import UserSimpleResponse


class MeetingOrderingEnum(str, Enum):
    CREATED_TIME = "created_time"
    MEETING_TIME = "meeting_time"
    DEADLINE_SOON = "deadline_soon"


class MeetingBase(BaseModel):
    name: Optional[str]
    location: Optional[str]
    description: Optional[str] = None
    meeting_time: Optional[datetime]
    max_participants: Optional[int]

    chat_id: Optional[str] = None
    x_coord: Optional[str] = None
    y_coord: Optional[str] = None

    image_url: Optional[str] = None
    is_active: Optional[bool] = True


class MeetingUserBase(BaseModel):
    user_id: int
    meeting_id: int


class MeetingTagBase(BaseModel):
    tag: Optional[TagResponse]

    class Config:
        orm_mode = True


class MeetingTopicBase(BaseModel):
    topic: Optional[TopicResponse]

    class Config:
        orm_mode = True


class MeetingLanguageBase(BaseModel):
    language: Optional[LanguageBase]

    class Config:
        orm_mode = True


class MeetingCountBase(BaseModel):
    current_participants: Optional[int] = 1
    korean_count: Optional[int] = 0
    foreign_count: Optional[int] = 0


class MeetingCountCreateUpdate(MeetingCountBase):
    pass


class MeetingCreateUpdate(MeetingBase):
    custom_tags: Optional[List[str]] = []
    custom_topics: Optional[List[str]] = []

    creator_id: Optional[int]
    tag_ids: Optional[List[int]] = []
    topic_ids: Optional[List[int]] = []
    language_ids: Optional[List[int]] = []


class MeetingIn(MeetingBase, MeetingCountBase):
    creator_id: Optional[int]
    pass


class MeetingUserCreate(BaseModel):
    meeting_id: int
    user_id: int


class MeetingItemCreate(BaseModel):
    meeting_id: int
    tag_id: Optional[int]
    topic_id: Optional[int]
    language_id: Optional[int]


class MeetingResponse(CoreSchema, MeetingBase, MeetingCountBase):
    created_time: Optional[datetime] = None
    creator: Optional[UserSimpleResponse] = None

    meeting_tags: Optional[List[MeetingTagBase]] = Field(..., exclude=True)
    meeting_topics: Optional[List[MeetingTopicBase]] = Field(..., exclude=True)
    meeting_languages: Optional[List[MeetingLanguageBase]] = Field(..., exclude=True)

    participants_status: Optional[str] = None

    @computed_field
    @property
    def tags(self) -> List[TagResponse]:
        return [meeting_tag.tag for meeting_tag in self.meeting_tags]

    class Config:
        orm_mode = True


class MeetingListResponse(BaseModel):
    total_count: int
    meetings: List[MeetingResponse]


class MeetingDetailResponse(MeetingResponse):
    @computed_field
    @property
    def topics(self) -> List[TopicResponse]:
        return [meeting_topic.topic for meeting_topic in self.meeting_topics]

    @computed_field
    @property
    def languages(self) -> List[TopicResponse]:
        return [
            meeting_language.language for meeting_language in self.meeting_languages
        ]


class MeetingUserResponse(CoreSchema, MeetingUserBase):
    class Config:
        orm_mode = True
