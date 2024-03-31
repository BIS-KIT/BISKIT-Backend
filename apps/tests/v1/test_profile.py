import json
import pytest
from datetime import datetime, timedelta

from tests.confest import (
    client,
    session,
    test_nationality,
    test_university,
    test_user,
    test_token,
    test_profile,
    test_language,
    test_tag,
    test_topic,
    create_test_meeting,
    create_test_meeting_user,
    create_test_user,
)

from schemas.enum import ReultStatusEnum, LanguageLevelEnum
from schemas import profile as profile_schmea
from models import profile as profile_models


def test_get_profile_photos(
    client,
    test_user,
    test_profile,
    test_nationality,
):
    # 테스트용 사용자 ID 목록 생성
    user_ids = [test_user.id]

    # get_profile_photos 엔드포인트 호출
    response = client.get("v1/profile/photos", params={"user_ids": user_ids})

    # 응답 상태 코드 검증
    assert response.status_code == 200

    # 응답 데이터 검증
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == test_user.id
    assert data[0]["profile_photo"] == test_profile.profile_photo
    assert data[0]["nick_name"] == test_profile.nick_name
    assert "nationalities" in data[0]


def test_check_nick_name(client, test_profile):
    nick_name = test_profile.nick_name

    response = client.get("v1/profile/nick-name", params={"nick_name": nick_name})

    assert response.status_code != 200


def test_student_varification(client, test_profile):
    user_id = test_profile.user_id
    student_card = "test_student_card"

    response = client.post(
        "v1/student-card", params={"user_id": user_id, "student_card": student_card}
    )

    assert response.status_code == 200

    data = response.json()

    assert student_card == data.get("student_card")
    assert ReultStatusEnum.PENDING.value == data.get("verification_status")


def test_read_student_varification(client, test_profile):
    user_id = test_profile.user_id
    test_student_card = test_profile.student_verification

    response = client.get(f"v1/student-card/{user_id}")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data.get("student_card") == test_student_card.student_card
    assert data.get("verification_status") == test_student_card.verification_status


def test_delete_profile_photo(client, test_profile):
    user_id = test_profile.user_id

    response = client.delete(f"v1/profile/{user_id}/photo")

    assert response.status_code == 200, response.content

    assert test_profile.profile_photo == None


def test_create_profile(client, test_user, test_language):
    user_id = test_user.id
    test_language_confest = test_language

    language_schema = profile_schmea.AvailableLanguageIn(
        level="BASIC", language_id=test_language_confest.id
    )

    profile_schema_obj = profile_schmea.ProfileRegister(
        nick_name="test_profile",
        profile_photo="test_profile_photo",
        available_languages=[language_schema],
    )

    json_data = json.loads(profile_schema_obj.model_dump_json())

    # HTTP 요청 시뮬레이션
    response = client.post(f"/v1/profile?user_id={user_id}", json=json_data)

    assert response.status_code == 200

    data = response.json()

    assert data["nick_name"] == "test_profile"
    assert data["profile_photo"] == "test_profile_photo"

    assert data["available_languages"][0]["level"] == "BASIC"


def test_update_profile(client, test_profile):
    test_profile_fixture = test_profile

    available_lang_schmea = profile_schmea.AvailableLanguageIn(
        level="ADVANCED", language_id=1
    )
    introduction_schema = profile_schmea.IntroductionIn(keyword="운동", context="test")
    university_schema = profile_schmea.ProfileUniversityUpdate(education_status="졸업")

    profile_update_schema = profile_schmea.ProfileUpdate(
        nick_name="testname",
        available_languages=[available_lang_schmea],
        introductions=[introduction_schema],
        university_info=university_schema,
    )

    json_data = json.loads(profile_update_schema.model_dump_json())

    response = client.put(f"/v1/profile/{test_profile_fixture.id}", json=json_data)

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["nick_name"] == "testname"
    assert data["introductions"][0]["context"] == "test"
    assert data["available_languages"][0]["level"] == "ADVANCED"
    assert data["user_university"]["education_status"] == "졸업"


def test_get_user_meetings_with_order_by(
    session, client, test_user, test_topic, test_tag, test_language, test_university
):
    user_fixture = test_user

    now = datetime.now()
    test_meeting1 = create_test_meeting(
        session=session,
        user_id=user_fixture.id,
        test_topic=test_topic,
        test_tag=test_tag,
        test_language=test_language,
        meeting_time=now + timedelta(days=2),
        university_id=test_university.id,
    )

    test_meeting2 = create_test_meeting(
        session=session,
        user_id=user_fixture.id,
        test_topic=test_topic,
        test_tag=test_tag,
        test_language=test_language,
        meeting_time=now + timedelta(days=1),
        university_id=test_university.id,
    )

    test_meeting3 = create_test_meeting(
        session=session,
        user_id=user_fixture.id,
        test_topic=test_topic,
        test_tag=test_tag,
        test_language=test_language,
        meeting_time=now,
        university_id=test_university.id,
    )

    response = client.get(
        f"v1/profile/{user_fixture.id}/meetings?order_by=meeting_time"
    )

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["total_count"] == 3

    # test order_by filter
    assert (
        data["meetings"][0]["id"] == test_meeting3["id"]
    ), "Meetings are not in the expected order"
    assert (
        data["meetings"][1]["id"] == test_meeting2["id"]
    ), "Meetings are not in the expected order"
    assert (
        data["meetings"][2]["id"] == test_meeting1["id"]
    ), "Meetings are not in the expected order"


def test_get_user_meetings_with_status(
    session,
    client,
    test_user,
    test_topic,
    test_tag,
    test_language,
    test_nationality,
    test_university,
):
    user_fixture = test_user

    now = datetime.now()
    pending_test_meeting = create_test_meeting(
        session=session,
        user_id=user_fixture.id,
        test_topic=test_topic,
        test_tag=test_tag,
        test_language=test_language,
        meeting_time=now,
        university_id=test_university.id,
    )

    approve_test_meeting = create_test_meeting(
        session=session,
        user_id=user_fixture.id,
        test_topic=test_topic,
        test_tag=test_tag,
        test_language=test_language,
        meeting_time=now,
        university_id=test_university.id,
    )
    # test status filter
    status_test_user = create_test_user(
        session=session,
        test_nationality=test_nationality,
        test_university=test_university,
        test_language=test_language,
    )
    pending_meeting_user = create_test_meeting_user(
        session=session,
        user_id=status_test_user["id"],
        meeting_id=pending_test_meeting["id"],
    )

    approve_meeting_user = create_test_meeting_user(
        session=session,
        user_id=status_test_user["id"],
        meeting_id=approve_test_meeting["id"],
        is_approve=True,
    )

    pending_response = client.get(
        f"v1/profile/{status_test_user['id']}/meetings?status=PENDING"
    )

    assert pending_response.status_code == 200, pending_response.content

    pending_data = pending_response.json()

    assert pending_data["meetings"][0]["id"] == pending_test_meeting["id"]

    approve_response = client.get(
        f"v1/profile/{status_test_user['id']}/meetings?status=APPROVE"
    )

    assert approve_response.status_code == 200, approve_response.content

    approve_data = approve_response.json()

    assert approve_data["meetings"][0]["id"] == approve_test_meeting["id"]
