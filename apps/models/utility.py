from enum import Enum

from models.base import ModelBase
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship, validates


class OsLanguage(str, Enum):
    EN = "english"
    KR = "korean"


class Nationality(ModelBase):
    kr_name = Column(String)
    en_name = Column(String)
    code = Column(String)


class Language(ModelBase):
    kr_name = Column(String)
    en_name = Column(String)

    meeting_languages = relationship("MeetingLanguage", back_populates="language")


class University(ModelBase):
    kr_name = Column(String)
    en_name = Column(String)


class Tag(ModelBase):  

    name = Column(String) 

    metting_tags = relationship("MeetingTag", back_populates="tag")

class Topic(ModelBase):

    name = Column(String)

    metting_topics = relationship("MeetingTopic", back_populates="topic")