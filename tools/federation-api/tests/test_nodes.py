import os

import httpx
import pytest

from app.api import utility as util


@pytest.mark.parametrize(
    "local_nodes",
    [
        "(https://mylocalnode.org, Local Node)",
        "(https://mylocalnode.org/, Local Node) (https://firstpublicnode.org/, First Public Node)",
    ],
)
def test_nodes_discovery_endpoint(test_app, monkeypatch, local_nodes):
    """Test that a federation node index is correctly created from locally set and remote node lists."""
    monkeypatch.setenv("LOCAL_NB_NODES", local_nodes)
    monkeypatch.setattr(
        util,
        "LOCAL_NODES",
        os.environ.get(
            "LOCAL_NB_NODES", "(https://api.neurobagel.org/, OpenNeuro)"
        ),
    )

    def mock_httpx_get(**kwargs):
        return httpx.Response(
            status_code=200,
            json=[
                {
                    "NodeName": "First Public Node",
                    "ApiURL": "https://firstpublicnode.org",
                },
                {
                    "NodeName": "Second Public Node",
                    "ApiURL": "https://secondpublicnode.org",
                },
            ],
        )

    monkeypatch.setattr(httpx, "get", mock_httpx_get)

    with test_app:
        response = test_app.get("/nodes/")
        assert util.FEDERATION_NODES == {
            "https://firstpublicnode.org/": "First Public Node",
            "https://secondpublicnode.org/": "Second Public Node",
            "https://mylocalnode.org/": "Local Node",
        }
        assert response.json() == [
            {
                "NodeName": "First Public Node",
                "ApiURL": "https://firstpublicnode.org/",
            },
            {
                "NodeName": "Second Public Node",
                "ApiURL": "https://secondpublicnode.org/",
            },
            {"NodeName": "Local Node", "ApiURL": "https://mylocalnode.org/"},
        ]


def test_failed_public_nodes_fetching_raises_warning(test_app, monkeypatch):
    """Test that when request for remote list of public nodes fails, an informative warning is raised and the federation node index only includes local nodes."""
    monkeypatch.setenv(
        "LOCAL_NB_NODES", "(https://mylocalnode.org, Local Node)"
    )
    monkeypatch.setattr(
        util,
        "LOCAL_NODES",
        os.environ.get(
            "LOCAL_NB_NODES", "(https://api.neurobagel.org/, OpenNeuro)"
        ),
    )

    def mock_httpx_get(**kwargs):
        return httpx.Response(
            status_code=404, json={}, text="Some error message"
        )

    monkeypatch.setattr(httpx, "get", mock_httpx_get)

    with pytest.warns(UserWarning) as w:
        with test_app:
            response = test_app.get("/nodes/")
            assert util.FEDERATION_NODES == {
                "https://mylocalnode.org/": "Local Node"
            }
            assert response.json() == [
                {
                    "NodeName": "Local Node",
                    "ApiURL": "https://mylocalnode.org/",
                }
            ]

    for warn_substr in [
        "Unable to fetch directory of public Neurobagel nodes",
        "The federation API will only register the nodes defined locally for this API: {'https://mylocalnode.org/': 'Local Node'}",
    ]:
        assert warn_substr in w[0].message.args[0]
