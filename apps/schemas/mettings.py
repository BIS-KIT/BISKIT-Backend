from datetime import date
from pydantic import BaseModel
from enum import Enum
from typing import Optional, List, Union

from schemas.base import CoreSchema
from schemas.utility import TagResponse, TopicResponse, LanguageBase

class meetingBase(BaseModel):
    name : Optional[str]
    location : Optional[str]
    description : Optional[str]
    meeting_time : Optional[date]
    max_participants : Optional[str]
    current_participants : Optional[str]
    participants_status : Optional[str]

    image_url : Optional[str]
    is_active : bool = True

class meetingUserBase(BaseModel):
    user_id : int
    meeting_id : int

class meetingTagBase(BaseModel):
    pass

class meetingTopicBase(BaseModel):
    pass

class meetingLanguageBase(BaseModel):
    pass

class meetingCreateUpdate(meetingBase):
    tag_ids : Optional[List[int]]
    topic_ids : Optional[List[int]]
    language_ids : Optional[List[int]]

class meetingUserCreate(BaseModel):
    meeting_id : int
    user_id : int

class meetingItemCreate(BaseModel):

    meeting_id : int
    tag_ids : Optional[List[int]]
    topic_ids : Optional[List[int]]
    language_ids : Optional[List[int]]

class meetingResponse(CoreSchema,meetingBase):

    meeting_tags : Optional[List[TagResponse]]
    meeting_topics : Optional[List[TopicResponse]]
    meeting_languages : Optional[List[LanguageBase]]

    class Config:
        orm_mode=True

class meetingUserResponse(CoreSchema, meetingUserBase):
    class Config:
        orm_mode = True