import os

import pytest
import requests


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