from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from typing import Optional, List, Union

from schemas.base import CoreSchema
from schemas.utility import TagResponse, TopicResponse, LanguageBase
from schemas.user import UserSimpleResponse

class MeetingBase(BaseModel):
    name : Optional[str]
    location : Optional[str]
    description : Optional[str] = None
    meeting_time : Optional[datetime]
    max_participants : Optional[int]

    image_url : Optional[str] = None
    is_active : Optional[bool] = True

class MeetingUserBase(BaseModel):
    user_id : int
    meeting_id : int

class MeetingTagBase(BaseModel):
    pass

class MeetingTopicBase(BaseModel):
    pass

class MeetingLanguageBase(BaseModel):
    pass

class MeetingCountBase(BaseModel):
    current_participants : Optional[int] = 1
    korean_count : Optional[int] = 0
    foreign_count : Optional[int]= 0

class MeetingCountCreateUpdate(MeetingCountBase):
    pass

class MeetingCreateUpdate(MeetingBase, MeetingCountBase):

    custom_tags : Optional[List[str]]= []
    custom_topics : Optional[List[str]]= []

    creator_id : Optional[int]
    tag_ids : Optional[List[int]]= []
    topic_ids : Optional[List[int]]= []
    language_ids : Optional[List[int]]= []

class MeetingIn(MeetingBase, MeetingCountBase):
    creator_id : Optional[int]
    pass

class MeetingUserCreate(BaseModel):
    meeting_id : int
    user_id : int

class MeetingItemCreate(BaseModel):

    meeting_id : int
    tag_id : Optional[int]
    topic_id : Optional[int]
    language_id : Optional[int]

class MeetingResponse(CoreSchema,MeetingBase, MeetingCountBase):

    creator: Optional[UserSimpleResponse] = None

    meeting_tags : Optional[List[TagResponse]] = None
    meeting_topics : Optional[List[TopicResponse]] = None
    meeting_languages : Optional[List[LanguageBase]] = None

    participants_status : Optional[str] = None

    class Config:
        orm_mode=True

class MeetingUserResponse(CoreSchema, MeetingUserBase):
    class Config:
        orm_mode = True