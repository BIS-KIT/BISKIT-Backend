from typing import Any, Dict, Optional, Union
import os, random, string, boto3
from botocore.exceptions import NoCredentialsError

from sqlalchemy.orm import Session
from fastapi import UploadFile

from log import log_error
from crud.base import CRUDBase
from core.config import settings
from models.profile import Profile, AvailableLanguage, Introduction, StudentVerification
from schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    AvailableLanguageCreate,
    IntroductionCreate,
    StudentVerificationCreate,
    StudentVerificationUpdate,
    StudentVerificationBase,
)


def save_upload_file(upload_file: UploadFile, destination: str) -> None:
    s3_client = get_aws_client()
    bucket_name = settings.BUCKET_NAME

    try:
        s3_client.upload_fileobj(upload_file.file, bucket_name, destination)
    except NoCredentialsError:
        log_error("Credentials not available")
    finally:
        upload_file.file.close()

    image_url = (
        f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{destination}"
    )

    return image_url


def generate_random_string(length=3):
    return "".join(random.choices(string.ascii_letters, k=length))


def get_aws_client():
    AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
    AWS_DEFAULT_REGION = settings.AWS_REGION
    try:
        client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_DEFAULT_REGION,
        )
    except Exception as e:
        client = None
        log_error(e)
    return client


class CRUDProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    """
    CRUD operations for User model.
    """

    def get_verification(self, db: Session, profile_id: int):
        return (
            db.query(StudentVerification)
            .filter(StudentVerification.profile_id == profile_id)
            .first()
        )

    def list_verification(self, db: Session):
        return db.query(StudentVerification).all()

    def update_verification(
        self,
        db: Session,
        db_obj: StudentVerification,
        obj_in: StudentVerificationUpdate,
    ):
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def create_verification(self, db: Session, obj_in: StudentVerificationCreate):
        if not obj_in.profile_id:
            raise ValueError("There is no profile_id")

        profile = db.query(Profile).filter(Profile.id == obj_in.profile_id)
        if not profile:
            raise ValueError("There is no Profile")
        db_obj = StudentVerification(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_ava_lan(self, db: Session, profile_id: int, id: int):
        if profile_id:
            obj = (
                db.query(AvailableLanguage)
                .filter(AvailableLanguage.profile_id == profile_id)
                .delete()
            )
            db.commit()
        else:
            obj = (
                db.query(AvailableLanguage).filter(AvailableLanguage.id == id).delete()
            )
            db.commit()
        return obj

    def get_introduction(self, db: Session, id: int):
        return db.query(Introduction).filter(Introduction.id == id).first()

    def update_introduction(
        self, db: Session, db_obj: Introduction, obj_in: IntroductionCreate
    ):
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def create_introduction(self, db: Session, obj_in: IntroductionCreate):
        db_obj = Introduction(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_introduction(self, db: Session, id: int):
        obj = db.query(Introduction).filter(Introduction.id == id).delete()
        db.commit()
        return obj

    def get_ava_lan(self, db: Session, id: int):
        return db.query(AvailableLanguage).filter(AvailableLanguage.id == id).first()

    def create_ava_lan(self, db: Session, obj_in: AvailableLanguageCreate):
        db_obj = AvailableLanguage(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_ava_lan(
        self, db: Session, db_obj: AvailableLanguage, obj_in: AvailableLanguageCreate
    ):
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_by_nick_name(self, db: Session, nick_name: str):
        return db.query(Profile).filter(Profile.nick_name == nick_name).first()

    def get_by_user_id(self, db: Session, *, user_id: str) -> Optional[Profile]:
        return db.query(Profile).filter(Profile.user_id == user_id).first()

    def create(self, db: Session, *, obj_in: ProfileCreate) -> Profile:
        """
        Create a new user.

        Args:
            db: Database session instance.
            obj_in: User creation schema containing user details.

        Returns:
            Created User instance.
        """
        if not obj_in.user_id:
            raise ValueError("There is no user_id")

        db_obj = Profile(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Profile,
        obj_in: Union[ProfileUpdate, Dict[str, Any]],
    ) -> Profile:
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

        if not update_data["nick_name"]:
            del update_data["nick_name"]

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def delete_file_from_s3(self, file_url: str) -> None:
        s3_client = get_aws_client()
        bucket_name = settings.BUCKET_NAME

        # Assuming file_url follows the format: https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{destination}
        # Extract the S3 object key from the file_url
        object_key = file_url

        try:
            s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        except Exception as e:
            log_error(f"Error deleting {file_url} from S3:{e}")

    def upload_profile_photo(self, db: Session, user_id: int, photo: UploadFile):
        profile = self.get_by_user_id(db, user_id=user_id)
        if not profile:
            return None

        if profile.profile_photo:
            # Delete the old photo from S3
            self.delete_file_from_s3(profile.profile_photo)

        random_str = generate_random_string()
        file_path = f"/profile_photo/{random_str}_{photo}"
        s3_url = self.save_upload_file(photo, file_path)

        profile.profile_photo = file_path
        db.commit()
        db.refresh(profile)
        return profile

    def remove_profile_photo(self, db: Session, user_id: int):
        profile = self.get_by_user_id(db, user_id=user_id)
        if not profile or not profile.profile_photo:
            return None

        # 필요하다면 실제 이미지 파일도 제거합니다.
        self.delete_file_from_s3(profile.profile_photo)

        profile.profile_photo = None
        db.commit()
        db.refresh(profile)
        return profile


profile = CRUDProfile(Profile)
