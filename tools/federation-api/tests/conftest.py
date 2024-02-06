import httpx
import pytest
from starlette.testclient import TestClient

from app.api import utility as util
from app.main import app


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="function")
def set_valid_test_federation_nodes(monkeypatch):
    """Set two correctly formatted federation nodes for a test function (mocks the result of reading/parsing available public and local nodes on startup)."""
    monkeypatch.setattr(
        util,
        "FEDERATION_NODES",
        {
            "https://firstpublicnode.org/": "First Public Node",
            "https://secondpublicnode.org/": "Second Public Node",
        },
    )


@pytest.fixture()
def mock_failed_connection_httpx_get():
    """Return a mock for the httpx.AsyncClient.get method that raises a ConnectError when called."""

    async def _mock_httpx_get_with_connect_error(self, **kwargs):
        # The self parameter is necessary to match the signature of the method being mocked,
        # which is a class method of the httpx.AsyncClient class (see https://www.python-httpx.org/api/#asyncclient).
        raise httpx.ConnectError("Some connection error")

    return _mock_httpx_get_with_connect_error
