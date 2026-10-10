import os

import pytest
import requests

BASE_URL = "https://reqres.in/api"


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