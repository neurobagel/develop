import httpx
import pytest
from starlette.testclient import TestClient

from app.api import utility as util
from app.main import app


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client


@pytest.fixture()
def enable_auth(monkeypatch):
    """Enable the authentication requirement for the API."""
    monkeypatch.setattr("app.api.security.AUTH_ENABLED", True)


@pytest.fixture()
def disable_auth(monkeypatch):
    """
    Disable the authentication requirement for the API to skip startup checks
    (for when the tested route does not require authentication).
    """
    monkeypatch.setattr("app.api.security.AUTH_ENABLED", False)


@pytest.fixture()
def mock_verify_and_extract_token():
    """Mock a successful token verification that does not raise any exceptions."""

    def _verify_and_extract_token(token):
        return None

    return _verify_and_extract_token


@pytest.fixture()
def set_mock_verify_and_extract_token(
    monkeypatch, mock_verify_and_extract_token
):
    """Set the verify_token function to a mock that does not raise any exceptions."""
    monkeypatch.setattr(
        "app.api.routers.query.verify_and_extract_token",
        mock_verify_and_extract_token,
    )


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


@pytest.fixture()
def mocked_single_matching_dataset_result():
    """Valid aggregate query result for a single matching dataset."""
    return {
        "dataset_uuid": "http://neurobagel.org/vocab/12345",
        "dataset_name": "QPN",
        "dataset_portal_uri": "https://rpq-qpn.ca/en/researchers-section/databases/",
        "dataset_total_subjects": 200,
        "num_matching_subjects": 5,
        "records_protected": True,
        "subject_data": "protected",
        "image_modals": [
            "http://purl.org/nidash/nidm#T1Weighted",
            "http://purl.org/nidash/nidm#T2Weighted",
        ],
        "available_pipelines": {
            "https://github.com/nipoppy/pipeline-catalog/tree/main/processing/fmriprep": [
                "23.1.3"
            ],
            "https://github.com/nipoppy/pipeline-catalog/tree/main/processing/freesurfer": [
                "7.3.2"
            ],
        },
    }
