from typing import Any, Dict, Optional, Union, List
from pydantic.networks import EmailStr
import smtplib
from jinja2 import Environment, FileSystemLoader
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from passlib.context import CryptContext
from fastapi import HTTPException

from log import log_error
from core.config import settings
from crud.base import CRUDBase
import crud
from crud.profile import save_upload_file, generate_random_string
from models.user import (
    User,
    EmailCertification,
    Consent,
    UserNationality,
    AccountDeletionRequest,
)
from models.meeting import Meeting, MeetingUser
from models.profile import UserUniversity
from schemas import user as user_schmea

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


class CRUDUser(CRUDBase[User, user_schmea.UserCreate, user_schmea.UserUpdate]):
    """
    CRUD operations for User model.
    """

    def get_deactive_users(self, db: Session):
        deactive_users = db.query(User).filter(User.is_active == False).all()
        return deactive_users

    def get_user_fcm_token(self, db: Session, user_id):
        obj = db.query(User).filter(User.id == user_id).first()
        return obj.fcm_token

    def get_all_users(self, db: Session):
        users = db.query(User).filter(User.is_active == True).all()
        return users

    def get_consent(self, db: Session, user_id: int):
        return db.query(Consent).filter(Consent.user_id == user_id).first()

    def create_consent(self, db: Session, obj_in: user_schmea.ConsentCreate):
        db_obj = Consent(**obj_in.model_dump())
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

    def create_university(self, db: Session, obj_in: user_schmea.UserUniversityCreate):
        db_obj = UserUniversity(**obj_in.model_dump())
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
        self,
        db: Session,
        db_obj: UserUniversity,
        obj_in: user_schmea.UserUniversityCreate,
    ):
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_nationality(self, db: Session, user_id: int):
        return (
            db.query(UserNationality).filter(UserNationality.user_id == user_id).first()
        )

    def read_nationalities(self, db: Session, user_id: int):
        return (
            db.query(UserNationality).filter(UserNationality.user_id == user_id).all()
        )

    def create_nationality(
        self, db: Session, obj_in: user_schmea.UserNationalityCreate
    ):
        db_obj = UserNationality(**obj_in.model_dump())
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
            user_nationality = user_schmea.UserNationalityCreate(
                nationality_id=id, user_id=user_id
            )
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

    def remove_email_certification(
        self, db: Session, *, db_obj: user_schmea.EmailCertificationCheck
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
        self, db: Session, *, obj_in: user_schmea.EmailCertificationIn
    ) -> user_schmea.EmailCertificationCheck:
        """
        Create a new email certification entry.

        Args:
            db: Database session instance.
            obj_in: EmailCertificationIn instance containing email and certification.

        Returns:
            Created EmailCertificationCheck instance.
        """
        db_obj = EmailCertification(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_email_certification(
        self, db: Session, *, email: str, certification: str
    ) -> Optional[user_schmea.EmailCertificationCheck]:
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

    def get_by_sns(self, db: Session, sns_type: str, sns_id: str):
        return (
            db.query(User)
            .filter(User.sns_id == sns_id)
            .filter(User.sns_type == sns_type)
            .first()
        )

    def get_by_birth(self, db: Session, name: str, birth: str):
        return (
            db.query(User).filter(User.name == name).filter(User.birth == birth).first()
        )

    def update_fcm_token(self, db: Session, user_id: int, fcm_token: str):
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValueError("User with given ID not found")

        user.fcm_token = fcm_token

        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except:
            db.rollback()
            raise
        finally:
            db.close()

        return user

    def create(self, db: Session, *, obj_in: user_schmea.UserCreate) -> User:
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
        db_obj = User(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[user_schmea.UserBaseUpdate, Dict[str, Any]],
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
            update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True)

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

    def get_nationality_by_user_id(
        self, db: Session, user_id: int
    ) -> List[UserNationality]:
        user_nationalities = (
            db.query(UserNationality)
            .options(
                joinedload(UserNationality.nationality)
            )  # Nationality를 join하여 로드
            .filter(UserNationality.user_id == user_id)
            .all()
        )

        return user_nationalities

    def deactive_user(self, db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        user.is_active = False
        user.deactive_time = datetime.now()
        db.commit()
        return user

    def save_deletion_request(self, db: Session, reason: str):
        db_obj = AccountDeletionRequest(reason)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def made_admin(self, db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        user.is_admin = True
        db.commit()
        return user

    def read_all_chat_users(self, db: Session, chat_id: str) -> Dict[int, str]:
        meeting_users = (
            db.query(MeetingUser)
            .options(joinedload(MeetingUser.user))
            .join(Meeting)
            .filter(Meeting.chat_id == chat_id)
        )
        user_dict = {
            mu.user.id: mu.user.fcm_token for mu in meeting_users if mu.user.fcm_token
        }
        return user_dict


class CRUDDeleteRequests(
    CRUDBase[
        AccountDeletionRequest,
        user_schmea.DeletionRequestCreate,
        user_schmea.DeletionRequestCreate,
    ]
):
    pass


class CRUDSignUP:
    def __init__(self, crud_user: CRUDUser):
        self.crud_user = crud_user

    def check_exists(self, db: Session, obj_in: user_schmea.UserRegister):
        # 데이터베이스에서 이메일로 사용자 확인
        if obj_in.email:
            user = self.crud_user.get_by_email(db=db, email=obj_in.email)
            if user:
                if not user.is_active:
                    raise HTTPException(
                        status_code=403,
                        detail="This account is the account that requested to be deleted.",
                    )
                raise HTTPException(status_code=409, detail="User already registered.")
        elif obj_in.sns_type and obj_in.sns_id:
            user = self.crud_user.get_by_sns(
                db=db, sns_type=obj_in.sns_type, sns_id=obj_in.sns_id
            )
            if user:
                raise HTTPException(status_code=409, detail="User already registered.")

        check_user = self.crud_user.get_by_birth(
            db=db, name=obj_in.name, birth=obj_in.birth
        )
        if check_user:
            raise HTTPException(
                status_code=409,
                detail="User with same name and birthdate already registered.",
            )

        user_nationality_obj_list = obj_in.nationality_ids

        university = crud.utility.get(db=db, university_id=obj_in.university_id)
        if not university:
            raise HTTPException(status_code=400, detail="University Not Found")

        for id in user_nationality_obj_list:
            nation = crud.utility.get(db=db, nationality_id=id)
            if not nation:
                raise HTTPException(status_code=400, detail="Nationality Not Found")

        return True

    def register_user(self, db: Session, obj_in: user_schmea.UserRegister):
        new_user = None
        consent_obj = None
        user_university_obj = None
        hashed_password = None

        password = obj_in.password
        user_nationality_obj_list = obj_in.nationality_ids

        if password:
            hashed_password = get_password_hash(password)

        user_in = user_schmea.UserCreate(
            email=obj_in.email,
            password=hashed_password,
            name=obj_in.name,
            birth=obj_in.birth,
            gender=obj_in.gender,
            sns_type=obj_in.sns_type,
            sns_id=obj_in.sns_id,
            fcm_token=obj_in.fcm_token,
        )

        new_user = self.crud_user.create(db=db, obj_in=user_in)

        consent_in = user_schmea.ConsentCreate(
            terms_mandatory=obj_in.terms_mandatory,
            terms_optional=obj_in.terms_optional,
            terms_push=obj_in.terms_push,
            user_id=new_user.id,
        )

        user_university_in = user_schmea.UserUniversityCreate(
            department=obj_in.department,
            education_status=obj_in.education_status,
            university_id=obj_in.university_id,
            user_id=new_user.id,
        )

        for id in user_nationality_obj_list:
            user_nationality_in = user_schmea.UserNationalityCreate(
                nationality_id=id, user_id=new_user.id
            )
            user_nationality_obj = self.crud_user.create_nationality(
                db=db, obj_in=user_nationality_in
            )

        consent_obj = self.crud_user.create_consent(db=db, obj_in=consent_in)
        user_university_obj = self.crud_user.create_university(
            db=db, obj_in=user_university_in
        )
        system = crud.system.create_with_default_value(db=db, user_id=new_user.id)
        return new_user


user = CRUDUser(User)
signup = CRUDSignUP(user)
deletion_requests = CRUDDeleteRequests(AccountDeletionRequest)
