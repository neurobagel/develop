import httpx
import pytest
from fastapi import status


def test_partially_failed_terms_fetching_handled_gracefully(
    test_app,
    monkeypatch,
    set_valid_test_federation_nodes,
):
    """
    When some nodes fail while getting term instances for an attribute (/attribute/{data_element_URI}),
    the overall API get request still succeeds, and the response includes a list of the encountered errors along with the successfully fetched terms.
    """
    mocked_node_attribute_response = {
        "nb:Assessment": [
            {
                "TermURL": "cogatlas:trm_56a9137d9dce1",
                "Label": "behavioral approach/inhibition systems",
            },
            {
                "TermURL": "cogatlas:trm_55a6a8e81b7f4",
                "Label": "Barratt Impulsiveness Scale",
            },
        ]
    }

    async def mock_httpx_get(self, **kwargs):
        # The self parameter is necessary to match the signature of the method being mocked,
        # which is a class method of the httpx.AsyncClient class (see https://www.python-httpx.org/api/#asyncclient).
        if (
            kwargs["url"]
            == "https://secondpublicnode.org/attributes/nb:Assessment"
        ):
            return httpx.Response(
                status_code=500, json={}, text="Some internal server error"
            )
        return httpx.Response(
            status_code=200,
            json=mocked_node_attribute_response,
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

    with pytest.warns(UserWarning):
        response = test_app.get("/attributes/nb:Assessment")

    assert response.status_code == status.HTTP_207_MULTI_STATUS

    response_object = response.json()
    assert response_object["errors"] == [
        {
            "node_name": "Second Public Node",
            "error": "Internal Server Error: Some internal server error",
        }
    ]
    assert response_object["responses"] == mocked_node_attribute_response
    assert response_object["nodes_response_status"] == "partial success"


def test_fully_failed_terms_fetching_handled_gracefully(
    test_app,
    monkeypatch,
    mock_failed_connection_httpx_get,
    set_valid_test_federation_nodes,
):
    """
    When *all* nodes fail while getting term instances for an attribute (/attribute/{data_element_URI}),
    the overall API get request still succeeds, but includes an overall failure status and all encountered errors in the response.
    """
    monkeypatch.setattr(
        httpx.AsyncClient, "get", mock_failed_connection_httpx_get
    )

    with pytest.warns(UserWarning):
        response = test_app.get("/attributes/nb:Assessment")

    assert response.status_code == status.HTTP_207_MULTI_STATUS

    response = response.json()
    assert response["nodes_response_status"] == "fail"
    assert len(response["errors"]) == 2
    assert response["responses"] == {"nb:Assessment": []}
