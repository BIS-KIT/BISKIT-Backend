from typing import Any, Dict, Optional, Union
import os, random, string

from sqlalchemy.orm import Session
from fastapi import UploadFile

from crud.base import CRUDBase
from models.profile import Profile
from schemas.profile import ProfileCreate, ProfileUpdate


def generate_random_string(length=3):
    return "".join(random.choices(string.ascii_letters, k=length))


class CRUDProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    """
    CRUD operations for User model.
    """

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

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def save_upload_file(self, upload_file: UploadFile, destination: str) -> None:
        try:
            with open(destination, "wb") as buffer:
                buffer.write(upload_file.file.read())
        finally:
            upload_file.file.close()

    def upload_profile_photo(self, db: Session, user_id: int, photo: UploadFile):
        profile = self.get_by_user_id(db, user_id=user_id)
        if not profile:
            return None

        if profile.profile_photo:
            old_photo_path = profile.profile_photo
            if os.path.exists(old_photo_path):
                os.remove(old_photo_path)

        random_str = generate_random_string()
        file_path = f"media/profile_photo/{random_str}_{photo.filename}"
        self.save_upload_file(photo, file_path)

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
