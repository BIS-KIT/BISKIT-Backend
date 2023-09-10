from apps.models.base import ModelBase
from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship


class User(ModelBase):
    email = Column(String, unique=True, index=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    birth = Column(Date)
    nationality = Column(String)
    university = Column(String, nullable=True)
    department = Column(String, nullable=True)
    gender = Column(String)
    is_graduated = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)


class Consent(ModelBase):
    terms_mandatory = Column(Boolean, nullable=True)  # 필수 약관 동의
    terms_optional = Column(Boolean, default=False, nullable=True)  # 선택 약관 동의
    terms_push = Column(Boolean, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="consents")


class Verification(ModelBase):
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    user = relationship("User", back_populates="verification")

    # 학생증 사진의 파일 경로나 URL을 저장하는 필드
    student_card_image = Column(String)
    verification_status = Column(String, default="pending")


class FirebaseAuth(ModelBase):
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    user = relationship("User", backref="firebase_auth")

    provider_id = Column(String, nullable=True)  # 예: 'google.com', 'kakao.com'
    uid = Column(String, unique=True, index=True)  # Firebase에서 제공하는 고유 사용자 ID
    firebase_token = Column(String, nullable=True)  # Firebase 인증 토큰 (주기적으로 갱신됨)


User.Verification = relationship("Verification", uselist=False, back_populates="user")
