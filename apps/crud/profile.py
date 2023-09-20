from typing import Any, Dict, Optional, Union
import os, random, string, boto3
from botocore.exceptions import NoCredentialsError

from sqlalchemy.orm import Session
from fastapi import UploadFile

from crud.base import CRUDBase
from core.config import settings
from models.profile import Profile
from schemas.profile import ProfileCreate, ProfileUpdate


def generate_random_string(length=3):
    return "".join(random.choices(string.ascii_letters, k=length))


def get_aws_client():
    AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
    AWS_DEFAULT_REGION = settings.AWS_REGION

    client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION,
    )
    return client


class CRUDProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    """
    CRUD operations for User model.
    """

    def get_by_nick_name(self, db: Session, nick_name: str):
        return db.query(Profile).filter(Profile.nick_name == nick_name).first()

    def get_by_user_id(self, db: Session, *, user_id: str) -> Optional[Profile]:
        return db.query(Profile).filter(Profile.user_id == user_id).first()

    def create(self, db: Session, *, obj_in: ProfileCreate, user_id: int) -> Profile:
        """
        Create a new user.

        Args:
            db: Database session instance.
            obj_in: User creation schema containing user details.

        Returns:
            Created User instance.
        """
        if not user_id:
            raise ValueError("There is no user_id")

        if obj_in.profile_photo:
            random_str = generate_random_string()
            file_path = f"profile_photo/{random_str}_{obj_in.profile_photo.filename}"
            s3_url = self.save_upload_file(obj_in.profile_photo, file_path)
            obj_in.profile_photo = file_path  # Update path

        db_obj = Profile(**obj_in.dict(), user_id=user_id)
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

        # Handle profile photo upload if provided
        if "profile_photo" in update_data:
            if update_data["profile_photo"]:
                photo = update_data["profile_photo"]
                # Delete old photo if exists
                if db_obj.profile_photo:
                    self.delete_file_from_s3(db_obj.profile_photo)

                random_str = generate_random_string()
                file_path = f"profile_photo/{random_str}_{photo.filename}"
                self.save_upload_file(photo, file_path)
                update_data["profile_photo"] = file_path  # Update path
            else:
                del update_data["profile_photo"]

        if not update_data["nick_name"]:
            del update_data["nick_name"]
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def save_upload_file(self, upload_file: UploadFile, destination: str) -> None:
        s3_client = get_aws_client()
        bucket_name = settings.BUCKET_NAME

        try:
            s3_client.upload_fileobj(upload_file.file, bucket_name, destination)
        except NoCredentialsError:
            print("Credentials not available")
        finally:
            upload_file.file.close()

        image_url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{destination}"

        return image_url

    def delete_file_from_s3(self, file_url: str) -> None:
        s3_client = get_aws_client()
        bucket_name = settings.BUCKET_NAME

        # Assuming file_url follows the format: https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{destination}
        # Extract the S3 object key from the file_url
        object_key = file_url

        try:
            s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        except Exception as e:
            print(f"Error deleting {file_url} from S3:", e)

    def upload_profile_photo(self, db: Session, user_id: int, photo: UploadFile):
        profile = self.get_by_user_id(db, user_id=user_id)
        if not profile:
            return None

        if profile.profile_photo:
            # Delete the old photo from S3
            self.delete_file_from_s3(profile.profile_photo)

        random_str = generate_random_string()
        file_path = f"/profile_photo/{random_str}_{photo.filename}"
        # TODO : Check this url
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
        os.remove(profile.profile_photo)

        profile.profile_photo = None
        db.commit()
        db.refresh(profile)
        return profile


profile = CRUDProfile(Profile)
