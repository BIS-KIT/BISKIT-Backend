import pytest

from .base import session
from .user_fixture import test_user
from .utility_fixture import test_university, test_language
from models import profile as profile_models


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
