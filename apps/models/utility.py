from enum import Enum

from models.base import ModelBase
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship


class OsLanguage(str,Enum):
    EN = "english"
    KR = "korean"


class Nationality(ModelBase):
    kr_name = Column(String)
    en_name = Column(String)
    code = Column(String)

    # user_nationalities = relationship("UserNationality", back_populates="nationality")


class Language(ModelBase):
    kr_name = Column(String)
    en_name = Column(String)

    # available_language = relationship("AvailableLanguage", back_populates="language")


class University(ModelBase):
    kr_name = Column(String)
    en_name = Column(String)

    # user_university = relationship("UserUniversity", back_populates="university")
