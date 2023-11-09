from typing import Any, Dict, Optional, Union, List
import os, random, string, boto3, re
from botocore.exceptions import NoCredentialsError

from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from log import log_error
from crud.base import CRUDBase
from core.config import settings
from models.profile import (
    Profile,
    AvailableLanguage,
    Introduction,
    StudentVerification,
    UserUniversity,
)
from schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
    AvailableLanguageCreate,
    IntroductionCreate,
    StudentVerificationCreate,
    StudentVerificationUpdate,
    ProfileRegister,
    ProfileUniversityUpdate,
    AvailableLanguageIn,
    IntroductionIn,
)
from schemas.enum import ReultStatusEnum
import crud


def pre_processing_useruniversity(db: Session):
    # 모든 UserUniversity 인스턴스를 가져오는 것 대신 필요할 때마다 하나씩 가져옵니다.
    all_useruniversity_ids = db.query(UserUniversity.id).all()

    for useruniversity_id in all_useruniversity_ids:
        useruniversity = db.query(UserUniversity).get(useruniversity_id)
        user_id = useruniversity.user_id
        # user_id를 기반으로 Profile을 조회합니다.
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        # Profile이 존재하는 경우에만 profile_id를 업데이트합니다.
        if profile:
            useruniversity.profile_id = profile.id
        else:
            continue
        # 변경 사항을 데이터베이스에 적용하기 위해 플러시합니다.
        db.flush()

    # 모든 변경 사항을 커밋합니다.
    db.commit()


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

    def get_verification(self, db: Session, profile_id: int = None, id: int = None):
        if profile_id:
            return (
                db.query(StudentVerification)
                .filter(StudentVerification.profile_id == profile_id)
                .first()
            )
        else:
            return (
                db.query(StudentVerification)
                .filter(StudentVerification.id == id)
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

    def remove_ava_lan(self, db: Session, profile_id: int = None, id: int = None):
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

    def get_introduction(
        self, db: Session, keyword: str = None, profile_id: int = None, id: int = None
    ):
        if profile_id:
            obj = (
                db.query(Introduction)
                .filter(
                    Introduction.keyword == keyword, Introduction.profile_ == profile_id
                )
                .first()
            )
            return obj
        return db.query(Introduction).filter(Introduction.id == id).first()

    def update_introduction(
        self, db: Session, db_obj: Introduction, obj_in: IntroductionCreate
    ):
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def create_introduction(
        self, db: Session, obj_in: IntroductionCreate, profile_id: int = None
    ):
        if profile_id is not None:
            obj_in["profile_id"] = profile_id
        db_obj = Introduction(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_introduction(
        self, db: Session, keyword: str = None, profile_id: int = None, id: int = None
    ):
        obj = db.query(Introduction).filter(Introduction.id == id).delete()
        if profile_id:
            obj = (
                db.query(Introduction)
                .filter(
                    Introduction.keyword == keyword, Introduction.profile_ == profile_id
                )
                .delete()
            )
        db.commit()
        return obj

    def get_ava_lan(self, db: Session, id: int):
        return db.query(AvailableLanguage).filter(AvailableLanguage.id == id).first()

    def create_ava_lan(
        self, db: Session, obj_in: AvailableLanguageCreate, profile_id: int = None
    ):
        if profile_id is not None:
            obj_in["profile_id"] = profile_id
        db_obj = AvailableLanguage(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_ava_lan(
        self,
        db: Session,
        db_obj: AvailableLanguage,
        obj_in: AvailableLanguageCreate,
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

    def create(self, db: Session, *, obj_in: ProfileRegister, user_id: int) -> Profile:
        """
        Create a new user.

        Args:
            db: Database session instance.
            obj_in: User creation schema containing user details.

        Returns:
            Created User instance.
        """

        available_languages: List[AvailableLanguageCreate] = obj_in.available_languages
        Introductions: List[IntroductionCreate] = obj_in.introductions
        student_card = obj_in.student_card
        try:
            profile_obj = Profile(
                nick_name=obj_in.nick_name,
                profile_photo=obj_in.profile_photo,
                user_id=user_id,
            )
            db.add(profile_obj)
            db.flush()

            if available_languages:
                for ava_lang in available_languages:
                    ava_lan_obj = AvailableLanguage(
                        level=ava_lang.level,
                        language_id=ava_lang.language_id,
                        profile_id=profile_obj.id,
                    )
                    db.add(ava_lan_obj)

            if Introductions:
                for intro in Introductions:
                    intro_obj = Introduction(
                        keyword=intro.keyword,
                        context=intro.context,
                        profile_id=profile_obj.id,
                    )
                    db.add(intro_obj)

            if student_card:
                student_card_obj = StudentVerification(
                    student_card=student_card.student_card,
                    verification_status=student_card.verification_status,
                    profile_id=profile_obj.id,
                )
            else:
                student_card_obj = StudentVerification(
                    student_card=None,
                    verification_status=ReultStatusEnum.UNVERIFIED,
                    profile_id=profile_obj.id,
                )
                db.add(student_card_obj)

            user_universty = self.matching_useruniversity(db=db, user_id=user_id)
            if user_universty:
                user_universty.profile_id = profile_obj.id
            else:
                raise HTTPException(status_code=404, detail="UserUniversity not found")
            db.commit()

        except Exception as e:
            db.rollback()
            log_error(e)
            raise e
        db.refresh(profile_obj)
        return profile_obj

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

        available_languages: List[AvailableLanguageIn] = obj_in.available_languages
        introductions: List[IntroductionIn] = obj_in.introductions
        university_info: ProfileUniversityUpdate = obj_in.university_info

        # Update basic profile fields if provided
        if obj_in.nick_name is not None:
            db_obj.nick_name = obj_in.nick_name
        if obj_in.profile_photo is not None:
            db_obj.profile_photo = obj_in.profile_photo
        if obj_in.context is not None:
            db_obj.context = obj_in.context

        if available_languages:
            existing_language_ids = {
                lang.language_id for lang in db_obj.available_languages
            }
            new_languages = {
                lang.language_id for lang in obj_in.available_languages or []
            }
            for language_id in existing_language_ids - new_languages:
                self.remove_ava_lan(db=db, id=language_id)

            for language_data in new_languages or []:
                if language_data.language_id in existing_language_ids:
                    existing_ava_lang = self.get_ava_lan(
                        db=db, id=language_data.language_id
                    )
                    self.update_ava_lan(
                        db=db, db_obj=existing_ava_lang, obj_in=language_data
                    )
                else:
                    # Add the new language
                    self.create_ava_lan(
                        db=db, obj_in=language_data, profile_id=db_obj.id
                    )

        if introductions:
            existing_intros = {intro.keyword: intro for intro in db_obj.introductions}
            new_intros = {
                intro_data.keyword: intro_data
                for intro_data in obj_in.introductions or []
            }

            for keyword in existing_intros.keys() - new_intros.keys():
                self.remove_introduction(db=db, keyword=keyword, profile_id=db_obj.id)

            for keyword, intro_data in new_intros.items():
                if keyword in existing_intros:
                    # Update the existing introduction if context has changed
                    existing_intro = self.get_introduction(
                        db=db, keyword=keyword, profile_id=db_obj.id
                    )
                    if intro_data.context != existing_intro.context:
                        self.update_introduction(
                            db=db, db_obj=existing_intro, obj_in=intro_data
                        )
                else:
                    # Add the new introduction
                    self.create_introduction(
                        db=db, obj_in=intro_data, profile_id=db_obj.id
                    )

        if university_info:
            existing_unviersity = self.get_user_university(db=db, profile_id=db_obj.id)
            self.update_user_university(
                db=db, db_obj=existing_unviersity, obj_in=university_info
            )

        db.commit()
        db.refresh(profile)

        return profile

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
        print(profile, profile.profile_photo)
        if not profile or not profile.profile_photo:
            return None

        # 필요하다면 실제 이미지 파일도 제거합니다.
        self.delete_file_from_s3(profile.profile_photo)

        profile.profile_photo = None
        db.commit()
        db.refresh(profile)
        return profile

    def matching_useruniversity(self, db: Session, user_id: int) -> UserUniversity:
        obj = db.query(UserUniversity).filter(UserUniversity.user_id == user_id).first()
        return obj

    def get_user_university(self, db: Session, profile_id: int):
        return (
            db.query(UserUniversity)
            .filter(UserUniversity.profile_id == profile_id)
            .first()
        )

    def update_user_university(
        self, db: Session, db_obj: UserUniversity, obj_in: ProfileUniversityUpdate
    ):
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)


profile = CRUDProfile(Profile)
