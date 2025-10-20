from urllib.parse import urlparse

import httpx
from fastapi import status


def test_unique_pipeline_versions_returned_from_nodes(
    test_app, monkeypatch, set_valid_test_federation_nodes
):
    """
    Test that given a successful request to two nodes for versions of a specific pipeline term,
    the API correctly returns a list of unique versions across both nodes.
    """

    # Predefine the responses from the mocked n-APIs set using the fixture set_valid_test_federation_nodes
    async def mock_httpx_request(self, method, url, **kwargs):
        if urlparse(url).hostname == "firstpublicnode.org":
            mocked_response_json = {"np:pipeline1": ["1.0.0", "1.0.1"]}
        else:
            mocked_response_json = {"np:pipeline1": ["1.0.1", "1.0.2"]}
        return httpx.Response(
            status_code=200,
            json=mocked_response_json,
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.get("/pipelines/np:pipeline1/versions")
    assert response.status_code == status.HTTP_200_OK

    response_object = response.json()
    assert len(response_object["errors"]) == 0
    assert response_object["responses"] == {
        "np:pipeline1": ["1.0.0", "1.0.1", "1.0.2"]
    }
    assert response_object["nodes_response_status"] == "success"
