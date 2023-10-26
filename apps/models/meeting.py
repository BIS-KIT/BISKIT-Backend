from sqlalchemy import Column, Integer, String,ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from models.base import ModelBase

class Meeting(ModelBase):
    name = Column(String)
    location = Column(String,nullable=True)
    description = Column(String,nullable=True)
    meeting_time = Column(DateTime, nullable=True)
    max_participants = Column(String)
    current_participants = Column(String,nullable=True)
    participants_status = Column(String,nullable=True)

    image_url = Column(String)
    is_active = Column(Boolean)

    meeting_tags = relationship("MeetingTag", back_populates="meeting")
    meeting_languages = relationship("MeetingLanguage", back_populates="meeting")
    meeting_topics = relationship("MeetingTopic", back_populates="meeting")
    meeting_users = relationship("MeetingUser", back_populates="meeting")


class MeetingUser(ModelBase):
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    meeting_id = Column(Integer, ForeignKey('meeting.id'), primary_key=True)
    
    user = relationship("User", backref="meeting_users")
    meeting = relationship("Meeting", back_populates="meeting_users")

class MeetingLanguage(ModelBase):
    
    meeting_id = Column(Integer, ForeignKey('meeting.id'))
    language_id = Column(Integer, ForeignKey('language.id'))

    meeting = relationship("Meeting", back_populates="meeting_languages")
    language = relationship("Language", backref="meeting_languages")

class MeetingTag(ModelBase):
    
    meeting_id = Column(Integer, ForeignKey("meeting.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True)
    
    meeting = relationship("Meeting", back_populates="meeting_tags")
    tag = relationship("Tag", backref="meeting_tags")


class MeetingTopic(ModelBase):
    
    meeting_id = Column(Integer, ForeignKey("meeting.id"), primary_key=True)
    topic_id = Column(Integer, ForeignKey("topic.id"), primary_key=True)
    
    meeting = relationship("Meeting", back_populates="meeting_topics")
    topic = relationship("Topic", backref="meeting_topics")