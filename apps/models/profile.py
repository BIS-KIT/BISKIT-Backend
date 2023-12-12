from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship

from models.base import ModelBase


class Profile(ModelBase):
    profile_photo = Column(String, nullable=True)  # 이미지 URL 저장
    nick_name = Column(String)
    context = Column(String, nullable=True)
    is_default_photo = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="profile")

    available_language_list = relationship(
        "AvailableLanguage", back_populates="profile", cascade="all, delete-orphan"
    )
    introductions = relationship(
        "Introduction", back_populates="profile", cascade="all, delete-orphan"
    )
    student_verification = relationship(
        "StudentVerification",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan",
    )
    user_university = relationship(
        "UserUniversity",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan",
    )


class UserUniversity(ModelBase):
    department = Column(String, nullable=True)
    education_status = Column(String, nullable=True)

    user_id = Column(Integer, nullable=True)

    university_id = Column(Integer, ForeignKey("university.id", ondelete="CASCADE"))
    university = relationship("University", backref="user_university")

    profile_id = Column(
        Integer, ForeignKey("profile.id", ondelete="CASCADE"), nullable=True
    )
    profile = relationship("Profile", back_populates="user_university")


class AvailableLanguage(ModelBase):
    level = Column(String)

    language_id = Column(Integer, ForeignKey("language.id", ondelete="CASCADE"))
    language = relationship("Language", backref="available_language")

    profile_id = Column(Integer, ForeignKey("profile.id", ondelete="CASCADE"))
    profile = relationship("Profile", back_populates="available_language_list")


class Introduction(ModelBase):
    keyword = Column(String)
    context = Column(Text)

    profile_id = Column(Integer, ForeignKey("profile.id", ondelete="CASCADE"))
    profile = relationship("Profile", back_populates="introductions")


class StudentVerification(ModelBase):
    student_card = Column(String)
    verification_status = Column(String, default="pending")

    profile_id = Column(Integer, ForeignKey("profile.id", ondelete="CASCADE"))
    profile = relationship("Profile", back_populates="student_verification")

    @property
    def user_email(self):
        return self.profile.user.email

    @property
    def user_name(self):
        return self.profile.user.name

    @property
    def user_birth(self):
        return self.profile.user.birth
