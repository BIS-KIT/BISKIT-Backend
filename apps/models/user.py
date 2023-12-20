from models.base import ModelBase
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    Enum,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship, backref


class User(ModelBase):
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=True)
    name = Column(String)
    birth = Column(Date)

    gender = Column(String)

    sns_type = Column(String, nullable=True)
    sns_id = Column(String, nullable=True)
    fcm_token = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    deactive_time = Column(DateTime, default=None, nullable=True)
    deleted_data = Column(Date, nullable=True)
    is_admin = Column(Boolean, default=False)

    profile = relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    consents = relationship(
        "Consent", back_populates="user", cascade="all, delete-orphan"
    )

    user_nationality = relationship(
        "UserNationality", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def profile_photo(self):
        return self.profile.profile_photo if self.profile else None

    @property
    def nick_name(self):
        return self.profile.nick_name if self.profile else None


class UserNationality(ModelBase):
    nationality_id = Column(Integer, ForeignKey("nationality.id", ondelete="CASCADE"))
    nationality = relationship(
        "Nationality", backref=backref("user_nationality", cascade="all, delete-orphan")
    )

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="user_nationality")


class EmailCertification(ModelBase):
    certification = Column(String, index=True)
    email = Column(String, index=True)


class Consent(ModelBase):
    terms_mandatory = Column(Boolean, default=True, nullable=True)  # 필수 약관 동의
    terms_optional = Column(Boolean, default=False, nullable=True)  # 선택 약관 동의
    terms_push = Column(Boolean, nullable=True)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="consents")


class FirebaseAuth(ModelBase):
    provider_id = Column(String)  # 예: 'google.com', 'kakao.com'
    uid = Column(String, unique=True, index=True)  # Firebase에서 제공하는 고유 사용자 ID
    firebase_token = Column(String)  # Firebase 인증 토큰 (주기적으로 갱신됨)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref="firebase_auth")


class AccountDeletionRequest(ModelBase):
    reason = Column(String, nullable=False)
