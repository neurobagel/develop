"""Constants for federation."""

import os
import re

import httpx
from fastapi import HTTPException

#  Neurobagel nodes
NEUROBAGEL_NODES = os.environ.get(
    "LOCAL_NB_NODES", "(https://api.neurobagel.org/, OpenNeuro)"
)


def parse_nodes_as_dict(nodes: str) -> list:
    """Returns user-defined Neurobagel nodes as a dict.
    It uses a regular expression to match the url, name pairs.
    Makes sure node URLs end with a slash."""
    pattern = re.compile(r"\((?P<url>https?://[^\s]+), (?P<label>[^\)]+)\)")
    matches = pattern.findall(nodes)
    for i in range(len(matches)):
        url, label = matches[i]
        if not url.endswith("/"):
            matches[i] = (url + "/", label)
    nodes_dict = {url: label for url, label in matches}
    return nodes_dict


def send_get_request(url: str, params: list):
    """
    Makes a GET request to one or more Neurobagel nodes.

    Parameters
    ----------
    url : str
        URL of Neurobagel node API.
    params : list
        Neurobagel query parameters.

    Returns
    -------
    dict
        JSON response from Neurobagel node API.


    Raises
    ------
    HTTPException
        _description_
    """
    response = httpx.get(
        url=url,
        params=params,
        # TODO: Revisit timeout value when query performance is improved
        timeout=30.0,
        # Enable redirect following (off by default) so APIs behind a proxy can be reached
        follow_redirects=True,
    )

    if not response.is_success:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"{response.reason_phrase}: {response.text}",
        )
    return response.json()
