import pytest
import requests

BASE_URL = "https://reqres.in/api"


def test_post_with_invalid_api_key_is_rejected():
    response = requests.post(
        f"{BASE_URL}/users",
        json={"name": "x", "job": "y"},
        headers={"x-api-key": "not-a-real-key"},
        timeout=10,
    )
    assert response.status_code == 403
    assert response.json().get("error") == "invalid_api_key"


@pytest.mark.xfail(strict=True, reason="ReqRes currently serves GET /users/2 without a key")
def test_get_without_api_key_is_rejected():
    response = requests.get(f"{BASE_URL}/users/2", timeout=10)
    assert response.status_code == 401


@pytest.mark.xfail(strict=True, reason="ReqRes currently serves GET /users/2 with an invalid key")
def test_get_with_invalid_api_key_is_rejected():
    response = requests.get(
        f"{BASE_URL}/users/2", headers={"x-api-key": "not-a-real-key"}, timeout=10
    )
    assert response.status_code == 403


def test_register_without_password_returns_400(api):
    response = api.post(
        f"{BASE_URL}/register", json={"email": "eve.holt@reqres.in"}, timeout=10
    )
    assert response.status_code == 400
    assert "error" in response.json()


def test_unknown_resource_returns_404(api):
    response = api.get(f"{BASE_URL}/unknown/23", timeout=10)
    assert response.status_code == 404