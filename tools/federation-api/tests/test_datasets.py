import logging

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
def test_valid_nodes_do_not_error(
    test_app,
    disable_auth,
    set_valid_test_federation_nodes,
    mocked_single_matching_dataset_result,
    valid_nodes,
    monkeypatch,
    caplog,
):
    """
    Smoke test that when a valid 'nodes' list is provided, POST /datasets does not raise an error and returns a combined response with the correct fields.
    """
    caplog.set_level(logging.INFO)

    async def mock_httpx_request(self, method, url, **kwargs):
        return httpx.Response(
            status_code=200, json=[mocked_single_matching_dataset_result]
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.post(ROUTE, json={"nodes": valid_nodes})

    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["nodes_response_status"] == "success"
    assert response["errors"] == []
    assert len(response["responses"]) == 2
    assert "Requests to all nodes succeeded (2/2)" in caplog.text
    for response in response["responses"]:
        assert "subject_data" not in response


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
        # TODO this test case currently doesn't pass as our implementation doesn't
        # forbid extra body parameters yet. It should be good once
        # https://github.com/neurobagel/federation-api/issues/165 is implemented
        # (
        #     [
        #         {
        #             "node_url": "https://firstpublicnode.org/",
        #             "dataset_uuids": ["http://neurobagel.org/vocab/12345"],
        #         }
        #     ],
        #     "Unrecognized Neurobagel node URL(s)",
        # ),
    ],
)
def test_invalid_nodes_raise_error(
    test_app,
    disable_auth,
    set_valid_test_federation_nodes,
    invalid_nodes,
    expected_error,
    monkeypatch,
):
    """Test that when an invalid 'nodes' list is provided, POST /datasets raises a 422 error with an appropriate message."""
    response = test_app.post(ROUTE, json={"nodes": invalid_nodes})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert expected_error in response.text
