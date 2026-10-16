import json
import logging
import os
from pathlib import Path

import pytest
import requests

BASE_URL = "https://reqres.in/api"
DATA = json.loads((Path(__file__).parent / "data" / "users.json").read_text())

logger = logging.getLogger("api")


def log_response(response, *args, **kwargs):
    """Log every request/response made through the session."""
    request = response.request
    elapsed_ms = response.elapsed.total_seconds() * 1000
    logger.info(
        "%s %s -> %s in %.0f ms",
        request.method, request.url, response.status_code, elapsed_ms,
    )
    logger.debug("Request body: %s", request.body)
    if response.status_code >= 400:
        logger.warning("Response body: %s", response.text[:500])


@pytest.fixture(scope="session")
def api():
    """A requests Session that sends the API key on every call."""
    key = os.environ.get("REQRES_API_KEY")
    if not key:
        pytest.fail("REQRES_API_KEY is not set. Run: set REQRES_API_KEY=your_key")
    session = requests.Session()
    session.headers.update({"x-api-key": key})
    session.hooks["response"].append(log_response)
    yield session
    session.close()


@pytest.fixture(scope="session")
def auth_token(api):
    """Log in once per test run and return the token."""
    response = api.post(f"{BASE_URL}/login", json=DATA["valid_login"], timeout=10)
    assert response.status_code == 200, f"Login failed: {response.status_code}"
    return response.json()["token"]


@pytest.fixture(scope="session")
def auth_api(api, auth_token):
    """Same session as api, plus a Bearer token on every call."""
    session = requests.Session()
    session.headers.update(api.headers)
    session.headers["Authorization"] = f"Bearer {auth_token}"
    session.hooks["response"].append(log_response)
    yield session
    session.close()