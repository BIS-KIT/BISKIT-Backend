from models.base import ModelBase
from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship


class User(ModelBase):
    email = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    birth = Column(Date)

    gender = Column(String)
    is_graduated = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    profile = relationship("Profile", back_populates="user", uselist=False)
    consents = relationship("Consent", back_populates="user")
    verification = relationship("Verification", back_populates="user")
    available_language = relationship("AvailableLanguage", back_populates="user")
    user_university = relationship("UserUniversity", back_populates="user")
    user_nationality = relationship("UserNationality", back_populates="user")


class UserNationality(ModelBase):
    nationality_id = Column(Integer, ForeignKey("nationality.id"))
    nationality = relationship("Nationality", back_populates="user_nationalities")

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="user_nationality")


class UserUniversity(ModelBase):
    department = Column(String, nullable=True)

    user_university_id = Column(Integer, ForeignKey("university.id"))
    university = relationship("University", back_populates="user_university")

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="user_university")


class EmailCertification(ModelBase):
    certification = Column(String, index=True)
    email = Column(String, index=True)


class Consent(ModelBase):
    terms_mandatory = Column(Boolean, nullable=True)  # 필수 약관 동의
    terms_optional = Column(Boolean, default=False, nullable=True)  # 선택 약관 동의
    terms_push = Column(Boolean, nullable=True)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="consents")


class Verification(ModelBase):
    # 학생증 사진의 파일 경로나 URL을 저장하는 필드
    student_card_image = Column(String)
    verification_status = Column(String, default="pending")

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="verification")


class FirebaseAuth(ModelBase):
    provider_id = Column(String)  # 예: 'google.com', 'kakao.com'
    uid = Column(String, unique=True, index=True)  # Firebase에서 제공하는 고유 사용자 ID
    firebase_token = Column(String)  # Firebase 인증 토큰 (주기적으로 갱신됨)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref="firebase_auth")
