"""Constants for federation."""

import os

import httpx
from fastapi import HTTPException

#  Neurobagel nodes
NEUROBAGEL_NODES = os.environ.get("NB_NODES", "https://api.neurobagel.org/")


def parse_nodes_as_list(nodes: str) -> list:
    """Returns user-defined Neurobagel nodes as a list.
    Empty strings are filtered out, because they are falsy."""
    return list(filter(None, nodes.split(" ")))


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
