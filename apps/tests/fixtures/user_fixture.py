import pytest
from datetime import timedelta

from .base import session
from .utility_fixture import test_nationality, test_university, test_language
from core.security import create_access_token
from crud.user import get_password_hash
from models import user as user_models
from models import profile as profile_models


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
        fcm_token="dX2jZUJjTQKE_N3trPHQNW:APA91bGHlmm5sMqN4f3vXXF-hY_g593GKo9JdiRABeH2rGj9CW-_WbVb8xybLfI3rckHR47rasfd9qMI-dDSmMtk5ofj5ckafCpvOeTojsDKlthnFgKlTq6tLFqFhAicSz6rhPEqJV8p",
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
def test_user_ios(session, test_nationality, test_university):
    nationality1, nationality2 = test_nationality
    test_university_fixture = test_university

    user = user_models.User(
        email="test_ios@gmail.com",
        password=get_password_hash("guswns95@@"),
        sns_type="kakao",
        sns_id="testsnslogin",
        name="김유나",
        birth="2000-08-04",
        gender="female",
        fcm_token="eoKqrEfH3E8dnxN9XaTwRj:APA91bGmgnbDCvH7ZKWM51IZ0pDI2JXUS7z3o9qFyQLEILTyVCgiMPE2BED_fUQiQxM85FcW-xHilSUaJ4oD72gOg5zmHpYAH0smajwXAdwTCV8g4j71ifQE77I-KffqhHg5qAjE3yFN",
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
def test_token(session, test_user):
    user = test_user

    token_data = {"sub": user.email, "auth_method": "email"}
    access_token = create_access_token(
        data=token_data, expires_delta=timedelta(minutes=1)
    )
    return access_token
