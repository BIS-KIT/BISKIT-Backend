from models.base import ModelBase
from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship


class Profile(ModelBase):
    first_name = Column(String)
    last_name = Column(String)
    nick_name = Column(String)
    birth = Column(Date)
    nationality = Column(String)
    university = Column(String, nullable=True)
    department = Column(String, nullable=True)
    gender = Column(String)
    is_graduated = Column(Boolean, default=False)
    profile_photo = Column(String, nullable=True)  # 이미지 URL 저장

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="profile")
