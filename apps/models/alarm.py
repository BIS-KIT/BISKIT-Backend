from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship, backref

from models.base import ModelBase


class Alarm(ModelBase):
    title = Column(String, nullable=True)
    content = Column(String, nullable=True)
    is_read = Column(String, default=False)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref=backref("alarms", cascade="all, delete-orphan"))
