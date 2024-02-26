import json

from tests.confest import *
from schemas import user as user_schmea


@pytest.mark.skip()
def test_read_current_user(client, test_token, test_user):
    test_email = test_user.email

    response = client.get(
        "v1/users/me", headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["email"] == test_email


@pytest.mark.skip()
def test_delete_user(client, test_user):
    user_id = test_user.id
    response = client.delete(f"v1/user/{user_id}")

    get_response = client.get(f"v1/users/{user_id}")

    assert get_response.status_code == 200, get_response.content

    data = get_response.json()

    assert data["is_active"] == False


@pytest.mark.skip()
def test_save_deletion_requests(client):
    delete_request = user_schmea.DeletionRequestCreate(reason="test")

    json_data = json.loads(delete_request.model_dump_json())

    response = client.post("v1/deletion-requests", json=json_data)

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["reason"] == "test"


@pytest.mark.skip()
def test_update_user(session, client, test_user):
    user_id = test_user.id
    test_name = f"test_{test_user.name}"
    test_nation_id = test_user.user_nationality[1].id

    update_schmea = user_schmea.UserUpdate(
        name=test_name,
        nationality_ids=[
            test_nation_id,
        ],
    )

    json_data = json.loads(update_schmea.model_dump_json(exclude_unset=True))

    response = client.put(f"v1/user/{user_id}", json=json_data)

    assert response.status_code == 200, response.content

    data = response.json()

    assert data["name"] == test_name
    assert data["user_nationality"][0]["id"] == test_nation_id
