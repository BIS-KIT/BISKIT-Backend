import json
from tests.confest import (
    client,
    session,
    test_nationality,
    test_university,
    test_user,
    test_token,
    test_profile,
    test_language,
)

from schemas.enum import ReultStatusEnum
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
