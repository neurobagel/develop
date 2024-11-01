import json
import logging

import httpx
import pytest
from fastapi import status
from fastapi.exceptions import HTTPException

from app.api.models import QueryModel


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
    set_mock_verify_and_extract_token,
    caplog,
):
    """
    Test that when queries to some nodes return unsuccessful responses, the overall API get request still succeeds,
    the successful responses are returned along with a list of the encountered errors, and the failed nodes are logged to the console.
    """

    async def mock_httpx_get(self, **kwargs):
        # The self parameter is necessary to match the signature of the method being mocked,
        # which is a class method of the httpx.AsyncClient class (see https://www.python-httpx.org/api/#asyncclient).
        if kwargs["url"] == "https://firstpublicnode.org/query":
            return httpx.Response(
                status_code=200, json=[mocked_single_matching_dataset_result]
            )

        return httpx.Response(
            status_code=500, json={}, text="Some internal server error"
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

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
    set_mock_verify_and_extract_token,
    error_to_raise,
    expected_node_message,
    caplog,
):
    """
    Test that when requests to some nodes fail (so there is no response status code), the overall API get request still succeeds,
    the successful responses are returned along with a list of the encountered errors, and the failed nodes are logged to the console.
    """

    async def mock_httpx_get(self, **kwargs):
        if kwargs["url"] == "https://firstpublicnode.org/query":
            return httpx.Response(
                status_code=200, json=[mocked_single_matching_dataset_result]
            )

        raise error_to_raise

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

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
    mock_failed_connection_httpx_get,
    mock_token,
    set_mock_verify_and_extract_token,
    set_valid_test_federation_nodes,
    caplog,
):
    """
    Test that when queries sent to all nodes fail, the federation API get request still succeeds,
    but includes an overall failure status and all encountered errors in the response.
    """
    monkeypatch.setattr(
        httpx.AsyncClient, "get", mock_failed_connection_httpx_get
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
    set_mock_verify_and_extract_token,
):
    """
    Test that when queries sent to all nodes succeed, the federation API response includes an overall success status and no errors.
    """
    # Need to set the logging level to INFO so that the success message is captured
    # pytest by default captures WARNING or above: https://docs.pytest.org/en/stable/how-to/logging.html#caplog-fixture
    caplog.set_level(logging.INFO)

    async def mock_httpx_get(self, **kwargs):
        return httpx.Response(
            status_code=200, json=[mocked_single_matching_dataset_result]
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

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

    async def mock_httpx_get(self, **kwargs):
        return httpx.Response(
            status_code=200, json=[mocked_single_matching_dataset_result]
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

    response = test_app.get("/query")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize("valid_iscontrol", ["true", "True", "TRUE"])
def test_valid_iscontrol_values_unchanged(valid_iscontrol):
    """Test that valid values for the 'is_control' field are accepted without modification or errors."""
    example_fquery = QueryModel(is_control=valid_iscontrol)
    assert example_fquery.is_control == valid_iscontrol


@pytest.mark.parametrize("invalid_iscontrol", ["false", 52])
def test_invalid_iscontrol_value_raises_error(invalid_iscontrol):
    """Test that invalid values for the 'is_control' field fail model validation and raise an informative HTTPException."""
    with pytest.raises(HTTPException) as exc:
        QueryModel(is_control=invalid_iscontrol)

    assert "'is_control' must be either set to 'true' or omitted" in str(
        exc.value
    )
