from enum import Enum

from models.base import ModelBase
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship, validates


class OsLanguage(str, Enum):
    EN = "english"
    KR = "korean"


class Nationality(ModelBase):
    kr_name = Column(String)
    en_name = Column(String)
    code = Column(String)


class Language(ModelBase):
    kr_name = Column(String)
    en_name = Column(String)

class University(ModelBase):
    kr_name = Column(String)
    en_name = Column(String)


class Tag(ModelBase):  

    kr_name = Column(String, nullable=True)
    en_name = Column(String, nullable=True)
    is_custom = Column(Boolean, default=False)

class Topic(ModelBase):

    kr_name = Column(String, nullable=True)
    en_name = Column(String, nullable=True)
    is_custom = Column(Boolean, default=False)