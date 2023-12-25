import pytest
import json
from tests.confest import client, session, create_test_data

from schemas import user as user_schmea


class TestLogin:
    def test_register_user(self, client, create_test_data):
        # 테스트 데이터 준비
        university, nationality = create_test_data

        obj_in = user_schmea.UserRegister(
            email="ssss@example.com",
            password="string",
            name="string",
            birth="2011-12-25",
            gender="male",
            sns_type="string",
            sns_id="string",
            fcm_token="string",
            nationality_ids=[nationality.id],
            university_id=university.id,
            department="string",
            education_status="string",
            terms_mandatory=True,
            terms_optional=False,
            terms_push=False,
        )

        json_data = json.loads(obj_in.model_dump_json())

        # HTTP 요청 시뮬레이션
        response = client.post("/v1/register", json=json_data)
        # 응답 검증
        assert response.status_code == 200, response.content
        assert "token" in response.json()
        assert response.json()["email"] == json_data["email"]
