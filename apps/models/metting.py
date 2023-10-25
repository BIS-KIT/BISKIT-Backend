from sqlalchemy import Column, Integer, String,ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from models.base import ModelBase

class Metting(ModelBase):
    name = Column(String)
    location = Column(String,nullable=True)
    description = Column(String,nullable=True)
    metting_time = Column(DateTime, nullable=True)
    max_participants = Column(String)
    current_participants = Column(String,nullable=True)
    participants_status = Column(String,nullable=True)

    image_url = Column(String)
    is_active = Column(Boolean)

    metting_tags = relationship("MeetingTag", back_populates="meeting")
    metting_languages = relationship("MeetingLanguage", back_populates="meeting")
    meeting_users = relationship("UserMeeting", back_populates="meeting")


class MettingUser(ModelBase):
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    meeting_id = Column(Integer, ForeignKey('metting.id'), primary_key=True)
    
    user = relationship("User", back_populates="meeting_users")
    meeting = relationship("Metting", back_populates="meeting_users")

class MeetingLanguage(ModelBase):
    
    meeting_id = Column(Integer, ForeignKey('meeting.id'))
    language_id = Column(Integer, ForeignKey('language.id'))

    meeting = relationship("Meeting", back_populates="metting_languages")
    language = relationship("Language", back_populates="metting_languages")

class MeetingTag(ModelBase):
    
    meeting_id = Column(Integer, ForeignKey("meeting.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True)
    
    meeting = relationship("Meeting", back_populates="metting_tags")
    tag = relationship("Tag", back_populates="metting_tags")


class MeetingTopic(ModelBase):
    
    meeting_id = Column(Integer, ForeignKey("meetings.id"), primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), primary_key=True)
    
    meeting = relationship("Meeting", back_populates="metting_topics")
    topic = relationship("Topic", back_populates="metting_topics")