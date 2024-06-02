import json

from tests.confest import *
from schemas import user as user_schmea


def test_get_user(client, test_user):

    response = client.get(f"v1/users/{test_user.id}")

    assert response.status_code == 200, response.content


def test_delete_user(client, test_user):
    user_id = test_user.id
    response = client.delete(f"v1/user/{user_id}")

    get_response = client.get(f"v1/users/{user_id}")

    assert get_response.status_code == 200, get_response.content

    data = get_response.json()

    assert data["is_active"] == False


def test_save_deletion_requests(client):

    response = client.post("v1/deletion-requests", json={"reason": "test"})

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["reason"] == "test"


def test_update_user(client, test_user, test_nationality):
    user_id = test_user.id
    test_name = f"update_test_user"
    test_nation_id = test_nationality[0].id

    update_schema = user_schmea.UserUpdate(
        name=test_name,
        nationality_ids=[
            test_nation_id,
        ],
    )

    json_data = json.loads(update_schema.model_dump_json())

    response = client.put(f"v1/user/{user_id}", json=json_data)

    assert response.status_code == 200, response.content

    data = response.json()
    assert data["name"] == test_name
    assert test_nation_id in [d["nationality"]["id"] for d in data["user_nationality"]]


def test_get_user_university(client, test_user):
    user_id = test_user.id

    response = client.get(f"v1/user/{user_id}/university")

    assert response.status_code == 200, response.content


def test_get_user_nationality(client, test_user):
    user_id = test_user.id

    response = client.get(f"v1/user/{user_id}/nationality")

    assert response.status_code == 200, response.content


def test_update_user_university(client, test_user):
    user_id = test_user.id

    test_department = "test_department"
    test_education_status = "test_education_status"

    update_schema = {
        "department": test_department,
        "education_status": test_education_status,
    }

    response = client.put(f"v1/user/{user_id}/university", json=update_schema)

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["department"] == test_department
    assert data["education_status"] == test_education_status


# def test_get_report_by_user(session, client, test_user):
#     user_id = test_user.id

#     report = create_test_report(session=session, reason="test", reporter_id=user_id)

#     response = client.get(f"v1/user/{user_id}/report")

#     assert response.status_code == 200, response.content
