# import pytest

# from .base import session
# from .user_fixture import test_user
# from models import alarm as alarm_models


# @pytest.fixture(scope="function")
# def test_alarm(session, test_user):
#     alarm = alarm_models.Alarm(
#         title="test_alarm", content="test_alarm", is_read=False, user_id=test_user.id
#     )
#     session.add(alarm)
#     session.commit()
#     return alarm
