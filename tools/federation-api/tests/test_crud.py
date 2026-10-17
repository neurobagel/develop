import pytest

from app.api import crud, models
from app.api import utility as util


@pytest.mark.parametrize(
    "response_cls,responses_from_nodes,expected_combined_results_payload",
    [
        (
            models.SubjectsQueryResponse,
            [
                [  # from Up-to-date Node
                    {
                        "dataset_uuid": "http://neurobagel.org/vocab/12345",
                        "subject_data": "protected",
                    },
                ],
                [  # from Outdated Node
                    {
                        "dataset_uuid": "http://neurobagel.org/vocab/67890",
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
                        "available_pipelines": {
                            "https://github.com/nipoppy/pipeline-catalog/tree/main/processing/fmriprep": [
                                "23.1.3"
                            ],
                            "https://github.com/nipoppy/pipeline-catalog/tree/main/processing/freesurfer": [
                                "7.3.2"
                            ],
                        },
                    }
                ],
            ],
            [
                {
                    "node_name": "Up-to-date Node",
                    "dataset_uuid": "http://neurobagel.org/vocab/12345",
                    "subject_data": "protected",
                },
                {
                    "node_name": "Outdated Node",
                    "dataset_uuid": "http://neurobagel.org/vocab/67890",
                    "subject_data": "protected",
                },
            ],
        ),
        (
            models.DatasetsQueryResponse,
            [
                [  # from Up-to-date Node
                    {
                        "dataset_uuid": "http://neurobagel.org/vocab/12345",
                        "dataset_name": "OpenNeuro Dataset",
                        "authors": ["First Author", "Second Author"],
                        "homepage": "https://openneuro.org/datasets/ds004392/versions/1.0.0",
                        "references_and_links": [],
                        "keywords": [],
                        "repository_url": "https://github.com/OpenNeuroDatasets-JSONLD/ds004392.git",
                        "access_instructions": None,
                        "access_type": "public",
                        "access_email": None,
                        "access_link": "https://github.com/OpenNeuroDatasets-JSONLD/ds004392.git",
                        "dataset_total_subjects": 50,
                        "num_matching_subjects": 10,
                        "records_protected": False,
                        "image_modals": [
                            "http://purl.org/nidash/nidm#FlowWeighted"
                        ],
                        "available_pipelines": {},
                    },
                ],
                [  # from Outdated Node
                    {
                        "dataset_uuid": "http://neurobagel.org/vocab/12345",
                        "dataset_name": "QPN",
                        "dataset_portal_uri": "https://rpq-qpn.ca/en/researchers-section/databases/",  # deprecated field
                        "dataset_total_subjects": 200,
                        "num_matching_subjects": 5,
                        "records_protected": True,
                        "image_modals": [
                            "http://purl.org/nidash/nidm#T1Weighted",
                            "http://purl.org/nidash/nidm#T2Weighted",
                        ],
                        "available_pipelines": {
                            "https://github.com/nipoppy/pipeline-catalog/tree/main/processing/fmriprep": [
                                "23.1.3"
                            ],
                            "https://github.com/nipoppy/pipeline-catalog/tree/main/processing/freesurfer": [
                                "7.3.2"
                            ],
                        },
                    },
                ],
            ],
            [
                {
                    "node_name": "Up-to-date Node",
                    "dataset_uuid": "http://neurobagel.org/vocab/12345",
                    "dataset_name": "OpenNeuro Dataset",
                    "authors": ["First Author", "Second Author"],
                    "homepage": "https://openneuro.org/datasets/ds004392/versions/1.0.0",
                    "references_and_links": [],
                    "keywords": [],
                    "repository_url": "https://github.com/OpenNeuroDatasets-JSONLD/ds004392.git",
                    "access_instructions": None,
                    "access_type": "public",
                    "access_email": None,
                    "access_link": "https://github.com/OpenNeuroDatasets-JSONLD/ds004392.git",
                    "dataset_total_subjects": 50,
                    "num_matching_subjects": 10,
                    "records_protected": False,
                    "image_modals": [
                        "http://purl.org/nidash/nidm#FlowWeighted"
                    ],
                    "available_pipelines": {},
                },
                {
                    "node_name": "Outdated Node",
                    "dataset_uuid": "http://neurobagel.org/vocab/12345",
                    "dataset_name": "QPN",
                    "authors": [],
                    "homepage": None,
                    "references_and_links": [],
                    "keywords": [],
                    "repository_url": None,
                    "access_instructions": None,
                    "access_type": None,
                    "access_email": None,
                    "access_link": None,
                    "dataset_total_subjects": 200,
                    "num_matching_subjects": 5,
                    "records_protected": True,
                    "image_modals": [
                        "http://purl.org/nidash/nidm#T1Weighted",
                        "http://purl.org/nidash/nidm#T2Weighted",
                    ],
                    "available_pipelines": {
                        "https://github.com/nipoppy/pipeline-catalog/tree/main/processing/fmriprep": [
                            "23.1.3"
                        ],
                        "https://github.com/nipoppy/pipeline-catalog/tree/main/processing/freesurfer": [
                            "7.3.2"
                        ],
                    },
                },
            ],
        ),
    ],
)
def test_unrecognized_fields_in_node_responses_handled_gracefully(
    monkeypatch,
    responses_from_nodes,
    response_cls,
    expected_combined_results_payload,
):
    """
    Test that when the response from one of the federated nodes includes unrecognized (potentially outdated) fields,
    the combined results payload is still constructed correctly, omitting the unrecognized fields per dataset.
    """
    monkeypatch.setattr(
        util,
        "FEDERATION_NODES",
        {
            "https://updatednode.org/": "Up-to-date Node",
            "https://outdatednode.org/": "Outdated Node",
        },
    )

    node_urls = ["https://updatednode.org/", "https://outdatednode.org/"]

    combined_results, node_errors = crud.gather_node_query_responses(
        node_urls=node_urls,
        responses=responses_from_nodes,
        response_cls=response_cls,
    )
    # We need to dump the models to dicts because gather_node_query_responses returns Pydantic model instances
    # (FastAPI handles the conversion to JSON automatically when returning responses)
    # but here we want to compare the actual payload content
    combined_results_payload = [resp.model_dump() for resp in combined_results]

    assert combined_results_payload == expected_combined_results_payload
    assert not node_errors
