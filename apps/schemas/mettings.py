from datetime import date
from pydantic import BaseModel
from enum import Enum
from typing import Optional, List, Union

from schemas.base import CoreSchema
from schemas.utility import TagResponse, TopicResponse, LanguageBase

class MettingBase(BaseModel):
    name : Optional[str]
    location : Optional[str]
    description : Optional[str]
    metting_time : Optional[date]
    max_participants : Optional[str]
    current_participants : Optional[str]
    participants_status : Optional[str]

    image_url : Optional[str]
    is_active : bool = True

class MettingUserBase(BaseModel):
    user_id : int
    metting_id : int

class MettingTagBase(BaseModel):
    pass

class MettingTopicBase(BaseModel):
    pass

class MettingLanguageBase(BaseModel):
    pass

class MettingCreateUpdate(MettingBase):
    tag_ids : Optional[List[int]]
    topic_ids : Optional[List[int]]
    language_ids : Optional[List[int]]

class MettingUserCreate(BaseModel):
    metting_id : int
    user_id : int

class MettingItemCreate(BaseModel):

    metting_id : int
    tag_ids : Optional[List[int]]
    topic_ids : Optional[List[int]]
    language_ids : Optional[List[int]]

class MettingResponse(CoreSchema,MettingBase):

    metting_tags : Optional[List[TagResponse]]
    metting_topics : Optional[List[TopicResponse]]
    metting_languages : Optional[List[LanguageBase]]

    class Config:
        orm_mode=True

class MettingUserResponse(CoreSchema, MettingUserBase):
    class Config:
        orm_mode = True