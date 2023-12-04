"""Constants and utility functions for federation."""

import json
import warnings
from pathlib import Path

import httpx
from fastapi import HTTPException

LOCAL_NODE_INDEX_PATH = Path(__file__).parents[2] / "local_nb_nodes.json"
FEDERATION_NODES = {}


def add_trailing_slash(url: str) -> str:
    """Add trailing slash to a URL if it does not already have one."""
    if not url.endswith("/"):
        url += "/"
    return url


def parse_nodes_as_dict(path: Path) -> dict:
    """
    Reads names and URLs of user-defined Neurobagel nodes from a JSON file (if available) and stores them in a dict
    where the keys are the node URLs, and the values are the node names.
    Makes sure node URLs end with a slash.
    """
    # TODO: Add more validation of input JSON, including for JSONDecodeError (invalid JSON)
    if path.exists() and path.stat().st_size > 0:
        with open(path, "r") as f:
            local_nodes = json.load(f)
        if local_nodes:
            if isinstance(local_nodes, list):
                return {
                    add_trailing_slash(node["ApiURL"]): node["NodeName"]
                    for node in local_nodes
                }
            return {
                add_trailing_slash(local_nodes["ApiURL"]): local_nodes[
                    "NodeName"
                ]
            }

    return {}


async def create_federation_node_index():
    """
    Creates an index of nodes for federation, which is a dict where the keys are the node URLs, and the values are the node names.
    Fetches the names and URLs of public Neurobagel nodes from a remote directory file, and combines them with the user-defined local nodes.
    """
    node_directory_url = "https://raw.githubusercontent.com/neurobagel/menu/main/node_directory/neurobagel_public_nodes.json"
    local_nodes = parse_nodes_as_dict(LOCAL_NODE_INDEX_PATH)

    if not local_nodes:
        warnings.warn(
            f"No local Neurobagel nodes defined or found. Federation will be limited to nodes available from the Neurobagel public node directory {node_directory_url}. "
            "(To specify one or more local nodes to federate over, define them in a 'local_nb_nodes.json' file in the current directory and relaunch the API.)\n"
        )

    node_directory_response = httpx.get(
        url=node_directory_url,
    )
    # TODO: Handle network errors gracefully
    if node_directory_response.is_success:
        public_nodes = {
            add_trailing_slash(node["ApiURL"]): node["NodeName"]
            for node in node_directory_response.json()
        }
    else:
        failed_get_warning = "\n".join(
            [
                f"Unable to fetch directory of public Neurobagel nodes from {node_directory_url}.",
                "Details of the response from the source:",
                f"Status code {node_directory_response.status_code}: {node_directory_response.reason_phrase}\n",
            ]
        )
        public_nodes = {}

        if local_nodes:
            warnings.warn(
                failed_get_warning
                + f"Federation will be limited to the nodes defined locally for this API: {local_nodes}."
            )
        else:
            warnings.warn(failed_get_warning)
            raise RuntimeError(
                "No local or public Neurobagel nodes available for federation. "
                "Please define at least one local node in a 'local_nb_nodes.json' file in the current directory and try again."
            )

    # This step will remove any duplicate keys from the local and public node dicts, giving priority to the local nodes.
    FEDERATION_NODES.update(
        {
            **public_nodes,
            **local_nodes,
        }
    )


def check_nodes_are_recognized(node_urls: list):
    """
    Check that all node URLs specified in the query exist in the node index for the API instance.
    If not, raise an informative exception where the unrecognized node URLs are listed in alphabetical order.
    """
    unrecognized_nodes = sorted(
        set(node_urls) - set(FEDERATION_NODES.keys())
    )  # Resulting set is sorted alphabetically to make the error message deterministic
    if unrecognized_nodes:
        raise HTTPException(
            status_code=422,
            detail=f"Unrecognized Neurobagel node URL(s): {unrecognized_nodes}. "
            f"The following nodes are available for federation: {list(FEDERATION_NODES.keys())}",
        )


def validate_query_node_url_list(node_urls: list) -> list:
    """Format and validate node URLs passed as values to the query endpoint, including setting a default list of node URLs when none are provided."""
    # Remove and ignore node URLs that are empty strings
    node_urls = list(filter(None, node_urls))
    if node_urls:
        node_urls = [add_trailing_slash(node_url) for node_url in node_urls]
        # Remove duplicates while preserving order
        node_urls = list(dict.fromkeys(node_urls))
        check_nodes_are_recognized(node_urls)
    else:
        # default to searching over all known nodes
        node_urls = list(FEDERATION_NODES.keys())
    return node_urls


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
