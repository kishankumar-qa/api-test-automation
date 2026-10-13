import os

import pytest
import requests

from jsonschema import validate

BASE_URL = "https://reqres.in/api"

USER_SCHEMA = {
    "type": "object",
    "required": ["data"],
    "properties": {
        "data": {
            "type": "object",
            "required": ["id", "email", "first_name", "last_name", "avatar"],
            "properties": {
                "id": {"type": "integer"},
                "email": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "avatar": {"type": "string"},
            },
        }
    },
}

CREATED_USER_SCHEMA = {
    "type": "object",
    "required": ["name", "job", "id", "createdAt"],
    "properties": {
        "name": {"type": "string"},
        "job": {"type": "string"},
        "id": {"type": ["string", "integer"]},
        "createdAt": {"type": "string"},
    },
}
@pytest.fixture(scope="session")
def api():
    """A requests Session that sends the API key on every call."""
    key = os.environ.get("REQRES_API_KEY")
    if not key:
        pytest.fail("REQRES_API_KEY is not set. Run: set REQRES_API_KEY=your_key")
    session = requests.Session()
    session.headers.update({"x-api-key": key})
    yield session
    session.close()


def test_get_users_page_2(api):
    response = api.get(f"{BASE_URL}/users", params={"page": 2}, timeout=10)
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 2
    assert len(body["data"]) > 0


def test_create_user(api):
    payload = {"name": "Kishan", "job": "API Automation Specialist"}
    response = api.post(f"{BASE_URL}/users", json=payload, timeout=10)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == payload["name"]
    assert body["job"] == payload["job"]
    assert "id" in body


@pytest.mark.parametrize("user_id, expected_status", [(2, 200), (5, 200), (23, 404)])
def test_get_single_user_status(api, user_id, expected_status):
    response = api.get(f"{BASE_URL}/users/{user_id}", timeout=10)
    assert response.status_code == expected_status


def test_update_user_put(api):
    payload = {"name": "Kishan", "job": "Senior API Automation Specialist"}
    response = api.put(f"{BASE_URL}/users/2", json=payload, timeout=10)
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == payload["name"]
    assert body["job"] == payload["job"]
    assert "updatedAt" in body


def test_delete_user(api):
    response = api.delete(f"{BASE_URL}/users/2", timeout=10)
    assert response.status_code == 204
    assert response.text == ""


def test_login_without_password_returns_400(api):
    response = api.post(
        f"{BASE_URL}/login", json={"email": "eve.holt@reqres.in"}, timeout=10
    )
    assert response.status_code == 400
    assert "error" in response.json()


def test_get_user_matches_schema(api):
    response = api.get(f"{BASE_URL}/users/2", timeout=10)
    assert response.status_code == 200
    validate(instance=response.json(), schema=USER_SCHEMA)


def test_create_user_matches_schema(api):
    payload = {"name": "Kishan", "job": "API Automation Specialist"}
    response = api.post(f"{BASE_URL}/users", json=payload, timeout=10)
    assert response.status_code == 201
    validate(instance=response.json(), schema=CREATED_USER_SCHEMA)