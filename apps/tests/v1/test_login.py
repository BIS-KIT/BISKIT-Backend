import pytest
import json
from tests.confest import client, session, test_nationality, test_university

from schemas import user as user_schmea
from models import user as user_models
from models import profile as profile_models


class TestLogin:
    def test_register_user(self, client, session, test_university, test_nationality):
        # 테스트 데이터 준비
        university = test_university
        nationality1, nationality2 = test_nationality

        obj_in = user_schmea.UserRegister(
            email="ssss@example.com",
            password="string",
            name="string",
            birth="2011-12-25",
            gender="male",
            sns_type="string",
            sns_id="string",
            fcm_token="string",
            nationality_ids=[nationality1.id, nationality2.id],
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

        # 데이터베이스 검증
        db_user = (
            session.query(user_models.User)
            .filter(user_models.User.email == json_data["email"])
            .first()
        )
        assert db_user is not None
        assert db_user.name == json_data["name"]

        # Consent 객체 검증
        db_consent = (
            session.query(user_models.Consent)
            .filter(user_models.Consent.user_id == db_user.id)
            .first()
        )
        assert db_consent is not None
        assert db_consent.terms_mandatory == json_data["terms_mandatory"]

        # UserUniversity 객체 검증
        db_user_university = (
            session.query(profile_models.UserUniversity)
            .filter(profile_models.UserUniversity.user_id == db_user.id)
            .first()
        )
        assert db_user_university is not None
        assert db_user_university.university_id == json_data["university_id"]
