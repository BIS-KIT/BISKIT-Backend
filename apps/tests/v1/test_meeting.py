import json
import pytest
from datetime import datetime, timedelta

from tests.confest import *
from schemas import meeting as meeting_schmea
from schemas.enum import ReultStatusEnum


# @pytest.mark.skip()
def test_create_meeting(client, test_user, test_tag, test_topic, test_language):
    meeting_time = datetime.now() + timedelta(days=3)

    test_custom_tag = "test_tag"
    test_custom_topic = "test_topic"

    meeting_create_schema = meeting_schmea.MeetingCreate(
        name="test_meeting",
        location="test_loc",
        meeting_time=meeting_time,
        max_participants=4,
        custom_tags=[test_custom_tag],
        custom_topics=[test_custom_topic],
        creator_id=test_user.id,
        tag_ids=[test_tag.id],
        topic_ids=[test_topic.id],
        language_ids=[test_language.id],
    )

    json_data = json.loads(meeting_create_schema.model_dump_json())

    response = client.post("v1/meeting", json=json_data)

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["creator"]["id"] == test_user.id
    assert data["name"] == meeting_create_schema.name
    assert len(data["tags"]) == 2
    assert data["korean_count"] != None
    assert data["foreign_count"] == 0


# @pytest.mark.skip()
def test_get_meeting_requests(client, session, test_meeting, test_user):
    test_join_request = create_test_join_request(
        session=session, user_id=test_user.id, meeting_id=test_meeting.id
    )

    response = client.get(f"v1/meetings/{test_meeting.id}/requests")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["total_count"] == 1


# @pytest.mark.skip()
def test_check_meeting_request_status(client, session, test_user, test_meeting):
    test_join_request = create_test_join_request(
        session=session, user_id=test_user.id, meeting_id=test_meeting.id
    )

    response = client.get(f"v1/meeting/{test_meeting.id}/user/{test_user.id}")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["status"] == ReultStatusEnum.PENDING


# @pytest.mark.skip()
def test_join_meeting_request(
    session, client, test_meeting, test_nationality, test_university, test_language
):
    test_user = create_test_user(
        session=session,
        test_nationality=test_nationality,
        test_university=test_university,
        test_language=test_language,
    )

    join_requst_schema = meeting_schmea.MeetingUserCreate(
        meeting_id=test_meeting.id, user_id=test_user["id"]
    )

    json_data = json.loads(join_requst_schema.model_dump_json())

    response = client.post("v1/meeting/join/request", json=json_data)

    assert response.status_code == 200, response.content


# @pytest.mark.skip()
def test_join_meeting_approve(
    session, client, test_meeting, test_nationality, test_university, test_language
):
    test_user = create_test_user(
        session=session,
        test_nationality=test_nationality,
        test_university=test_university,
        test_language=test_language,
    )

    meeting_request = create_test_meeting_user(
        session=session, user_id=test_user["id"], meeting_id=test_meeting.id
    )

    response = client.post(f"/v1/meeting/join/approve?obj_id={meeting_request['id']}")

    assert response.status_code == 201, response.content

    data = response.json()

    assert data["status"] == ReultStatusEnum.APPROVE


# @pytest.mark.skip()
def test_exit_meeting(session, client):
    pass


# @pytest.mark.skip()
def test_join_meeting_reject():
    pass


# @pytest.mark.skip()
def test_get_meetings_by_user_university():
    pass


# @pytest.mark.skip()
def test_get_meetings_detail():
    pass


# @pytest.mark.skip()
def test_delete_meeting():
    pass


# @pytest.mark.skip()
def test_update_meeting():
    pass


# @pytest.mark.skip()
def test_get_meeting_with_filter():
    pass


# @pytest.mark.skip()
def test_get_meeting_all_review():
    pass


# @pytest.mark.skip()
def test_create_review():
    pass


# @pytest.mark.skip()
def test_update_review():
    pass


# @pytest.mark.skip()
def test_delete_review():
    pass
