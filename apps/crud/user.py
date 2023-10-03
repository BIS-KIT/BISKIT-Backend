from typing import Any, Dict, Optional, Union, List
from pydantic.networks import EmailStr
import smtplib
from jinja2 import Environment, FileSystemLoader
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from log import log_error
from core.config import settings
from crud.base import CRUDBase
from crud.profile import save_upload_file, generate_random_string
from models.user import (
    User,
    EmailCertification,
    Consent,
    UserNationality,
    UserUniversity,
)
from schemas.user import (
    UserCreate,
    UserUpdate,
    EmailCertificationIn,
    EmailCertificationCheck,
    ConsentCreate,
    UserUniversityCreate,
    UserNationalityCreate,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def render_template(filename: str, **kwargs):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(filename)
    return template.render(**kwargs)


def send_email(certification: int, receiver_email: EmailStr, language_code: str = "kr"):
    if language_code == "kr":
        body_template = "email_kr.html"
        SUBJECT = "BISKIT 이메일 인증"
    else:
        body_template = "email_kr.html"
        SUBJECT = "BISKIT Email Certification"

    s3_logo_url = settings.LOGO_URL
    BODY = render_template(
        body_template, certification=certification, s3_logo_url=s3_logo_url
    )

    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USER
    msg["To"] = receiver_email
    msg["Subject"] = SUBJECT
    msg.attach(MIMEText(BODY, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, receiver_email, msg.as_string())
        return True
    except Exception as e:
        log_error(f"Error occurred while sending email: {e}")
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

    def get_consent(self, db: Session, user_id: int):
        return db.query(Consent).filter(Consent.user_id == user_id).first()

    def create_consent(self, db: Session, obj_in: ConsentCreate):
        db_obj = Consent(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_consent(self, db: Session, id: int):
        obj = db.query(Consent).filter(Consent.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return obj

    def get_university(self, db: Session, user_id: int):
        return (
            db.query(UserUniversity).filter(UserUniversity.user_id == user_id).first()
        )

    def create_university(self, db: Session, obj_in: UserUniversityCreate):
        db_obj = UserUniversity(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_university(self, db: Session, id: int):
        obj = db.query(UserUniversity).filter(UserUniversity.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return obj

    def update_university(
        self, db: Session, db_obj: UserUniversity, obj_in: UserUniversityCreate
    ):
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_nationality(self, db: Session, user_id: int):
        return (
            db.query(UserNationality).filter(UserNationality.user_id == user_id).first()
        )

    def read_nationalities(self, db: Session, user_id: int):
        return (
            db.query(UserNationality).filter(UserNationality.user_id == user_id).all()
        )

    def create_nationality(self, db: Session, obj_in: UserNationalityCreate):
        db_obj = UserNationality(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_user_nationalities(
        self, db: Session, user_id: int, new_nationality_ids: List[int]
    ):
        # 기존 nationality_ids 불러오기
        existing_nationalities = self.read_nationalities(db=db, user_id=user_id)
        existing_nationality_ids = [
            nationality.nationality_id for nationality in existing_nationalities
        ]
        # 새로 추가된 nationality_ids 찾기
        to_add = set(new_nationality_ids) - set(existing_nationality_ids)

        # 삭제된 nationality_ids 찾기
        to_remove = set(existing_nationality_ids) - set(new_nationality_ids)
        # 새로운 nationality_ids 추가
        for id in to_add:
            user_nationality = UserNationalityCreate(nationality_id=id, user_id=user_id)
            self.create_nationality(db=db, obj_in=user_nationality)

        # 삭제된 nationality_ids 제거
        for nationality_id in to_remove:
            self.remove_nationality(db=db, nationality_id=nationality_id)

    def remove_nationality(self, db: Session, nationality_id: int):
        obj = (
            db.query(UserNationality)
            .filter(UserNationality.nationality_id == nationality_id)
            .first()
        )
        if obj:
            db.delete(obj)
            db.commit()
            return obj

    # def update_nationality(
    #     self, db: Session, db_obj: UserNationality, obj_in: UserNationalityCreate
    # ):
    #     if isinstance(obj_in, dict):
    #         update_data = obj_in
    #     else:
    #         update_data = obj_in.dict(exclude_unset=True)
    #     return super().update(db, db_obj=db_obj, obj_in=update_data)

    def remove_email_certification(
        self, db: Session, *, db_obj: EmailCertificationCheck
    ):
        obj = (
            db.query(EmailCertification)
            .filter(
                EmailCertification.email == db_obj.email,
                EmailCertification.certification == db_obj.certification,
            )
            .first()
        )
        db.delete(obj)
        db.commit()
        return obj

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
        db_obj = EmailCertification(**obj_in.dict())
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
            db.query(EmailCertification)
            .filter(
                EmailCertification.email == email,
                EmailCertification.certification == certification,
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

        if "password" in update_data and update_data["password"]:
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
