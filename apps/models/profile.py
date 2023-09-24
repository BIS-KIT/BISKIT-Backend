from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship

from models.base import ModelBase


class Profile(ModelBase):
    profile_photo = Column(String, nullable=True)  # 이미지 URL 저장
    nick_name = Column(String)

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="profile")

    available_languages = relationship("AvailableLanguage", back_populates="profile")
    introductions = relationship("Introduction", back_populates="profile")
    verification = relationship("Verification", back_populates="profile", uselist=False)


class AvailableLanguage(ModelBase):
    level = Column(String)

    language_id = Column(Integer, ForeignKey("language.id", ondelete="SET NULL"))
    language = relationship("Language", backref="available_language")

    profile_id = Column(Integer, ForeignKey("profile.id", ondelete="CASCADE"))
    profile = relationship("Profile", back_populates="available_languages")


class Introduction(ModelBase):
    keyword = Column(String)
    context = Column(Text)

    profile_id = Column(Integer, ForeignKey("profile.id", ondelete="CASCADE"))
    profile = relationship("Profile", back_populates="introductions")


class Verification(ModelBase):
    # 학생증 사진의 파일 경로나 URL을 저장하는 필드
    student_card_image = Column(String)
    verification_status = Column(String, default="pending")

    profile_id = Column(Integer, ForeignKey("profile.id", ondelete="CASCADE"))
    profile = relationship("Profile", back_populates="verification")
