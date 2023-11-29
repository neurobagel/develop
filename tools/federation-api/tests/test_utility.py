import os
from contextlib import nullcontext as does_not_raise

import pytest
from fastapi import HTTPException

from app.api import utility as util


@pytest.mark.parametrize(
    "url, expected_url",
    [
        ("https://publicnode.org", "https://publicnode.org/"),
        ("https://publicnode.org/", "https://publicnode.org/"),
    ],
)
def test_add_trailing_slash(url, expected_url):
    """Test that a trailing slash is added to a URL if it does not already have one."""
    assert util.add_trailing_slash(url) == expected_url


@pytest.mark.parametrize(
    "set_nodes, expected_nodes",
    [
        (
            "(http://firstnode.neurobagel.org/query, firstnode)",
            {"http://firstnode.neurobagel.org/query/": "firstnode"},
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
        (
            "(https://firstnode.neurobagel.org/query/, firstnode)(https://secondnode.neurobagel.org/query, secondnode)",
            {
                "https://firstnode.neurobagel.org/query/": "firstnode",
                "https://secondnode.neurobagel.org/query/": "secondnode",
            },
        ),
        (
            "(https://firstnode.neurobagel.org/query/,firstnode)(https://secondnode.neurobagel.org/query,secondnode)",
            {
                "https://firstnode.neurobagel.org/query/": "firstnode",
                "https://secondnode.neurobagel.org/query/": "secondnode",
            },
        ),
    ],
)
def test_parse_nodes_as_dict(monkeypatch, set_nodes, expected_nodes):
    """Test that Neurobagel node URLs provided in a string environment variable are correctly parsed into a list."""
    monkeypatch.setenv("LOCAL_NB_NODES", set_nodes)
    # TODO: This currently only compares the keys of the dicts, not the values, due to calling sorted(). This is probably not what we want.
    assert sorted(
        util.parse_nodes_as_dict(
            os.environ.get(
                "LOCAL_NB_NODES", "https://api.neurobagel.org/query/"
            )
        )
    ) == sorted(expected_nodes)


def test_recognized_query_nodes_do_not_raise_error(monkeypatch):
    """Test that node URLs found in the federation node index do not raise an error."""
    monkeypatch.setattr(
        util,
        "FEDERATION_NODES",
        {
            "https://firstknownnode.org/": "My First Node",
            "https://secondknownnode.org/": "My Second Node",
        },
    )

    util.check_nodes_are_recognized(["https://firstknownnode.org/"])


@pytest.mark.parametrize(
    "node_url_list, unrecognized_urls",
    [
        (
            ["https://firstknownnode.org/", "https://mysterynode.org/"],
            "['https://mysterynode.org/']",
        ),
        (
            ["https://mysterynode.org/", "https://unknownnode.org/"],
            "['https://mysterynode.org/', 'https://unknownnode.org/']",
        ),
    ],
)
def test_unrecognized_query_nodes_raise_error(
    monkeypatch, node_url_list, unrecognized_urls
):
    """Test that we raise a helpful error when the user is trying to query an unknown node."""
    monkeypatch.setattr(
        util,
        "FEDERATION_NODES",
        {
            "https://firstknownnode.org/": "My First Node",
            "https://secondknownnode.org/": "My Second Node",
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        util.check_nodes_are_recognized(node_url_list)
    assert (
        f"Unrecognized Neurobagel node URL(s): {unrecognized_urls}"
        in exc_info.value.detail
    )  

    
@pytest.mark.parametrize(
    "raw_url_list, expected_url_list",
    [
        (["https://firstknownnode.org"], ["https://firstknownnode.org/"]),
        (
            ["https://firstknownnode.org", "https://secondknownnode.org/"],
            ["https://firstknownnode.org/", "https://secondknownnode.org/"],
        ),
        (
            ["", "https://secondknownnode.org"],
            ["https://secondknownnode.org/"],
        ),
        (
            [
                "https://secondknownnode.org/",
                "https://firstknownnode.org",
                "https://secondknownnode.org/",
            ],
            ["https://secondknownnode.org/", "https://firstknownnode.org/"],
        ),
        ([], ["https://firstknownnode.org/", "https://secondknownnode.org/"]),
    ],
)
def test_validate_query_node_url_list(
    monkeypatch, raw_url_list, expected_url_list
):
    """Test that provided URLs are deduplicated, get a trailing slash, and default to FEDERATION_NODES if none are provided."""
    monkeypatch.setattr(
        util,
        "FEDERATION_NODES",
        {
            "https://firstknownnode.org/": "My First Node",
            "https://secondknownnode.org/": "My Second Node",
        },
    )

    assert util.validate_query_node_url_list(raw_url_list) == expected_url_list
