import pytest
import json
from tests.confest import (
    client,
    session,
    test_nationality,
    test_university,
    test_user,
    test_token,
)

from schemas import user as user_schmea
from models import user as user_models
from models import profile as profile_models


class TestLogin:
    def test_register_user(self, client, session, test_university, test_nationality):
        # 테스트 데이터 준비
        university = test_university
        nationality1, nationality2 = test_nationality

        schema_obj = user_schmea.UserRegister(
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

        json_data = json.loads(schema_obj.model_dump_json())

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

    def test_login(self, client, test_user):
        user = test_user

        password = "guswns95@@"

        email_login_schema = user_schmea.UserLogin(
            email=test_user.email, password=password
        )
        sns_login_schema = user_schmea.UserLogin(
            sns_id=test_user.sns_id, sns_type=test_user.sns_type
        )
        email_json_data = json.loads(email_login_schema.model_dump_json())
        sns_json_data = json.loads(sns_login_schema.model_dump_json())

        email_response = client.post("/v1/login", json=email_json_data)
        sns_response = client.post("/v1/login", json=sns_json_data)

        assert email_response.status_code == 200, email_response.content
        assert "access_token" in email_response.json()

        assert sns_response.status_code == 200, sns_response.content
        assert "access_token" in sns_response.json()

    def test_current_password(self, client, test_user):
        user = test_user

        schema_obj = user_schmea.ConfirmPassword(user_id=user.id, password="guswns95@@")

        json_data = json.loads(schema_obj.model_dump_json())

        response = client.post("/v1/confirm-password", json=json_data)

        assert response.status_code == 200, response.content

    def test_change_password(self, client, test_token):
        schema_obj = user_schmea.PasswordChange(new_password="testpassword@@")

        json_data = json.loads(schema_obj.model_dump_json())

        response = client.post(
            "/v1/change-password",
            json=json_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response.status_code == 200, response.content
