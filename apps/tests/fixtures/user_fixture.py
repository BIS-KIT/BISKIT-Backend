import pytest

from ..factories import UserFactory, DeletionRequestFactory, UserNationalityFactory


@pytest.fixture(scope="function")
def test_user():
    test_user = UserFactory(with_nationality=True, with_profile=True)
    return test_user


@pytest.fixture(scope="function")
def test_deletion_request():
    deletion_request = DeletionRequestFactory()
    return deletion_request
