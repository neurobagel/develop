from urllib.parse import urlparse

import httpx
import pytest
from fastapi import status

from app.api import crud


@pytest.mark.parametrize(
    "attributes_path,attribute_uri,node1_response,node2_response,expected_unique_terms",
    [
        (
            "/assessments",
            "nb:Assessment",
            {
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
            },
            {
                "nb:Assessment": [
                    {
                        "TermURL": "cogatlas:trm001",
                        "Label": "Alternate Label 1",
                    },
                ]
            },
            ["cogatlas:trm001", "cogatlas:trm002"],
        ),
        (
            "/imaging-modalities",
            "nb:Image",
            {
                "nb:Image": [
                    {
                        "TermURL": "nidm:T1Weighted",
                        "Label": "T1 Weighted",
                        "Abbreviation": "T1w",
                        "DataType": "anat",
                    },
                ]
            },
            {
                "nb:Image": [
                    {
                        "TermURL": "nidm:T1Weighted",
                        "Label": "T1 Weighted",
                        "Abbreviation": "T1w",
                        "DataType": "anat",
                    },
                    {
                        "TermURL": "nidm:FlowWeighted",
                        "Label": "Blood-Oxygen-Level Dependent image",
                        "Abbreviation": "bold",
                        "DataType": "func",
                    },
                ]
            },
            ["nidm:T1Weighted", "nidm:FlowWeighted"],
        ),
    ],
)
def test_get_instances_with_duplicate_terms_handled(
    test_app,
    monkeypatch,
    set_valid_test_federation_nodes,
    attributes_path,
    attribute_uri,
    node1_response,
    node2_response,
    expected_unique_terms,
):
    """
    When multiple nodes return a term with the same URI,
    the API should return only one instance of that term in the final federated response.
    """

    async def mock_httpx_request(self, method, url, **kwargs):
        # The self parameter is necessary to match the signature of the method being mocked,
        # which is a class method of the httpx.AsyncClient class (see https://www.python-httpx.org/api/#asyncclient).
        if urlparse(url).hostname == "firstpublicnode.org":
            mocked_node_instances_response = node1_response
        else:
            mocked_node_instances_response = node2_response
        return httpx.Response(
            status_code=200,
            json=mocked_node_instances_response,
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.get(attributes_path)
    response_object = response.json()
    instances = response_object["responses"][attribute_uri]
    # In this test we only check the unique TermURLs of the returned instances
    # because it is possible for labels to vary between nodes
    instance_term_uris = [instance["TermURL"] for instance in instances]

    assert response.status_code == status.HTTP_200_OK
    assert len(response_object["errors"]) == 0
    assert response_object["nodes_response_status"] == "success"
    assert len(instances) == len(expected_unique_terms)
    assert set(instance_term_uris) == set(expected_unique_terms)


def test_partially_failed_get_instances_handled_gracefully(
    test_app, monkeypatch, set_valid_test_federation_nodes, caplog
):
    """
    When some nodes fail while getting term instances for an attribute (/assessments),
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

    async def mock_httpx_request(self, method, url, **kwargs):
        if urlparse(url).hostname == "secondpublicnode.org":
            return httpx.Response(
                status_code=500, json={}, text="Some internal server error"
            )
        return httpx.Response(
            status_code=200,
            json=mocked_node_get_assessments_response,
        )

    monkeypatch.setattr(httpx.AsyncClient, "request", mock_httpx_request)

    response = test_app.get("/assessments")

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
    mock_failed_connection_httpx_request,
    set_valid_test_federation_nodes,
    caplog,
):
    """
    When *all* nodes fail while getting term instances for an attribute (/assessments),
    the overall API get request still succeeds, but includes an overall failure status and all encountered errors in the response.
    """
    monkeypatch.setattr(
        httpx.AsyncClient, "get", mock_failed_connection_httpx_request
    )

    response = test_app.get("/assessments")

    assert response.status_code == status.HTTP_207_MULTI_STATUS
    # We expect several warnings from logging
    assert len(caplog.records) > 0
    any(record.levelname == "WARNING" for record in caplog.records)

    response = response.json()
    assert response["nodes_response_status"] == "fail"
    assert len(response["errors"]) == 2
    assert response["responses"] == {"nb:Assessment": []}


@pytest.mark.parametrize(
    "path",
    [
        "assessments",
        "diagnoses",
        "imaging-modalities",
        "pipelines",
        "query",
        "subjects",
        "datasets",
    ],
)
def test_node_request_urls_do_not_have_trailing_slash(path):
    """
    Ensure that URLs used to forward requests to node APIs do not include a trailing slash.
    """
    # TODO: Revisit once root_path is tested in production -
    # the example node URLs below assume that validate_query_node_url_list has already been called,
    # which will have appended trailing slashes to the node URLs if they were missing
    node_request_urls = crud.build_node_request_urls(
        node_urls=[
            "https://api.node1.institute.org/",
            "https://node2.institute.org/api/",
        ],
        path=path,
    )
    assert node_request_urls == [
        f"https://api.node1.institute.org/{path}",
        f"https://node2.institute.org/api/{path}",
    ]
