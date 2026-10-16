import pytest
BASE_URL = "https://reqres.in/api"

@pytest.mark.smoke
def test_login_returns_token(auth_token):
    assert isinstance(auth_token, str)
    assert len(auth_token) > 0


def test_authenticated_request_sends_bearer_header(auth_api):
    response = auth_api.get(f"{BASE_URL}/users/2", timeout=10)
    assert response.status_code == 200
    assert response.request.headers["Authorization"].startswith("Bearer ")