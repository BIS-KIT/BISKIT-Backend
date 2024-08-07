from typing import Any, Dict, Optional, Union, List
import time, random, string, boto3, requests
from botocore.exceptions import NoCredentialsError

from sqlalchemy import func, desc, asc, extract
from sqlalchemy.orm import Session, aliased
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
from models.meeting import Meeting, MeetingUser, Review
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
from schemas.enum import ReultStatusEnum, MyMeetingEnum, MeetingOrderingEnum
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
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def create_verification(self, db: Session, obj_in: StudentVerificationCreate):
        """
        학생증 재인증시 기존 객체 삭제 후 재생성
        """
        if not obj_in.profile_id:
            raise ValueError("There is no profile_id")

        profile = db.query(Profile).filter(Profile.id == obj_in.profile_id)
        if not profile:
            raise ValueError("There is no Profile")

        check_student_verify = db.query(StudentVerification).filter(
            StudentVerification.profile_id == obj_in.profile_id
        )
        if check_student_verify:
            check_student_verify.delete()

        db_obj = StudentVerification(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove_ava_lan(
        self,
        db: Session,
        profile_id: int = None,
        id: int = None,
        language_id: int = None,
    ):
        query = db.query(AvailableLanguage)
        if id is not None:
            query = query.filter(AvailableLanguage.id == id)
        if language_id is not None:
            query = query.filter(AvailableLanguage.language_id == language_id)
        if profile_id is not None:
            query = query.filter(AvailableLanguage.profile_id == profile_id)

        # Now perform the delete operation
        count = query.delete()
        db.commit()
        return count

    def get_introduction(
        self, db: Session, keyword: str = None, profile_id: int = None, id: int = None
    ):
        if profile_id:
            obj = (
                db.query(Introduction)
                .filter(
                    Introduction.keyword == keyword,
                    Introduction.profile_id == profile_id,
                )
                .first()
            )
            return obj
        return db.query(Introduction).filter(Introduction.id == id).first()

    def update_introduction(
        self, db: Session, db_obj: Introduction, obj_in: IntroductionCreate
    ):
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def create_introduction(
        self, db: Session, obj_in: IntroductionCreate, profile_id: int = None
    ):
        create_obj = IntroductionCreate(**obj_in.model_dump()).model_dump()
        if profile_id is not None:
            create_obj["profile_id"] = profile_id
        db_obj = Introduction(**create_obj)
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
                    Introduction.keyword == keyword,
                    Introduction.profile_id == profile_id,
                )
                .delete()
            )
        db.commit()
        return obj

    def get_ava_lan(
        self,
        db: Session,
        id: int = None,
        language_id: int = None,
        profile_id: int = None,
    ):
        query = db.query(AvailableLanguage)
        if id is not None:
            query = query.filter(AvailableLanguage.id == id)
        if language_id is not None:
            query = query.filter(AvailableLanguage.language_id == language_id)
        if profile_id is not None:
            query = query.filter(AvailableLanguage.profile_id == profile_id)
        return query.first()

    def create_ava_lan(
        self, db: Session, obj_in: AvailableLanguageCreate, profile_id: int = None
    ):
        create_obj = AvailableLanguageCreate(**obj_in.model_dump()).model_dump()
        if profile_id is not None:
            create_obj["profile_id"] = profile_id
        db_obj = AvailableLanguage(**create_obj)
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
        if obj_in is None:
            return None

        obj_data = db_obj.to_dict()
        update_data = obj_in.model_dump(exclude_unset=True)
        if "profile_id" in update_data:
            raise ValueError("Cannot change the profile association via this method.")

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

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
                    verification_status=ReultStatusEnum.PENDING.value,
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
        origin_available_languages = db_obj.available_language_list
        update_available_languages = obj_in.available_languages

        origin_introductions = db_obj.introductions
        update_introductions = obj_in.introductions

        university_info: ProfileUniversityUpdate = obj_in.university_info

        # Update basic profile fields if provided
        if obj_in.nick_name is not None:
            db_obj.nick_name = obj_in.nick_name
        if obj_in.profile_photo is not None:
            db_obj.profile_photo = obj_in.profile_photo
        if obj_in.context is not None:
            db_obj.context = obj_in.context
        if obj_in.is_default_photo is not None:
            db_obj.is_default_photo = obj_in.is_default_photo

        if update_available_languages:
            existing_language_ids = {
                lang.language_id for lang in origin_available_languages
            }
            new_language_ids = {
                lang.language_id for lang in update_available_languages or []
            }
            for language_id in existing_language_ids - new_language_ids:
                self.remove_ava_lan(
                    db=db, language_id=language_id, profile_id=db_obj.id
                )

            for language_data in update_available_languages or []:
                if language_data.language_id in existing_language_ids:
                    existing_ava_lang = self.get_ava_lan(
                        db=db,
                        language_id=language_data.language_id,
                        profile_id=db_obj.id,
                    )
                    self.update_ava_lan(
                        db=db, db_obj=existing_ava_lang, obj_in=language_data
                    )
                else:
                    # Add the new language
                    self.create_ava_lan(
                        db=db, obj_in=language_data, profile_id=db_obj.id
                    )

        if update_introductions:
            existing_intros = {intro.keyword: intro for intro in origin_introductions}
            new_intros = {
                intro_data.keyword: intro_data
                for intro_data in update_introductions or []
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
        # db.refresh(profile)
        return db_obj

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
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def get_user_all_meetings(
        self,
        db: Session,
        order_by: str,
        user_id: int,
        status: str,
        skip: int,
        limit: int,
    ) -> List[Meeting]:
        # 사용자가 생성한 모임 검색
        created_meetings = db.query(Meeting).filter(Meeting.creator_id == user_id)

        # 사용자가 참여한 모임 검색
        participated_query = (
            db.query(Meeting).join(MeetingUser).filter(MeetingUser.user_id == user_id)
        )
        if status == MyMeetingEnum.APPROVE.value:
            created_meetings = created_meetings.filter(Meeting.is_active == True)
            participated_query = participated_query.filter(
                MeetingUser.status == MyMeetingEnum.APPROVE.value,
                Meeting.is_active == True,
            )
        elif status == MyMeetingEnum.PENDING.value:
            all_meetings = participated_query.filter(
                MeetingUser.status == MyMeetingEnum.PENDING.value,
                Meeting.is_active == True,
            )
            total_count = all_meetings.count()
            return all_meetings.offset(skip).limit(limit).all(), total_count
        elif status == MyMeetingEnum.PAST.value:
            user_reviews = aliased(Review)
            review_subquery = (
                db.query(user_reviews.meeting_id)
                .filter(user_reviews.creator_id == user_id)
                .subquery()
            )

            created_meetings = created_meetings.filter(
                Meeting.is_active == False,
                ~Meeting.id.in_(review_subquery),  # 사용자가 리뷰를 작성한 미팅 제외
            )
            participated_query = participated_query.filter(
                Meeting.is_active == False,
                ~Meeting.id.in_(review_subquery),  # 사용자가 리뷰를 작성한 미팅 제외
            )

        all_meetings = created_meetings.union(participated_query)
        # order_by 매개변수에 따른 정렬 로직 적용
        if order_by == MeetingOrderingEnum.CREATED_TIME:
            all_meetings = all_meetings.order_by(asc(Meeting.created_time))
        elif order_by == MeetingOrderingEnum.DEADLINE_SOON:
            # 현재 시간 이후의 모임만 선택
            all_meetings = all_meetings.filter(Meeting.meeting_time > func.now())
            # meeting_time과 now() 사이의 시간 차이를 초로 계산하여 정렬
            time_difference_seconds = extract(
                "epoch", Meeting.meeting_time - func.now()
            )
            all_meetings = all_meetings.order_by(time_difference_seconds)
        else:
            all_meetings = all_meetings.order_by(asc(Meeting.meeting_time))

        total_count = all_meetings.count()

        return list(all_meetings.offset(skip).limit(limit).all()), total_count

    def get_with_nick_name(self, db: Session, nick_name: str):
        profile = db.query(Profile).filter(Profile.nick_name == nick_name).first()
        return profile

    def check_student_card_verifiy(self, db: Session, user_id: int) -> bool:
        profile = self.get_by_user_id(db=db, user_id=user_id)
        student_card = (
            db.query(StudentVerification)
            .filter(StudentVerification.profile_id == profile.id)
            .first()
        )
        if (
            not student_card
            or not student_card.verification_status == ReultStatusEnum.APPROVE.value
        ):
            raise HTTPException(status_code=403, detail="Need to student-card verifiy")
        return True

    def get_random_nick_name(self, db: Session, os_lang: str):
        kr_nick_name, en_nick_name = None
        if os_lang == "kr":
            while True:
                response = requests.get(settings.NICKNAME_API)

                # API 요청이 성공했는지 확인
                if response.status_code != 200:
                    # 잠시 후에 다시 시도
                    time.sleep(3)  # 3초 대기
                    continue

                data = response.json()
                kr_nick_name = data.get("words")[0]

                check_exists = self.get_with_nick_name(db=db, nick_name=kr_nick_name)

                # 중복되지 않은 닉네임이면 break
                if check_exists is None:
                    break

                # 중복된 경우, 잠시 대기 후 다시 시도
                time.sleep(2)  # 2초 대기
        elif os_lang == "en":
            s3_client = get_aws_client()
            en_nick_name = data.get("en_nick_name")

        return {"kr_nick_name": kr_nick_name, "en_nick_name": en_nick_name}


profile = CRUDProfile(Profile)
