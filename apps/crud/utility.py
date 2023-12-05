import re
from typing import Optional

from sqlalchemy.orm import Session

from models.utility import Language, Nationality, University, Topic, Tag
from models.profile import UserUniversity
from models import user as user_model
from models import system as system_model
import crud
from core.config import settings


def check_korean(text):
    return bool(re.search("[\u3131-\u3163\uac00-\ud7a3]", text))


class CRUDUtility:
    def get(
        self,
        db: Session,
        language_id: int = None,
        nationality_id: int = None,
        university_id: int = None,
    ):
        if language_id:
            return db.query(Language).filter(Language.id == language_id).first()
        if nationality_id:
            return (
                db.query(Nationality).filter(Nationality.id == nationality_id).first()
            )
        if university_id:
            return db.query(University).filter(University.id == university_id).first()

    def get_university_by_user(self, db: Session, user_id: int):
        return (
            db.query(University)
            .join(UserUniversity)
            .filter(UserUniversity.user_id == user_id)
            .first()
        )

    def get_topic(self, db: Session, topic_id: int):
        return db.query(Topic).filter(Topic.id == topic_id).first()

    def get_tag(self, db: Session, tag_id: int):
        return db.query(Tag).filter(Tag.id == tag_id).first()

    def create_topic(self, db: Session, name: str):
        if check_korean(name):
            db_obj = Topic(kr_name=name)
        else:
            db_obj = Topic(en_name=name)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_tag(self, db: Session, name: str):
        if check_korean(name):
            db_obj = Tag(kr_name=name)
        else:
            db_obj = Tag(en_name=name)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_topic(self, db: Session, topic_id: int):
        db_obj = db.query(Topic).filter(Topic.id == topic_id).delete()
        db.commit()
        return db_obj

    def delete_tag(self, db: Session, tag_id: int):
        db_obj = db.query(Tag).filter(Tag.id == tag_id).delete()
        db.commit()
        return db_obj

    def read_topics(self, db: Session, is_custom: Optional[bool] = None):
        ORDERED_TOPICS = {
            "푸드": 1,
            "언어교환": 2,
            "액티비티": 3,
            "스포츠": 4,
            "스터디": 5,
            "문화/예술": 6,
            "취미": 7,
            "기타": 8,
        }
        if is_custom is None:
            topics = db.query(Topic).all()
        elif is_custom:
            topics = db.query(Topic).filter(Topic.is_custom == True).all()
        else:
            topics = db.query(Topic).filter(Topic.is_custom == False).all()
        return sorted(topics, key=lambda x: ORDERED_TOPICS.get(x.kr_name, 9))

    def read_tags(self, db: Session, is_custom: Optional[bool] = None):
        if is_custom is None:
            return db.query(Tag).all()
        elif is_custom:
            return db.query(Tag).filter(Tag.is_custom == True).all()
        else:
            return db.query(Tag).filter(Tag.is_custom == False).all()

    def create_fix_topics_tags(self, db: Session):
        base_url = settings.S3_URL + "/default_icon/"

        topic_mapping = {
            "푸드": "ic_food_fill_48.svg",
            "스포츠": "ic_sports_fill_48.svg",
            "액티비티": "ic_activity_fill_48.svg",
            "언어교환": "ic_language_exchange_fill_48.svg",
            "스터디": "ic_study_fill_48.svg",
            "문화/예술": "ic_culture_fill_48.svg",
            "취미": "ic_hobby_fill_48.svg",
            "기타": "ic_talk_fill_48.svg",
        }

        topic_fixs_mapping = {
            "푸드": "Food",
            "언어교환": "Language Exchange",
            "액티비티": "Activity",
            "스포츠": "Sprots",
            "스터디": "Study",
            "문화/예술": "Culture/Art",
            "취미": "Hobby",
            "기타": "etc",
        }

        tag_fixs_mapping = {
            "영어 못해도 괜찮아요": "It's okay if you can't speak English",
            "혼자와도 괜찮아요": "It's okay to come alone",
            "늦잠가능": "Sleeping in is okay",
            "한국어 못해도 괜찮아요": "It's okay if you can't speak Korean",
            "비건": "Vegan",
            "뒷풀이": "After Party",
            "여자만": "Only for women",
            "남자만": "Only for men",
        }

        for kr, en in topic_fixs_mapping.items():
            topic = db.query(Topic).filter(Topic.kr_name == kr).first()
            if not topic:
                topic = Topic(kr_name=kr, en_name=en, is_custom=False)
                db.add(topic)
            topic.icon_url = base_url + topic_mapping[kr]

        for kr, en in tag_fixs_mapping.items():
            if not db.query(Tag).filter(Tag.kr_name == kr).first():
                tag = Tag(kr_name=kr, en_name=en, is_custom=False)
                db.add(tag)

        db.commit()
        return {"message": "Items created or updated successfully"}

    def png_to_svg(self, db: Session):
        # tags = db.query(Tag).all()
        topics = db.query(Topic).all()

        for obj in topics:
            if obj.icon_url and obj.icon_url.endswith(".png"):
                obj.icon_url = obj.icon_url.rsplit(".", 1)[0] + ".svg"

        # 필요한 경우, 변경 사항을 데이터베이스에 커밋
        db.commit()

    def create_default_system(self, db: Session):
        users_without_system = (
            db.query(user_model.User).filter(user_model.User.systems == None).all()
        )
        user_ids = [user.id for user in users_without_system]
        for user_id in user_ids:
            crud.system.create_with_default_value(db=db, user_id=user_id)


utility = CRUDUtility()
