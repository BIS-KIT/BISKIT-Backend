import pytest

from ..factories import (
    UserFactory,
    DeletionRequestFactory,
    ProfileFactory,
    StudentVerificationFactory,
)
from schemas.enum import ReultStatusEnum


@pytest.fixture(scope="function")
def test_user():

    test_user = UserFactory(
        with_nationality=True,
        with_profile=True,
    )
    return test_user


@pytest.fixture(scope="function")
def test_user_without_profile():
    test_user = UserFactory(with_nationality=True, with_profile=False)
    return test_user


@pytest.fixture(scope="function")
def test_user_without_student_card():

    test_user = UserFactory(
        with_nationality=True,
    )

    test_profile = ProfileFactory(
        user=test_user,
        with_university=True,
        with_language=True,
        with_introduction=True,
    )

    test_student_card = StudentVerificationFactory(
        verification_status=ReultStatusEnum.APPROVE.name, profile=test_profile
    )

    return test_user


@pytest.fixture(scope="function")
def test_deletion_request():
    deletion_request = DeletionRequestFactory()
    return deletion_request
