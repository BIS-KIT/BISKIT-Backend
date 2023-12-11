from datetime import datetime
from pydantic import BaseModel, computed_field, Field
from enum import Enum
from typing import Optional, List, Union

from schemas.base import CoreSchema
from schemas.utility import TagResponse, TopicResponse, LanguageBase
from schemas.user import UserSimpleResponse, UserResponse
from schemas.profile import AvailableLanguageResponse, ProfileBase
from schemas.enum import ReultStatusEnum, MeetingOrderingEnum, TimeFilterEnum


class MeetingBase(BaseModel):
    name: Optional[str]
    location: Optional[str]
    description: Optional[str] = None
    meeting_time: Optional[datetime]
    max_participants: Optional[int]

    chat_id: Optional[str] = None
    place_url: Optional[str] = None
    x_coord: Optional[str] = None
    y_coord: Optional[str] = None

    image_url: Optional[str] = None
    is_active: Optional[bool] = True


class MeetingUserBase(BaseModel):
    user: Optional[UserResponse]
    meeting_id: int
    status: Optional[str]
    created_time: Optional[datetime]


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


class MeetingCreate(MeetingBase):
    custom_tags: Optional[List[str]] = []
    custom_topics: Optional[List[str]] = []

    creator_id: Optional[int]
    tag_ids: Optional[List[int]] = []
    topic_ids: Optional[List[int]] = []
    language_ids: Optional[List[int]] = []


class MeetingUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    meeting_time: Optional[datetime] = None
    max_participants: Optional[int] = None
    place_url: Optional[str] = None
    x_coord: Optional[str] = None
    y_coord: Optional[str] = None
    image_url: Optional[str] = None

    custom_tags: Optional[List[str]] = []
    custom_topics: Optional[List[str]] = []

    tag_ids: Optional[List[int]] = []
    topic_ids: Optional[List[int]] = []
    language_ids: Optional[List[int]] = []


class MeetingUpdateIn(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    meeting_time: Optional[datetime] = None
    max_participants: Optional[int] = None
    place_url: Optional[str] = None
    x_coord: Optional[str] = None
    y_coord: Optional[str] = None
    image_url: Optional[str] = None


class MeetingIn(MeetingBase, MeetingCountBase):
    creator_id: Optional[int]
    university_id: Optional[int]


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
    chat_id: Optional[str] = None

    university_id: Optional[int]

    meeting_tags: Optional[List[MeetingTagBase]] = Field(..., exclude=True)
    meeting_topics: Optional[List[MeetingTopicBase]] = Field(..., exclude=True)
    meeting_languages: Optional[List[MeetingLanguageBase]] = Field(..., exclude=True)
    meeting_users: Optional[List[MeetingUserBase]] = Field(..., exclude=True)

    participants_status: Optional[str] = None

    @computed_field
    @property
    def tags(self) -> List[TagResponse]:
        return [meeting_tag.tag for meeting_tag in self.meeting_tags]

    class Config:
        orm_mode = True


class MeetingListResponse(BaseModel):
    total_count: int
    meetings: Optional[List[MeetingResponse]] = []


class MeetingUserLanguage(CoreSchema):
    level: Optional[str] = None
    language: Optional[LanguageBase] = None
    # profile: Optional[ProfileBase] = None

    # @computed_field
    # @property
    # def user_id(self) -> Optional[int]:
    #     return self.profile.user_id


class CommentBase(BaseModel):
    content: Optional[str]

    meeting_id: Optional[int]
    creator_id: Optional[int]
    parent_id: Optional[int] = None


class CommentCreate(CommentBase):
    class Config:
        orm_mode = True


class MeetingDetailResponse(MeetingResponse):
    creator: Optional[UserResponse] = None

    @computed_field
    @property
    def topics(self) -> List[TopicResponse]:
        return [meeting_topic.topic for meeting_topic in self.meeting_topics]

    @computed_field
    @property
    def languages(self) -> List[LanguageBase]:
        return [
            meeting_language.language for meeting_language in self.meeting_languages
        ]

    @computed_field
    @property
    def participants(self) -> List[UserResponse]:
        return [self.creator] + [
            instance.user
            for instance in self.meeting_users
            if instance.status == ReultStatusEnum.APPROVE.value
        ]


class MeetingUserResponse(CoreSchema, MeetingUserBase):
    class Config:
        orm_mode = True


class MeetingUserListResponse(BaseModel):
    total_count: int
    requests: Optional[List[MeetingUserResponse]] = []


class ReviewBase(BaseModel):
    context: Optional[str] = None
    image_url: Optional[str] = None


class ReviewPhotoBase(BaseModel):
    image_url: Optional[str]


class ReviwPhotoCreate(ReviewPhotoBase):
    review_id: str
    creator_id: int


class ReviewIn(ReviewBase):
    creator_id: int
    pass


class ReviewUpdateIn(ReviewBase):
    pass


class ReviewCreate(ReviewBase):
    meeting_id: int
    creator_id: int


class ReviewUpdate(ReviewBase):
    pass


class ReviewPhotoResponse(CoreSchema, ReviewPhotoBase):
    pass


class ReviewResponse(CoreSchema, ReviewBase):
    meeting_id: int = None
    creator: Optional[UserSimpleResponse] = None

    class Meta:
        orm_mode = True


class ReviewListReponse(BaseModel):
    total_count: int
    reviews: Optional[List[ReviewResponse]] = []


class ChatAlarm(BaseModel):
    chat_id: str
    content: str
    user_id: int
