from models.base import ModelBase
from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship


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
