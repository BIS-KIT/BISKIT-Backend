import json
import pytest
from datetime import datetime, timedelta

import crud
from tests.confest import *
from schemas import system as system_schmea


def test_get_systems(client, test_user, test_system):
    response = client.get(f"v1/system/{test_user.id}")

    assert response.status_code == 200, response.content


def test_update_system(client, test_user, test_system):
    update_schema = system_schmea.SystemUpdate(system_language="en", etc_alarm=False)

    json_data = json.loads(update_schema.model_dump_json(exclude_unset=True))

    response = client.put(f"v1/system/{test_system.id}", json=json_data)

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["system_language"] == json_data["system_language"]
    assert data["etc_alarm"] == json_data["etc_alarm"]


def test_get_report(client, test_report):

    response = client.get(f"v1/report/{test_report.id}")

    assert response.status_code == 200, response.content


def test_create_report(client, test_user):
    test_reason = "test_reason"
    test_content = "test_content"
    test_content_id = 3

    create_schmea = system_schmea.ReportCreate(
        reason=test_reason,
        content_type=test_content,
        content_id=test_content_id,
        reporter_id=test_user.id,
    )

    json_data = json.loads(create_schmea.model_dump_json(exclude_unset=True))

    response = client.post("v1/report", json=json_data)

    assert response.status_code == 200, response.content


def test_create_ban(
    client, session, test_user, test_language, test_nationality, test_university
):
    reporter_user = create_test_user(
        session=session,
        test_language=test_language,
        test_nationality=test_nationality,
        test_university=test_university,
    )

    create_schmea = system_schmea.BanCreate(
        target_id=test_user.id, reporter_id=reporter_user["id"]
    )

    json_data = json.loads(create_schmea.model_dump_json(exclude_unset=True))

    response = client.post("v1/ban", json=json_data)

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["target"]["id"] == test_user.id


def test_unban_with_ban_obj(client, test_ban):

    ban_ids_to_unban = [test_ban.id]

    response = client.request(method="DELETE", url="v1/ban", json=ban_ids_to_unban)

    assert response.status_code == 200, response.content


def test_unban_with_user_id(session, client, test_ban):

    response = client.delete(
        f"v1/unban?reporter_id={test_ban.reporter_id}&target_id={test_ban.target_id}"
    )

    assert response.status_code == 200, response.content


def test_check_user_ban(client, test_ban):
    target_ids = [test_ban.target_id]

    response = client.get(
        f"v1/bans/{test_ban.reporter_id}?target_ids={','.join(map(str, target_ids))}"
    )

    assert response.status_code == 200, response.content

    data = response.json()

    assert data[0]["id"] == test_ban.id


def test_read_ban_by_user_id(client, test_ban):

    response = client.get(f"v1/ban/{test_ban.reporter_id}")

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["ban_list"][0]["id"] == test_ban.id
