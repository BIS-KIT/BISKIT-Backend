import pytest
from datetime import timedelta, datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy_utils import database_exists, create_database

from main import app
from core.config import settings
from core.security import create_access_token
from database.session import Base, get_db
from crud.user import get_password_hash
from models.base import ModelBase
from models import utility as utility_models
from models import user as user_models
from models import profile as profile_models
from models import meeting as meeting_models


DATABASE_URL = f"postgresql+psycopg2://postgres:{settings.DB_ROOT_PASSWORD}@maindb:5432/{settings.TEST_DB}"

engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if not database_exists(engine.url):
    create_database(engine.url)

ModelBase.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def session():
    ModelBase.metadata.drop_all(bind=engine)
    ModelBase.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    # app에서 사용하는 DB를 오버라이드하는 부분
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="function")
def test_university(session):
    university = utility_models.University(kr_name="서울대학교 ")
    session.add(university)
    session.commit()

    return university


@pytest.fixture(scope="function")
def test_language(session):
    language = utility_models.Language(kr_name="한국어")
    session.add(language)
    session.commit()

    return language


@pytest.fixture(scope="function")
def test_tag(session):
    tag = utility_models.Tag(name="Networking")
    session.add(tag)
    session.commit()
    return tag


@pytest.fixture(scope="function")
def test_topic(session):
    topic = utility_models.Topic(name="Technology")
    session.add(topic)
    session.commit()
    return topic


@pytest.fixture(scope="function")
def test_nationality(session):
    nationality1 = utility_models.Nationality(kr_name="대한민국")
    nationality2 = utility_models.Nationality(kr_name="미국")
    session.add(nationality1)
    session.add(nationality2)
    session.commit()
    return nationality1, nationality2


@pytest.fixture(scope="function")
def test_user(session, test_nationality, test_university):
    nationality1, nationality2 = test_nationality
    test_university_fixture = test_university

    user = user_models.User(
        email="test@gmail.com",
        password=get_password_hash("guswns95@@"),
        sns_type="kakao",
        sns_id="testsnslogin",
        name="이현준",
        birth="2000-12-13",
        gender="male",
        fcm_token="e5k60HCtTo-NPXw1L1OIGe:APA91bEvp9T5wTAjTEq5yEQFaExjbA8LpkKr_C92t-5_XlGvWQh4cVKSxQYb6ybysMlbwd9hV-RMCyoR_VfjS1gqxV0eIPI0Pzcd_ukYGAmvEPuyETU8NXvKBeE_urAxKBHCOpsPLWz8",
    )
    session.add(user)
    session.flush()

    # Consent 객체 생성 및 연결
    consent = user_models.Consent(
        user_id=user.id, terms_mandatory=True, terms_optional=False, terms_push=False
    )
    session.add(consent)

    # UserNationality 객체 생성 및 연결
    user_nationality1 = user_models.UserNationality(
        user_id=user.id, nationality_id=nationality1.id
    )
    user_nationality2 = user_models.UserNationality(
        user_id=user.id, nationality_id=nationality2.id
    )
    session.add(user_nationality1)
    session.add(user_nationality2)

    user_university = profile_models.UserUniversity(
        department="test_department",
        education_status="test_status",
        university_id=test_university_fixture.id,
        user_id=user.id,
    )

    session.add(user_university)

    session.commit()

    return user


@pytest.fixture(scope="function")
def test_profile(session, test_user, test_university, test_language):
    language = test_language
    university = test_university
    user = test_user

    profile = profile_models.Profile(
        user_id=user.id,
        profile_photo="test",
        nick_name="test_nick",
        context="introduction",
        is_default_photo=False,
    )
    session.add(profile)
    session.flush()

    intoroduction = profile_models.Introduction(
        profile_id=profile.id, keyword="운동", context="건강"
    )

    available_language = profile_models.AvailableLanguage(
        profile_id=profile.id, language_id=language.id, level="BASIC"
    )

    student_verification = profile_models.StudentVerification(
        profile_id=profile.id, verification_status="APPROVE", student_card="test_image"
    )

    user_university = profile_models.UserUniversity(
        university_id=university.id,
        department="대학원",
        education_status="재학중",
        profile_id=profile.id,
    )
    session.add(intoroduction)
    session.add(available_language)
    session.add(student_verification)
    session.add(user_university)
    session.commit()
    return profile


@pytest.fixture(scope="function")
def test_token(session, test_user):
    user = test_user

    token_data = {"sub": user.email, "auth_method": "email"}
    access_token = create_access_token(
        data=token_data, expires_delta=timedelta(minutes=1)
    )
    return access_token


def create_test_meeting(
    session, user_id: int, test_profile, test_topic, test_tag, test_language
):

    meeting_obj = meeting_models.Meeting(
        name="Test Meeting",
        location="Test Location",
        description="This is a test meeting.",
        meeting_time=datetime.now(),
        max_participants=10,
        current_participants=5,
        korean_count=3,
        foreign_count=2,
        chat_id="testChatId123",
        place_url="http://example.com/test-meeting-location",
        x_coord="127.001",
        y_coord="37.001",
        image_url="http://example.com/test-meeting-image.jpg",
        is_active=True,
        creator_id=user_id,
    )
    session.add(meeting_obj)
    session.flush()  # Use flush to ensure meeting.id is populated

    # Associate Language, Tag, and Topic with the Meeting
    meeting_language = profile_models.MeetingLanguage(
        meeting_id=meeting_obj.id, language_id=test_language.id
    )
    meeting_tag = profile_models.MeetingTag(
        meeting_id=meeting_obj.id, tag_id=test_tag.id
    )
    meeting_topic = profile_models.MeetingTopic(
        meeting_id=meeting_obj.id, topic_id=test_topic.id
    )

    session.add_all([meeting_language, meeting_tag, meeting_topic])
    session.commit()
    return meeting_obj


@pytest.fixture(scope="function")
def test_review(session, test_user, test_meeting):
    meeting_fixture = test_meeting
    user_fixture = test_user

    review_obj = meeting_models.Review(
        context="test_review",
        image_url="http://example.com/test_review_image",
        meeting_id=meeting_fixture,
        creator_id=user_fixture.id,
    )

    session.add(review_obj)
    session.commit()
    return review_obj
