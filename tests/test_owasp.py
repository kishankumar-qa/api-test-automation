import pytest
import requests

pytestmark = pytest.mark.owasp

BASE = "http://127.0.0.1:8000/v1/notes"


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# API1:2023 Broken Object Level Authorization
@pytest.mark.xfail(strict=True, reason="Mock has no ownership check: Alice can read Bob's note")
def test_user_cannot_read_another_users_note(ai_server):
    response = requests.get(f"{BASE}/2", headers=auth("token-alice"), timeout=10)
    assert response.status_code in (403, 404)


def test_user_can_read_own_note(ai_server):
    response = requests.get(f"{BASE}/1", headers=auth("token-alice"), timeout=10)
    assert response.status_code == 200
    assert response.json()["owner"] == "alice"


# API2:2023 Broken Authentication
def test_missing_token_is_rejected(ai_server):
    assert requests.get(f"{BASE}/1", timeout=10).status_code == 401


def test_invalid_token_is_rejected(ai_server):
    response = requests.get(f"{BASE}/1", headers=auth("not-a-real-token"), timeout=10)
    assert response.status_code == 401


# API3:2023 Broken Object Property Level Authorization
@pytest.mark.xfail(strict=True, reason="Mock returns internal fields (owner_email, internal_flags)")
def test_response_does_not_expose_internal_fields(ai_server):
    body = requests.get(f"{BASE}/1", headers=auth("token-alice"), timeout=10).json()
    assert "owner_email" not in body
    assert "internal_flags" not in body


# API4:2023 Unrestricted Resource Consumption
def test_burst_of_requests_is_rate_limited(ai_server):
    statuses = [
        requests.get(f"{BASE}/1", headers=auth("token-carol"), timeout=10).status_code
        for _ in range(30)
    ]
    assert 429 in statuses


# API5:2023 Broken Function Level Authorization
def test_non_admin_cannot_delete_note(ai_server):
    response = requests.delete(f"{BASE}/1", headers=auth("token-bob"), timeout=10)
    assert response.status_code == 403


def test_admin_can_delete_note(ai_server):
    response = requests.delete(f"{BASE}/1", headers=auth("token-admin"), timeout=10)
    assert response.status_code == 204