import os

import pytest

from app.api import utility as util


@pytest.mark.parametrize(
    "set_nodes, expected_nodes",
    [
        (
            "https://firstnode.neurobagel.org/query/",
            ["https://firstnode.neurobagel.org/query/"],
        ),
        (
            "https://firstnode.neurobagel.org/query/ https://secondnode.neurobagel.org/query/",
            [
                "https://firstnode.neurobagel.org/query/",
                "https://secondnode.neurobagel.org/query/",
            ],
        ),
        (
            " https://firstnode.neurobagel.org/query/ https://secondnode.neurobagel.org/query/  ",
            [
                "https://firstnode.neurobagel.org/query/",
                "https://secondnode.neurobagel.org/query/",
            ],
        ),
    ],
)
def test_parse_nodes_as_list(monkeypatch, set_nodes, expected_nodes):
    """Test that Neurobagel node URLs provided in a string environment variable are correctly parseed into a list."""
    monkeypatch.setenv("NB_NODES", set_nodes)
    assert sorted(
        util.parse_nodes_as_list(
            os.environ.get("NB_NODES", "https://api.neurobagel.org/query/")
        )
    ) == sorted(expected_nodes)
