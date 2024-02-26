import pytest, random
from datetime import timedelta, datetime

from .utility_fixture import test_topic, test_tag, test_language
from crud.user import get_password_hash
from models import profile as profile_models
from models import meeting as meeting_models
from models import user as user_models
from models import utility as utility_models
from models import system as system_models
from schemas.enum import MyMeetingEnum


def create_test_meeting(
    session,
    user_id: int,
    test_topic,
    test_tag,
    test_language,
    meeting_time=datetime.now(),
):

    meeting_obj = meeting_models.Meeting(
        name="Test Meeting",
        location="Test Location",
        description="This is a test meeting.",
        meeting_time=meeting_time,
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
    meeting_language = meeting_models.MeetingLanguage(
        meeting_id=meeting_obj.id, language_id=test_language.id
    )
    meeting_tag = meeting_models.MeetingTag(
        meeting_id=meeting_obj.id, tag_id=test_tag.id
    )
    meeting_topic = meeting_models.MeetingTopic(
        meeting_id=meeting_obj.id, topic_id=test_topic.id
    )

    session.add_all([meeting_language, meeting_tag, meeting_topic])
    session.commit()
    return meeting_obj.to_dict()


def create_test_meeting_user(
    session, user_id: int, meeting_id: int, is_approve: bool = False
):
    status = MyMeetingEnum.APPROVE if is_approve else MyMeetingEnum.PENDING

    meeting_user_obj = meeting_models.MeetingUser(
        status=status, meeting_id=meeting_id, user_id=user_id
    )
    session.add(meeting_user_obj)
    session.commit()
    return meeting_user_obj.to_dict()


def create_test_user(session, test_nationality, test_university, is_sns: bool = False):
    nationality1, nationality2 = test_nationality
    test_university_fixture = test_university

    start_date = datetime(1990, 1, 1)
    end_date = datetime(2010, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_birth = start_date + timedelta(days=random_number_of_days)
    random_birth_str = random_birth.strftime("%Y-%m-%d")

    if is_sns:
        user = user_models.User(
            email="test1@gmail.com",
            password=get_password_hash("guswns95@@"),
            sns_type="kakao",
            sns_id="testsnslogin",
            name="이현준",
            birth=random_birth_str,
            gender="male",
            fcm_token="e5k60HCtTo-NPXw1L1OIGe:APA91bEvp9T5wTAjTEq5yEQFaExjbA8LpkKr_C92t-5_XlGvWQh4cVKSxQYb6ybysMlbwd9hV-RMCyoR_VfjS1gqxV0eIPI0Pzcd_ukYGAmvEPuyETU8NXvKBeE_urAxKBHCOpsPLWz8",
        )
    else:
        user = user_models.User(
            email="test2@gmail.com",
            password=get_password_hash("guswns95@@"),
            name="이현준",
            birth=random_birth_str,
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

    return user.to_dict()


def create_test_university(session, name: str):
    university_obj = utility_models.University(kr_name=name)
    session.add(university_obj)
    session.commit()
    return university_obj.to_dict()


def create_test_report(session, reason: str, reporter_id: int):

    report_obj = system_models.Report(reason=reason, reporter_id=reporter_id)
    session.add(report_obj)
    session.commit()
    return report_obj.to_dict()


def create_test_review(session):
    pass
