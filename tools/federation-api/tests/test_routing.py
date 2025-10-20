import httpx
import pytest
from fastapi import status

from app.main import app


@pytest.mark.parametrize(
    "route",
    ["/", ""],
)
def test_root(test_app, set_valid_test_federation_nodes, route, monkeypatch):
    """Given a GET request to the root endpoint, Check for 200 status and expected content."""

    monkeypatch.setattr(app, "root_path", "")
    response = test_app.get(route, follow_redirects=False)

    assert response.status_code == status.HTTP_200_OK
    assert all(
        substring in response.text
        for substring in [
            "<h1>Welcome to the Neurobagel Federation API!</h1>",
            '<a href="/docs">API documentation</a>',
        ]
    )


@pytest.mark.parametrize(
    "valid_route",
    ["/query", "/query?min_age=20", "/nodes"],
)
def test_request_without_trailing_slash_not_redirected(
    test_app,
    monkeypatch,
    set_valid_test_federation_nodes,
    mocked_single_matching_dataset_result,
    disable_auth,
    valid_route,
):
    """Test that a request to a route without a / is not redirected to have a trailing slash."""

    async def mock_httpx_request(self, method, url, **kwargs):
        return httpx.Response(
            status_code=200, json=[mocked_single_matching_dataset_result]
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.get(valid_route, follow_redirects=False)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "invalid_route",
    [
        "/query/",
        "/query/?min_age=20",
        "/nodes/",
        "/attributes/",
        "/assessments/",
    ],
)
def test_request_including_trailing_slash_fails(
    test_app, disable_auth, invalid_route
):
    """
    Test that a request to routes including a trailing slash, where none is expected,
    is *not* redirected to exclude the slash, and returns a 404.
    """
    response = test_app.get(invalid_route)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "test_route,expected_status_code",
    [("", 200), ("/fapi/v1", 200), ("/wrongroot", 404)],
)
def test_docs_work_using_defined_root_path(
    test_app, test_route, expected_status_code, monkeypatch
):
    """
    Test that when the API root_path is set to a non-empty string,
    the interactive docs and OpenAPI schema are only reachable with the correct path prefix
    (e.g., mimicking access through a proxy) or without the prefix entirely (e.g., mimicking local access or by a proxy itself).

    Note: We test the OpenAPI schema as well because when the root path is not set correctly,
    the docs break from failure to fetch openapi.json.
    (https://fastapi.tiangolo.com/advanced/behind-a-proxy/#proxy-with-a-stripped-path-prefix)
    """

    monkeypatch.setattr(app, "root_path", "/fapi/v1")
    docs_response = test_app.get(f"{test_route}/docs", follow_redirects=False)
    schema_response = test_app.get(
        f"{test_route}/openapi.json", follow_redirects=False
    )
    assert docs_response.status_code == expected_status_code
    assert schema_response.status_code == expected_status_code


@pytest.mark.parametrize(
    "test_route,expected_status_code",
    [("", 200), ("/fapi/", 200), ("/fapi", 404)],
)
def test_docs_when_root_path_includes_trailing_slash(
    test_app, test_route, expected_status_code, monkeypatch
):
    """
    Test that when the API root_path is set with a trailing slash, the interactive docs and OpenAPI schema are only reachable
    using a path prefix with the extra trailing slash also included, or without the prefix entirely.

    This provides a sanity check that the app does not ignore/redirect trailing slashes in the root_path when requests are received.
    """

    monkeypatch.setattr(app, "root_path", "/fapi/")
    docs_response = test_app.get(f"{test_route}/docs", follow_redirects=False)
    schema_response = test_app.get(
        f"{test_route}/openapi.json", follow_redirects=False
    )
    assert docs_response.status_code == expected_status_code
    assert schema_response.status_code == expected_status_code
