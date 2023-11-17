import os

import pytest

from app.api import utility as util


@pytest.mark.parametrize(
    "set_nodes, expected_nodes",
    [
        (
            "(https://firstnode.neurobagel.org/query, firstnode)",
            {"https://firstnode.neurobagel.org/query/": "firstnode"},
        ),
        (
            "(https://firstnode.neurobagel.org/query/, firstnode) (https://secondnode.neurobagel.org/query, secondnode)",
            {
                "https://firstnode.neurobagel.org/query/": "firstnode",
                "https://secondnode.neurobagel.org/query/": "secondnode",
            },
        ),
        (
            "(firstnode.neurobagel.org/query/, firstnode) (https://secondnode.neurobagel.org/query, secondnode)",
            {
                "https://secondnode.neurobagel.org/query/": "secondnode",
            },
        ),
        (
            "( , firstnode) (https://secondnode.neurobagel.org/query, secondnode)",
            {
                "https://secondnode.neurobagel.org/query/": "secondnode",
            },
        ),
    ],
)
def test_parse_nodes_as_dict(monkeypatch, set_nodes, expected_nodes):
    """Test that Neurobagel node URLs provided in a string environment variable are correctly parseed into a list."""
    monkeypatch.setenv("NB_NODES", set_nodes)
    assert sorted(
        util.parse_nodes_as_dict(
            os.environ.get("NB_NODES", "https://api.neurobagel.org/query/")
        )
    ) == sorted(expected_nodes)
