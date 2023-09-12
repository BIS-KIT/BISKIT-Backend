from models.base import ModelBase
from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship


class Profile(ModelBase):
    user_id = Column(Integer, ForeignKey("user.id"))
    first_name = Column(String)
    last_name = Column(String)
    birth = Column(Date)
    nationality = Column(String)
    university = Column(String, nullable=True)
    department = Column(String, nullable=True)
    gender = Column(String)
    is_graduated = Column(Boolean, default=False)
    user = relationship("User", back_populates="profile")
