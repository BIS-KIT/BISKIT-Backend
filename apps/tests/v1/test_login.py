import pytest
from tests.confest import client, session


class TestLogin:
    def test_register_user(self, client):
        # 테스트 데이터 준비
        user_data = {
            "email": "ssss@example.com",
            "password": "string",
            "name": "string",
            "birth": "2011-12-25",
            "gender": "male",
            "sns_type": "string",
            "sns_id": "string",
            "fcm_token": "string",
            "nationality_ids": [2],
            "university_id": 3,
            "department": "string",
            "education_status": "string",
            "terms_mandatory": True,
            "terms_optional": False,
            "terms_push": False,
        }

        # HTTP 요청 시뮬레이션
        response = client.post("/v1/register", json=user_data)

        # 응답 검증
        assert response.status_code == 200
        assert "token" in response.json()
        assert response.json()["email"] == user_data["email"]
