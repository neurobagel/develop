import json
from urllib.parse import urlparse

import httpx
import pytest
from fastapi import status

ROUTE = "/subjects"


@pytest.fixture()
def mock_token():
    """Create a mock token that is well-formed for testing purposes."""
    return "Bearer foo"


def test_partial_node_failure_responses_handled_gracefully(
    monkeypatch,
    test_app,
    set_valid_test_federation_nodes,
    mocked_subjects_query_response_for_single_dataset,
    mock_token,
    set_mock_verify_token,
    caplog,
):
    """
    Test that when queries to some nodes return unsuccessful responses, the overall API cohort query request still succeeds,
    the successful responses are returned along with a list of the encountered errors, and the failed nodes are logged to the console.
    """

    async def mock_httpx_request(self, method, url, **kwargs):
        # The self parameter is necessary to match the signature of the method being mocked,
        # which is a class method of the httpx.AsyncClient class (see https://www.python-httpx.org/api/#asyncclient).
        if urlparse(url).hostname == "firstpublicnode.org":
            return httpx.Response(
                status_code=200,
                json=[mocked_subjects_query_response_for_single_dataset],
            )

        return httpx.Response(
            status_code=500, json={}, text="Some internal server error"
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.post(
        ROUTE,
        headers={"Authorization": mock_token},
        json={},
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
                **mocked_subjects_query_response_for_single_dataset,
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
    mocked_subjects_query_response_for_single_dataset,
    mock_token,
    set_mock_verify_token,
    error_to_raise,
    expected_node_message,
    caplog,
):
    """
    Test that when requests to some nodes fail (so there is no response status code), the overall API cohort query request still succeeds,
    the successful responses are returned along with a list of the encountered errors, and the failed nodes are logged to the console.
    """

    async def mock_httpx_request(self, method, url, **kwargs):
        if urlparse(url).hostname == "firstpublicnode.org":
            return httpx.Response(
                status_code=200,
                json=[mocked_subjects_query_response_for_single_dataset],
            )

        raise error_to_raise

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.post(
        ROUTE,
        headers={"Authorization": mock_token},
        json={},
    )

    assert response.status_code == status.HTTP_207_MULTI_STATUS

    response = response.json()
    assert response["responses"] == [
        {
            **mocked_subjects_query_response_for_single_dataset,
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
    Test that when queries sent to all nodes fail, the federation API cohort query request still succeeds,
    but includes an overall failure status and all encountered errors in the response.
    """
    monkeypatch.setattr(
        httpx.AsyncClient, "post", mock_failed_connection_httpx_request
    )

    response = test_app.post(
        ROUTE,
        headers={"Authorization": mock_token},
        json={},
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
    mocked_subjects_query_response_for_single_dataset,
    mock_token,
    set_mock_verify_token,
):
    """
    Test that when queries sent to all nodes succeed, the federation API cohort query response includes an overall success status and no errors.
    """

    async def mock_httpx_request(self, method, url, **kwargs):
        return httpx.Response(
            status_code=200,
            json=[mocked_subjects_query_response_for_single_dataset],
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.post(
        ROUTE,
        headers={"Authorization": mock_token},
        json={},
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
    mocked_subjects_query_response_for_single_dataset,
    disable_auth,
):
    """
    Test that when authentication is disabled, a federated query request without a token succeeds.
    """

    async def mock_httpx_request(self, method, url, **kwargs):
        return httpx.Response(
            status_code=200,
            json=[mocked_subjects_query_response_for_single_dataset],
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.post(ROUTE, json={})

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "valid_nodes",
    [
        [
            {
                "node_url": "https://firstpublicnode.org/",
                "dataset_uuids": [
                    "http://neurobagel.org/vocab/12345",
                    "http://neurobagel.org/vocab/67890",
                ],
            },
            {
                "node_url": "https://secondpublicnode.org/",
            },
        ],
        [],
        None,
    ],
)
def test_valid_nodes_query_does_not_error(
    test_app,
    disable_auth,
    set_valid_test_federation_nodes,
    mocked_subjects_query_response_for_single_dataset,
    valid_nodes,
    monkeypatch,
    caplog,
):
    """
    Smoke test that when a valid 'nodes' list is provided, POST /subjects does not raise an error and returns a successful combined response.
    """

    async def mock_httpx_request(self, method, url, **kwargs):
        return httpx.Response(
            status_code=200,
            json=[mocked_subjects_query_response_for_single_dataset],
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.post(ROUTE, json={"nodes": valid_nodes})

    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["nodes_response_status"] == "success"
    assert response["errors"] == []
    assert len(response["responses"]) == 2
    assert "Requests to all nodes succeeded (2/2)" in caplog.text


@pytest.mark.parametrize(
    "valid_nodes",
    [
        [
            {
                "node_url": "https://firstpublicnode.org/",
                "dataset_uuids": [
                    "http://neurobagel.org/vocab/12345",
                    "http://neurobagel.org/vocab/67890",
                ],
            },
            {
                "node_url": "https://secondpublicnode.org/",
            },
        ],
        [],
        None,
    ],
)
def test_valid_nodes_query_returns_subject_data_only(
    test_app,
    disable_auth,
    set_valid_test_federation_nodes,
    mocked_subjects_query_response_for_single_dataset,
    valid_nodes,
    monkeypatch,
):
    """
    Test that when a valid 'nodes' list is provided, the POST /subjects response includes only subject data,
    without dataset-level metadata fields.
    """

    async def mock_httpx_request(self, method, url, **kwargs):
        return httpx.Response(
            status_code=200,
            json=[mocked_subjects_query_response_for_single_dataset],
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.post(ROUTE, json={"nodes": valid_nodes})

    response = response.json()
    for response in response["responses"]:
        assert "subject_data" in response
        assert "dataset_name" not in response
        assert "num_matching_subjects" not in response


@pytest.mark.parametrize(
    "invalid_nodes,expected_error",
    [
        (
            [
                {
                    "node_url": "https://firstpublicnode.org/",
                    "dataset_uuids": [
                        "http://neurobagel.org/vocab/12345",
                        "http://neurobagel.org/vocab/67890",
                    ],
                },
                {
                    "node_url": "https://firstpublicnode.org/",
                    "dataset_uuids": ["http://neurobagel.org/vocab/34567"],
                },
            ],
            "Duplicate node URL found",
        ),
        (
            [
                {
                    "node_url": "",
                    "dataset_uuids": ["http://neurobagel.org/vocab/12345"],
                },
            ],
            "Unrecognized Neurobagel node URL(s)",
        ),
        (
            [
                {
                    "dataset_uuids": ["http://neurobagel.org/vocab/12345"],
                },
            ],
            "Field required",
        ),
    ],
)
def test_invalid_nodes_query_raises_error(
    test_app,
    disable_auth,
    set_valid_test_federation_nodes,
    invalid_nodes,
    expected_error,
):
    """Test that when an invalid 'nodes' list is provided, POST /subjects raises a 422 error with an appropriate message."""
    response = test_app.post(ROUTE, json={"nodes": invalid_nodes})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert expected_error in response.text


def test_extra_query_fields_raise_error(
    test_app,
    disable_auth,
    set_valid_test_federation_nodes,
):
    """Test that when extra fields are provided in the query, POST /subjects raises a 422 error with an appropriate message."""
    response = test_app.post(
        ROUTE,
        json={
            "nodes": [
                {
                    "node_url": "https://firstpublicnode.org/",
                }
            ],
            "invalid_extra_field": "unexpected_value",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert all(
        msg in response.text for msg in ["invalid_extra_field", "Extra inputs"]
    )
