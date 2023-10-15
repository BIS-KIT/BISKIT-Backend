from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship

from models.base import ModelBase

class ChatImage(ModelBase):
    image_url = Column(String)
    chat_id = Column(String)
    message_id = Column(String)