import pytest
from datetime import datetime, timedelta

from .base import session
from .user_fixture import test_user
from .utility_fixture import test_university, test_language, test_tag, test_topic
from models import meeting as meeting_models


@pytest.fixture(scope="function")
def test_meeting(session, test_user, test_topic, test_tag, test_language):
    meeting_time = datetime.now() + timedelta(days=3)

    meeting = meeting_models.Meeting(
        name="Meeting fixture",
        location="Location",
        description="This is a test meeting.",
        meeting_time=meeting_time,
        max_participants=4,
        current_participants=0,
        korean_count=0,
        foreign_count=1,
        chat_id="testChatId",
        place_url="http://example.com",
        x_coord="127.001",
        y_coord="37.001",
        image_url="http://example.com",
        is_active=True,
        creator_id=test_user.id,
    )

    session.add(meeting)
    session.commit()
    return meeting
