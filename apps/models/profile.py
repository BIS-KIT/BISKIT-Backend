from models.base import ModelBase
from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship


class Profile(ModelBase):
    profile_photo = Column(String, nullable=True)  # 이미지 URL 저장
    nick_name = Column(String)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="profile")
