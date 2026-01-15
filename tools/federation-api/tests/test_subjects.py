import httpx
import pytest
from fastapi import status

ROUTE = "/subjects"


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
