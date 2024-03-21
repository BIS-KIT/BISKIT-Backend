import json
import pytest
from datetime import datetime, timedelta

from tests.confest import *
from schemas import meeting as meeting_schmea
from schemas.enum import ReultStatusEnum


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


def test_get_meeting_requests(client, session, test_meeting, test_user):
    test_join_request = create_test_join_request(
        session=session, user_id=test_user.id, meeting_id=test_meeting.id
    )

    response = client.get(f"v1/meetings/{test_meeting.id}/requests")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["total_count"] == 1


def test_check_meeting_request_status(client, session, test_user, test_meeting):
    test_join_request = create_test_join_request(
        session=session, user_id=test_user.id, meeting_id=test_meeting.id
    )

    response = client.get(f"v1/meeting/{test_meeting.id}/user/{test_user.id}")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["status"] == ReultStatusEnum.PENDING


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


def test_exit_meeting(
    session, client, test_meeting, test_language, test_nationality, test_university
):
    test_user = create_test_user(
        session=session,
        test_language=test_language,
        test_nationality=test_nationality,
        test_university=test_university,
        name="test_user",
    )

    meeting_request = create_test_meeting_user(
        session=session,
        user_id=test_user["id"],
        meeting_id=test_meeting.id,
        is_approve=True,
    )

    response = client.post(f"v1/meeting/{test_meeting.id}/user/{test_user['id']}/exit")

    assert response.status_code == 200, response.content


def test_join_meeting_reject(
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

    response = client.post(f"/v1/meeting/join/reject?obj_id={meeting_request['id']}")

    assert response.status_code == 200, response.content


def test_get_meetings_by_user_university(
    session,
    client,
    test_user,
    test_topic,
    test_tag,
    test_language,
    test_university,
    test_nationality,
):

    test_meeting = create_test_meeting(
        session=session,
        user_id=test_user.id,
        university_id=test_university.id,
        test_tag=test_tag,
        test_topic=test_topic,
        test_language=test_language,
    )

    test_user_for_meeting = create_test_user(
        session=session,
        test_nationality=test_nationality,
        test_university=test_university,
        test_language=test_language,
        name="test_usear",
    )
    test_meeting2 = create_test_meeting(
        session=session,
        user_id=test_user_for_meeting["id"],
        university_id=test_university.id,
        test_tag=test_tag,
        test_topic=test_topic,
        test_language=test_language,
    )

    response = client.get(f"v1/meeting/{test_user.id}/universty")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["total_count"] == 2


def test_get_meetings_detail(client, test_meeting):

    response = client.get(f"v1/meeting/{test_meeting.id}")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["id"] == test_meeting.id


def test_delete_meeting(client, test_meeting):

    response = client.delete(f"v1/meeting/{test_meeting.id}")

    assert response.status_code == 204, response.content


def test_update_meeting(client, test_meeting):
    update_name = "update_test_meeting"
    update_participants = test_meeting.max_participants + 1

    update_schmea = meeting_schmea.MeetingUpdate(
        name=update_name, max_participants=update_participants
    )

    json_data = json.loads(update_schmea.model_dump_json(exclude_unset=True))

    response = client.put(f"v1/meeting/{test_meeting.id}", json=json_data)

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["name"] == update_name
    assert data["max_participants"] == update_participants


def test_get_meeting_with_filter():
    pass


def test_get_meeting_all_review(session, client, test_user, test_meeting):
    test_review = create_test_review(
        session=session, meeting_id=test_meeting.id, user_id=test_user.id
    )

    response = client.get(f"v1/meeting/reviews/{test_user.id}")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["reviews"][0]["context"] == test_review["context"]


def test_create_review(client, test_user, test_meeting):
    test_context = "test_context"
    meeting_id = test_meeting.id
    review_schema = meeting_schmea.ReviewIn(
        context=test_context, creator_id=test_user.id
    )

    json_data = json.loads(review_schema.model_dump_json(exclude_unset=True))

    response = client.post(f"v1/meeting/{meeting_id}/reviews", json=json_data)

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["meeting_id"] == meeting_id
    assert data["context"] == test_context


def test_update_review(session, client, test_user, test_meeting):
    update_test_context = "update test context"

    test_review = create_test_review(
        session=session, meeting_id=test_meeting.id, user_id=test_user.id
    )

    update_review_schema = meeting_schmea.ReviewUpdateIn(context=update_test_context)

    json_data = json.loads(update_review_schema.model_dump_json(exclude_unset=True))

    response = client.put(f"v1/review/{test_review['id']}", json=json_data)

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["context"] == update_test_context


def test_delete_review(session, client, test_user, test_meeting):
    test_review = create_test_review(
        session=session, meeting_id=test_meeting.id, user_id=test_user.id
    )

    response = client.delete(f"v1/review/{test_review['id']}")

    assert response.status_code == 200, response.content
