from typing import Any, Dict, Optional, Union, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from core.config import settings
from crud.base import CRUDBase
from models.user import User
from schemas.user import (
    UserCreate,
    UserUpdate,
    EmailCertificationIn,
    EmailCertificationCheck,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def send_email(certification: int, receiver_email: EmailStr, language_code: str):
    BODY = f"Your certification code is: {certification}"

    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USER
    msg["To"] = receiver_email
    msg["Subject"] = "BISKIT 이메일 인증"
    msg.attach(MIMEText(BODY, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            # TLS(전송 계층 보안)를 사용하여 현재의 무안전한 연결을 보호하도록 업그레이드
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, receiver_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error occurred while sending email: {e}")
        return False


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    주어진 패스워드와 해시된 패스워드가 일치하는지 확인한다.

    Args:
    - plain_password: 검증할 패스워드.
    - hashed_password: 해시된 패스워드.

    Returns:
    - 패스워드가 일치하면 True, 그렇지 않으면 False.
    """
    ...
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    패스워드를 해싱한다.

    Args:
    - password: 해싱할 패스워드.

    Returns:
    - 해싱된 패스워드 문자열.
    """
    return pwd_context.hash(password)


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations for User model.
    """

    def create_email_certification(
        self, db: Session, *, obj_in: EmailCertificationIn
    ) -> EmailCertificationCheck:
        """
        Create a new email certification entry.

        Args:
            db: Database session instance.
            obj_in: EmailCertificationIn instance containing email and certification.

        Returns:
            Created EmailCertificationCheck instance.
        """
        db_obj = EmailCertificationCheck(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_email_certification(
        self, db: Session, *, email: str, certification: str
    ) -> Optional[EmailCertificationCheck]:
        """
        Retrieve an email certification entry by email and certification.

        Args:
            db: Database session instance.
            email: Email associated with the certification.
            certification: Certification code.

        Returns:
            EmailCertificationCheck instance if found, else None.
        """
        return (
            db.query(EmailCertificationCheck)
            .filter(
                EmailCertificationCheck.email == email,
                EmailCertificationCheck.certification == certification,
            )
            .first()
        )

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Retrieve a user by its email.

        Args:
            db: Database session instance.
            email: Email of the user to retrieve.

        Returns:
            User instance if found, else None.
        """
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user.

        Args:
            db: Database session instance.
            obj_in: User creation schema containing user details.

        Returns:
            Created User instance.
        """
        if "password" in obj_in:
            obj_in.password = get_password_hash(obj_in.password)
        db_obj = User(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update a user's details.

        Args:
            db: Database session instance.
            db_obj: User instance to update.
            obj_in: User update schema or dict containing updated details.

        Returns:
            Updated User instance.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by its email and password.

        Args:
            db: Database session instance.
            email: Email of the user to authenticate.
            password: Password for authentication.

        Returns:
            User instance if authentication is successful, else None.
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user = CRUDUser(User)
