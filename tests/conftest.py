import logging
import os

import pytest
import requests

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