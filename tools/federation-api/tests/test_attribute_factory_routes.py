import httpx
from fastapi import status


def test_get_instances_with_duplicate_terms_handled(
    test_app, monkeypatch, set_valid_test_federation_nodes
):
    """
    When multiple nodes return an assessment with the same URI for a request to /assessments/,
    the API should return only one instance of that assessment term in the final federated response.
    """

    async def mock_httpx_get(self, **kwargs):
        # The self parameter is necessary to match the signature of the method being mocked,
        # which is a class method of the httpx.AsyncClient class (see https://www.python-httpx.org/api/#asyncclient).
        if "https://firstpublicnode.org/" in kwargs["url"]:
            mocked_node_get_assessments_response = {
                "nb:Assessment": [
                    {
                        "TermURL": "cogatlas:trm001",
                        "Label": "Label 1",
                    },
                    {
                        "TermURL": "cogatlas:trm002",
                        "Label": "Label 2",
                    },
                ]
            }
        else:
            mocked_node_get_assessments_response = {
                "nb:Assessment": [
                    {
                        "TermURL": "cogatlas:trm001",
                        "Label": "Alternate Label 1",
                    },
                ]
            }
        return httpx.Response(
            status_code=200,
            json=mocked_node_get_assessments_response,
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

    response = test_app.get("/assessments/")

    response_object = response.json()
    found_instances = response_object["responses"]["nb:Assessment"]
    found_instance_term_uris = [
        instance["TermURL"]
        for instance in response_object["responses"]["nb:Assessment"]
    ]
    expected_term_uris = ["cogatlas:trm001", "cogatlas:trm002"]

    assert response.status_code == status.HTTP_200_OK
    assert len(response_object["errors"]) == 0
    assert response_object["nodes_response_status"] == "success"
    assert len(found_instances) == 2
    assert all(
        expected_term_uri in found_instance_term_uris
        for expected_term_uri in expected_term_uris
    )


def test_partially_failed_get_instances_handled_gracefully(
    test_app, monkeypatch, set_valid_test_federation_nodes, caplog
):
    """
    When some nodes fail while getting term instances for an attribute (/assessments/),
    the overall API get request still succeeds, and the response includes a list of the encountered errors along with the successfully fetched terms.
    """
    mocked_node_get_assessments_response = {
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
        if "https://secondpublicnode.org/" in kwargs["url"]:
            return httpx.Response(
                status_code=500, json={}, text="Some internal server error"
            )
        return httpx.Response(
            status_code=200,
            json=mocked_node_get_assessments_response,
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_httpx_get)

    response = test_app.get("/assessments/")

    assert response.status_code == status.HTTP_207_MULTI_STATUS

    assert len(caplog.records) > 0
    any(record.levelname == "WARNING" for record in caplog.records)

    response_object = response.json()
    assert response_object["errors"] == [
        {
            "node_name": "Second Public Node",
            "error": "Internal Server Error: Some internal server error",
        }
    ]
    assert response_object["responses"] == mocked_node_get_assessments_response
    assert response_object["nodes_response_status"] == "partial success"


def test_fully_failed_get_instances_handled_gracefully(
    test_app,
    monkeypatch,
    mock_failed_connection_httpx_get,
    set_valid_test_federation_nodes,
    caplog,
):
    """
    When *all* nodes fail while getting term instances for an attribute (/assessments/),
    the overall API get request still succeeds, but includes an overall failure status and all encountered errors in the response.
    """
    monkeypatch.setattr(
        httpx.AsyncClient, "get", mock_failed_connection_httpx_get
    )

    response = test_app.get("/assessments/")

    assert response.status_code == status.HTTP_207_MULTI_STATUS
    # We expect several warnings from logging
    assert len(caplog.records) > 0
    any(record.levelname == "WARNING" for record in caplog.records)

    response = response.json()
    assert response["nodes_response_status"] == "fail"
    assert len(response["errors"]) == 2
    assert response["responses"] == {"nb:Assessment": []}
