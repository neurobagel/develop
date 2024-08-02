import httpx
import pytest
from fastapi import status


@pytest.mark.parametrize(
    "root_path",
    ["/", ""],
)
def test_root(test_app, set_valid_test_federation_nodes, root_path):
    """Given a GET request to the root endpoint, Check for 200 status and expected content."""

    response = test_app.get(root_path, follow_redirects=False)

    assert response.status_code == status.HTTP_200_OK
    assert all(
        substring in response.text
        for substring in [
            "Welcome to",
            "Neurobagel",
            '<a href="/docs">documentation</a>',
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

    async def mock_httpx_get(self, **kwargs):
        return httpx.Response(
            status_code=200, json=[mocked_single_matching_dataset_result]
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

    response = test_app.get(valid_route, follow_redirects=False)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "invalid_route",
    ["/query/", "/query/?min_age=20", "/nodes/", "/attributes/nb:SomeClass/"],
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
