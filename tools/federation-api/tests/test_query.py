import json

import httpx
import pytest
from fastapi import status


@pytest.fixture()
def mock_token():
    """Create a mock token that is well-formed for testing purposes."""
    return "Bearer foo"


def test_partial_node_failure_responses_handled_gracefully(
    monkeypatch,
    test_app,
    set_valid_test_federation_nodes,
    mocked_single_matching_dataset_result,
    mock_token,
    set_mock_verify_token,
    caplog,
):
    """
    Test that when queries to some nodes return unsuccessful responses, the overall API get request still succeeds,
    the successful responses are returned along with a list of the encountered errors, and the failed nodes are logged to the console.
    """

    async def mock_httpx_request(self, method, url, **kwargs):
        # The self parameter is necessary to match the signature of the method being mocked,
        # which is a class method of the httpx.AsyncClient class (see https://www.python-httpx.org/api/#asyncclient).
        if url == "https://firstpublicnode.org/query":
            return httpx.Response(
                status_code=200, json=[mocked_single_matching_dataset_result]
            )

        return httpx.Response(
            status_code=500, json={}, text="Some internal server error"
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.get(
        "/query",
        headers={"Authorization": mock_token},
    )

    assert response.status_code == status.HTTP_207_MULTI_STATUS
    assert response.json() == {
        "errors": [
            {
                "node_name": "Second Public Node",
                "error": "Internal Server Error: Some internal server error",
            },
        ],
        "responses": [
            {
                **mocked_single_matching_dataset_result,
                "node_name": "First Public Node",
            },
        ],
        "nodes_response_status": "partial success",
    }
    assert (
        "Second Public Node (https://secondpublicnode.org/) did not succeed"
        in caplog.text
    )
    assert (
        "Requests to 1/2 nodes failed: ['Second Public Node']" in caplog.text
    )


@pytest.mark.parametrize(
    "error_to_raise,expected_node_message",
    [
        (
            httpx.ConnectError("Some connection error"),
            "Request failed due to a network error or because the node API could not be reached",
        ),
        (
            httpx.ConnectTimeout("Some timeout error"),
            "Request failed due to a timeout",
        ),
        (
            httpx.UnsupportedProtocol("Some protocol error"),
            "Request failed due to an error",
        ),
        # JSONDecodeError has some extra required parameters: https://docs.python.org/3/library/json.html#json.JSONDecodeError
        (
            json.JSONDecodeError("Some JSON decoding error", "", 0),
            "An unexpected error was encountered",
        ),
    ],
)
def test_partial_node_request_failures_handled_gracefully(
    monkeypatch,
    test_app,
    set_valid_test_federation_nodes,
    mocked_single_matching_dataset_result,
    mock_token,
    set_mock_verify_token,
    error_to_raise,
    expected_node_message,
    caplog,
):
    """
    Test that when requests to some nodes fail (so there is no response status code), the overall API get request still succeeds,
    the successful responses are returned along with a list of the encountered errors, and the failed nodes are logged to the console.
    """

    async def mock_httpx_request(self, method, url, **kwargs):
        if url == "https://firstpublicnode.org/query":
            return httpx.Response(
                status_code=200, json=[mocked_single_matching_dataset_result]
            )

        raise error_to_raise

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.get(
        "/query",
        headers={"Authorization": mock_token},
    )

    assert response.status_code == status.HTTP_207_MULTI_STATUS

    response = response.json()
    assert response["responses"] == [
        {
            **mocked_single_matching_dataset_result,
            "node_name": "First Public Node",
        },
    ]
    assert response["nodes_response_status"] == "partial success"

    node_errors = response["errors"]
    assert len(node_errors) == 1
    assert node_errors[0]["node_name"] == "Second Public Node"
    assert expected_node_message in node_errors[0]["error"]
    assert (
        "Second Public Node (https://secondpublicnode.org/) did not succeed"
        in caplog.text
    )
    assert (
        "Requests to 1/2 nodes failed: ['Second Public Node']" in caplog.text
    )


def test_all_nodes_failure_handled_gracefully(
    monkeypatch,
    test_app,
    mock_failed_connection_httpx_request,
    mock_token,
    set_mock_verify_token,
    set_valid_test_federation_nodes,
    caplog,
):
    """
    Test that when queries sent to all nodes fail, the federation API get request still succeeds,
    but includes an overall failure status and all encountered errors in the response.
    """
    monkeypatch.setattr(
        httpx.AsyncClient, "get", mock_failed_connection_httpx_request
    )

    response = test_app.get(
        "/query",
        headers={"Authorization": mock_token},
    )

    # We expect 3 logs here: one warning for each failed node, and one error for the overall failure
    assert len(caplog.records) == 3
    assert response.status_code == status.HTTP_207_MULTI_STATUS

    response = response.json()
    assert response["nodes_response_status"] == "fail"
    assert len(response["errors"]) == 2
    assert response["responses"] == []
    assert (
        "Requests to 2/2 nodes failed: ['First Public Node', 'Second Public Node']"
        in caplog.text
    )


def test_all_nodes_success_handled_gracefully(
    monkeypatch,
    test_app,
    caplog,
    set_valid_test_federation_nodes,
    mocked_single_matching_dataset_result,
    mock_token,
    set_mock_verify_token,
):
    """
    Test that when queries sent to all nodes succeed, the federation API response includes an overall success status and no errors.
    """

    async def mock_httpx_request(self, method, url, **kwargs):
        return httpx.Response(
            status_code=200, json=[mocked_single_matching_dataset_result]
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.get(
        "/query",
        headers={"Authorization": mock_token},
    )

    assert response.status_code == status.HTTP_200_OK

    response = response.json()
    assert response["nodes_response_status"] == "success"
    assert response["errors"] == []
    assert len(response["responses"]) == 2
    assert "Requests to all nodes succeeded (2/2)" in caplog.text


def test_query_without_token_succeeds_when_auth_disabled(
    monkeypatch,
    test_app,
    set_valid_test_federation_nodes,
    mocked_single_matching_dataset_result,
    disable_auth,
):
    """
    Test that when authentication is disabled, a federated query request without a token succeeds.
    """

    async def mock_httpx_request(self, method, url, **kwargs):
        return httpx.Response(
            status_code=200, json=[mocked_single_matching_dataset_result]
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.get("/query")

    assert response.status_code == status.HTTP_200_OK
