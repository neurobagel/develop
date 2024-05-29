import httpx
import pytest

from app.api import utility as util


@pytest.mark.parametrize(
    "local_nodes",
    [
        {"https://mylocalnode.org/": "Local Node"},
        {
            "https://mylocalnode.org/": "Local Node",
            "https://firstpublicnode.org/": "First Public Node",
        },
    ],
)
def test_nodes_discovery_endpoint(test_app, monkeypatch, local_nodes):
    """Test that a federation node index is correctly created from locally set and remote node lists."""

    def mock_parse_nodes_as_dict(path):
        return local_nodes

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

    monkeypatch.setattr(util, "parse_nodes_as_dict", mock_parse_nodes_as_dict)
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


def test_failed_public_nodes_fetching_raises_warning(
    test_app, monkeypatch, caplog
):
    """Test that when request for remote list of public nodes fails, an informative warning is raised and the federation node index only includes local nodes."""

    def mock_parse_nodes_as_dict(path):
        return {"https://mylocalnode.org/": "Local Node"}

    def mock_httpx_get(**kwargs):
        return httpx.Response(
            status_code=404, json={}, text="Some error message"
        )

    monkeypatch.setattr(util, "parse_nodes_as_dict", mock_parse_nodes_as_dict)
    monkeypatch.setattr(httpx, "get", mock_httpx_get)

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

    assert len(caplog.records) == 1
    for warn_substr in [
        "IS_FEDERATE_REMOTE_PUBLIC_NODES is set to True, but\n"
        "unable to fetch directory of public Neurobagel nodes",
        "Federation will be limited to the nodes defined locally for this API: {'https://mylocalnode.org/': 'Local Node'}",
    ]:
        assert warn_substr in caplog.text


def test_unset_local_nodes_raises_warning(test_app, monkeypatch):
    """Test that when no local nodes are set, an informative warning is raised and the federation node index only includes remote nodes."""

    def mock_parse_nodes_as_dict(path):
        return {}

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

    monkeypatch.setattr(util, "parse_nodes_as_dict", mock_parse_nodes_as_dict)
    monkeypatch.setattr(httpx, "get", mock_httpx_get)

    with pytest.warns(UserWarning) as w:
        with test_app:
            response = test_app.get("/nodes/")
            assert util.FEDERATION_NODES == {
                "https://firstpublicnode.org/": "First Public Node",
                "https://secondpublicnode.org/": "Second Public Node",
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
            ]

    assert len(w) == 1
    assert "No local Neurobagel nodes defined or found" in w[0].message.args[0]


def test_no_available_nodes_raises_error(monkeypatch, test_app, caplog):
    """Test that when no local or remote nodes are available, an informative error is raised."""

    def mock_parse_nodes_as_dict(path):
        return {}

    def mock_httpx_get(**kwargs):
        return httpx.Response(
            status_code=404, json={}, text="Some error message"
        )

    monkeypatch.setattr(util, "parse_nodes_as_dict", mock_parse_nodes_as_dict)
    monkeypatch.setattr(httpx, "get", mock_httpx_get)

    with pytest.warns(UserWarning) as w, pytest.raises(
        RuntimeError
    ) as exc_info:
        with test_app:
            pass

    # Two warnings are expected:
    # one via logging.warning for the failed GET request for public nodes, and
    # one via warnings.warn for the lack of local nodes (because User error).
    assert len(w) == 1
    assert len(caplog.records) == 1
    any(record.levelname == "WARNING" for record in caplog.records)
    assert (
        "No local or public Neurobagel nodes available for federation"
        in str(exc_info.value)
    )
