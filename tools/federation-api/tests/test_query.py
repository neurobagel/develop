import httpx
import pytest
from fastapi import status

from app.api import utility as util


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
    }


def test_partial_node_failure_responses_handled_gracefully(
    monkeypatch, test_app, capsys, mocked_single_matching_dataset_result
):
    """
    Test that when queries to some nodes return errors, the overall API get request still succeeds,
    the successful responses are returned along with a list of the encountered errors, and the failed nodes are logged to the console.
    """
    monkeypatch.setattr(
        util,
        "FEDERATION_NODES",
        {
            "https://firstpublicnode.org/": "First Public Node",
            "https://secondpublicnode.org/": "Second Public Node",
        },
    )

    async def mock_httpx_get(self, **kwargs):
        if kwargs["url"] == "https://firstpublicnode.org/query/":
            return httpx.Response(
                status_code=200, json=[mocked_single_matching_dataset_result]
            )

        return httpx.Response(
            status_code=500, json={}, text="Some internal server error"
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

    with pytest.warns(
        UserWarning,
        match=r"Second Public Node \(https://secondpublicnode.org/\) did not succeed",
    ):
        response = test_app.get("/query/")
        captured = capsys.readouterr()

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
        "Queries to 1/2 nodes failed: ['Second Public Node']" in captured.out
    )


def test_partial_node_connection_failures_handled_gracefully(
    monkeypatch, test_app, capsys, mocked_single_matching_dataset_result
):
    """
    Test that when requests to some nodes fail (e.g., if API is unreachable), the overall API get request still succeeds,
    the successful responses are returned along with a list of the encountered errors, and the failed nodes are logged to the console.
    """
    monkeypatch.setattr(
        util,
        "FEDERATION_NODES",
        {
            "https://firstpublicnode.org/": "First Public Node",
            "https://secondpublicnode.org/": "Second Public Node",
        },
    )

    async def mock_httpx_get(self, **kwargs):
        if kwargs["url"] == "https://firstpublicnode.org/query/":
            return httpx.Response(
                status_code=200, json=[mocked_single_matching_dataset_result]
            )

        raise httpx.ConnectError("Some connection error")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

    with pytest.warns(
        UserWarning,
        match=r"Second Public Node \(https://secondpublicnode.org/\) did not succeed",
    ):
        response = test_app.get("/query/")
        captured = capsys.readouterr()

    assert response.status_code == status.HTTP_207_MULTI_STATUS
    assert response.json() == {
        "errors": [
            {
                "node_name": "Second Public Node",
                "error": "Request failed due to a network error or because the node API cannot be reached: Some connection error",
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
        "Queries to 1/2 nodes failed: ['Second Public Node']" in captured.out
    )


def test_all_nodes_failure_handled_gracefully(monkeypatch, test_app, capsys):
    """
    Test that when queries sent to all nodes fail, the federation API get request still succeeds,
    but includes an overall failure status and all encountered errors in the response.
    """
    monkeypatch.setattr(
        util,
        "FEDERATION_NODES",
        {
            "https://firstpublicnode.org/": "First Public Node",
            "https://secondpublicnode.org/": "Second Public Node",
        },
    )

    async def mock_httpx_get(self, **kwargs):
        raise httpx.ConnectError("Some connection error")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

    with pytest.warns(
        UserWarning,
    ) as w:
        response = test_app.get("/query/")
        captured = capsys.readouterr()

    assert len(w) == 2
    assert response.status_code == status.HTTP_207_MULTI_STATUS

    response = response.json()
    assert response["nodes_response_status"] == "fail"
    assert len(response["errors"]) == 2
    assert response["responses"] == []
    assert (
        "Queries to 2/2 nodes failed: ['First Public Node', 'Second Public Node']"
        in captured.out
    )


def test_all_nodes_success_handled_gracefully(
    monkeypatch, test_app, capsys, mocked_single_matching_dataset_result
):
    """
    Test that when queries sent to all nodes succeed, the federation API response includes an overall success status and no errors.
    """
    monkeypatch.setattr(
        util,
        "FEDERATION_NODES",
        {
            "https://firstpublicnode.org/": "First Public Node",
            "https://secondpublicnode.org/": "Second Public Node",
        },
    )

    async def mock_httpx_get(self, **kwargs):
        return httpx.Response(
            status_code=200, json=[mocked_single_matching_dataset_result]
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

    response = test_app.get("/query/")
    captured = capsys.readouterr()

    assert response.status_code == status.HTTP_200_OK

    response = response.json()
    assert response["nodes_response_status"] == "success"
    assert response["errors"] == []
    assert len(response["responses"]) == 2
    assert "All nodes queried successfully (2/2)" in captured.out
