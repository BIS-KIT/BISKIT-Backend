import pandas as pd
from sqlalchemy.orm import Session
from models.utility import Language, Nationality, University, Topic, Tag
from database.session import SessionLocal
from core.config import settings

# B4:C147 범위 추출 (0부터 시작하는 인덱스를 기준으로)
# B는 2번째 열, C는 3번째 열이라고 가정합니다.
# 1번 시트에서 "B4:C147" 범위의 데이터 가져오기
language_scope = pd.read_excel("DataSet.xlsx", sheet_name=0, header=None).iloc[
    4:147, 1:3
]

# 2번 시트에서 "B4:D250" 범위의 데이터 가져오기
national_scope = pd.read_excel("DataSet.xlsx", sheet_name=1, header=None).iloc[
    3:250, 1:4
]

# 3번 시트에서 "B4:D250" 범위의 데이터 가져오기
university_scope = pd.read_excel("DataSet.xlsx", sheet_name=2, header=None).iloc[
    2:216, 1:8
]


def get_nationality():
    subset = national_scope
    db = SessionLocal()

    try:
        for _, row in subset.iterrows():
            kr_name = str(row[subset.columns[0]])
            en_name = str(row[subset.columns[1]])
            code = str(row[subset.columns[2]]).lower()
            # 해당 국적이 이미 DB에 있는지 확인
            existing_nationality = (
                db.query(Nationality).filter_by(kr_name=kr_name).first()
            )

            # 없으면 새로 추가
            if not existing_nationality:
                nationality = Nationality(kr_name=kr_name, en_name=en_name, code=code)
                db.add(nationality)

        db.commit()
    except Exception as e:
        print(f"Error: {e}")  # 오류 메시지 출력
        db.rollback()
    finally:
        db.close()


def get_language():
    subset = language_scope
    db = SessionLocal()

    try:
        for _, row in subset.iterrows():
            kr_name = row[subset.columns[0]]
            en_name = row[subset.columns[1]]

            # 해당 언어가 이미 DB에 있는지 확인
            existing_language = db.query(Language).filter_by(kr_name=kr_name).first()

            # 없으면 새로 추가
            if not existing_language:
                language = Language(kr_name=kr_name, en_name=en_name)
                db.add(language)

        db.commit()
    except Exception as e:
        print(f"Error: {e}")  # 오류 메시지 출력
        db.rollback()
    finally:
        db.close()


def get_university():
    subset = university_scope
    db = SessionLocal()

    try:
        for _, row in subset.iterrows():
            kr_name = str(row[subset.columns[3]]) or None
            en_name = str(row[subset.columns[4]]) or None
            campus_type = str(row[subset.columns[5]]) or None
            location = str(row[subset.columns[6]]) or None

            existing_university = (
                db.query(University).filter(University.kr_name == kr_name).first()
            )

            if not existing_university:
                university_obj = University(
                    kr_name=kr_name,
                    en_name=en_name,
                    campus_type=campus_type,
                    location=location,
                )
                db.add(university_obj)

        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


def create_fix_topics_tags():
    base_url = settings.S3_URL + "/default_icon/"

    init_data = {
        "topics": {
            "푸드": ("Food", "ic_food_fill_48.svg"),
            "언어교환": ("Language Exchange", "ic_language_exchange_fill_48.svg"),
            "액티비티": ("Activity", "ic_activity_fill_48.svg"),
            "스포츠": ("Sports", "ic_sports_fill_48.svg"),
            "스터디": ("Study", "ic_study_fill_48.svg"),
            "문화/예술": ("Culture/Art", "ic_culture_fill_48.svg"),
            "취미": ("Hobby", "ic_hobby_fill_48.svg"),
            "기타": ("etc", "ic_talk_fill_48.svg"),
        },
        "tags": {
            "영어 못해도 괜찮아요": ("Welcome English begginers", "💬"),
            "혼자와도 괜찮아요": ("It's okay to come alone", None),
            "늦참가능": ("Late Arrival Permitted", "⏳"),
            "한국어 못해도 괜찮아요": ("Welcome Korean begginers", "💬"),
            "비건": ("Vegan", "🌱"),
            "뒷풀이": ("After Party", "🍺"),
            "여자만": ("Only for women", "👩"),
            "남자만": ("Only for men", "👱‍♂️"),
        },
    }

    db = SessionLocal()
    try:
        for kr, (en, icon_image) in init_data["topics"].items():
            topic = db.query(Topic).filter(Topic.kr_name == kr).first()
            if not topic:
                topic = Topic(
                    kr_name=kr,
                    en_name=en,
                    is_custom=False,
                    icon_url=base_url + icon_image,
                )
                db.add(topic)

        for kr, (en, icon) in init_data["tags"].items():
            if not db.query(Tag).filter(Tag.kr_name == kr).first():
                tag = Tag(kr_name=kr, en_name=en, is_custom=False, icon=icon)
                db.add(tag)

        db.commit()

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

    return {"message": "Items created or updated successfully"}


def run_init_data():
    get_language()
    get_nationality()
    get_university()
    create_fix_topics_tags()
