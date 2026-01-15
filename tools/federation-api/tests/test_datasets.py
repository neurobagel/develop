import httpx
import pytest
from fastapi import status

ROUTE = "/datasets"


@pytest.mark.parametrize(
    "valid_nodes",
    [
        [
            {"node_url": "https://firstpublicnode.org/"},
            {"node_url": "https://secondpublicnode.org/"},
        ],
        [],
        None,
    ],
)
def test_valid_nodes_query_does_not_error(
    test_app,
    disable_auth,
    set_valid_test_federation_nodes,
    mocked_datasets_query_response_for_single_dataset,
    valid_nodes,
    monkeypatch,
    caplog,
):
    """
    Smoke test that when a valid 'nodes' list is provided, POST /datasets does not raise an error and returns a successful combined response.
    """

    async def mock_httpx_request(self, method, url, **kwargs):
        return httpx.Response(
            status_code=200,
            json=[mocked_datasets_query_response_for_single_dataset],
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
            {"node_url": "https://firstpublicnode.org/"},
            {"node_url": "https://secondpublicnode.org/"},
        ],
        [],
        None,
    ],
)
def test_valid_nodes_query_returns_only_dataset_metadata(
    test_app,
    disable_auth,
    set_valid_test_federation_nodes,
    mocked_datasets_query_response_for_single_dataset,
    valid_nodes,
    monkeypatch,
):
    """
    Test that when a valid 'nodes' list is provided, the POST /datasets response includes expected
    dataset-level metadata fields and no subject data.
    """

    async def mock_httpx_request(self, method, url, **kwargs):
        return httpx.Response(
            status_code=200,
            json=[mocked_datasets_query_response_for_single_dataset],
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.post(ROUTE, json={"nodes": valid_nodes})

    response = response.json()
    for response in response["responses"]:
        assert "subject_data" not in response
        assert "dataset_name" in response
        assert "access_type" in response


@pytest.mark.parametrize(
    "invalid_nodes,expected_error",
    [
        (
            [
                {"node_url": "https://firstpublicnode.org/"},
                {"node_url": "https://firstpublicnode.org/"},
            ],
            "Duplicate node URL found",
        ),
        (
            [{"node_url": ""}],
            "Unrecognized Neurobagel node URL(s)",
        ),
        (
            [
                {
                    "node_url": "https://firstpublicnode.org/",
                    "dataset_uuids": [
                        "http://neurobagel.org/vocab/12345"
                    ],  # Unexpected field
                }
            ],
            "Extra inputs",
        ),
    ],
)
def test_invalid_nodes_query_raises_error(
    test_app,
    disable_auth,
    set_valid_test_federation_nodes,
    invalid_nodes,
    expected_error,
    monkeypatch,
):
    """Test that when an invalid 'nodes' list is provided, POST /datasets raises a 422 error with an appropriate message."""
    response = test_app.post(ROUTE, json={"nodes": invalid_nodes})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert expected_error in response.text
