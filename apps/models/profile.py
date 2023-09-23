from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship

from models.base import ModelBase


class Profile(ModelBase):
    profile_photo = Column(String, nullable=True)  # 이미지 URL 저장
    nick_name = Column(String)

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="profile")


class AvailableLanguage(ModelBase):
    level = Column(String)

    language_id = Column(Integer, ForeignKey("language.id", ondelete="SET NULL"))
    language = relationship("Language", back_populates="available_language")

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    user = relationship("User", backref="available_language")
