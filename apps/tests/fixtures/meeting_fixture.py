import pytest

from .user_fixture import test_user
from ..factories import MeetingFactory, UserFactory


@pytest.fixture(scope="function")
def test_meeting(session, test_user):
    participants = [
        UserFactory(name="test1", with_nationality=True, with_profile=True),
        UserFactory(name="test2", with_nationality=True, with_profile=True),
    ]

    meeting = MeetingFactory(creator=test_user, meeting_users=participants)
    return meeting
