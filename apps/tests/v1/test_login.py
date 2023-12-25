import pytest
from tests.confest import client, session


class TestLogin:
    def setup_method(self):
        return

    def teardown_mothod(self):
        return

    def test_register_user(client):
        # 테스트 데이터 준비
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User",
            "birth": "2000-01-01",
            "gender": "M",
            "sns_type": None,
            "sns_id": None,
            "fcm_token": None,
            "terms_mandatory": True,
            "terms_optional": False,
            "terms_push": False,
            "university_id": 1,
            "department": "Computer Science",
            "education_status": "Undergraduate",
            "nationality_ids": [1],
        }

        # HTTP 요청 시뮬레이션
        response = client.post("/register", json=user_data)

        # 응답 검증
        assert response.status_code == 200
        assert "token" in response.json()
        assert response.json()["email"] == user_data["email"]
