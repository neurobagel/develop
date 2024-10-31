"""Constants and utility functions for federation."""

import json
import logging
import os
import warnings
from collections import namedtuple
from pathlib import Path

import httpx
import jsonschema
from fastapi import HTTPException, status
from jsonschema import validate

EnvVar = namedtuple("EnvVar", ["name", "value"])

IS_FEDERATE_REMOTE_PUBLIC_NODES = EnvVar(
    "NB_FEDERATE_REMOTE_PUBLIC_NODES",
    os.environ.get("NB_FEDERATE_REMOTE_PUBLIC_NODES", "True").lower()
    == "true",
)

LOCAL_NODE_INDEX_PATH = Path(__file__).parents[2] / "local_nb_nodes.json"

# Stores the names and URLs of all Neurobagel nodes known to the API instance, in the form of {node_url: node_name, ...}
FEDERATION_NODES = {}

# We use this schema to validate the local_nb_nodes.json file
# We allow both array type input and a single JSON object
# Therefore the schema supports both
LOCAL_NODE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "definitions": {
        "node": {
            "type": "object",
            "properties": {
                "ApiURL": {"type": "string", "pattern": "^(http|https)://"},
                "NodeName": {"type": "string"},
            },
            "required": ["ApiURL", "NodeName"],
            "additionalProperties": False,
        }
    },
    "oneOf": [
        {
            "type": "array",
            "items": {"$ref": "#/definitions/node"},
            "minItems": 1,
        },
        {"$ref": "#/definitions/node"},
    ],
}

# API resource names (base paths) and corresponding controlled terms for
# Neurobagel attributes queryable using the API
RESOURCE_URI_MAP = {
    "assessments": "nb:Assessment",
    "diagnoses": "nb:Diagnosis",
    "pipelines": "nb:Pipeline",
}


def add_trailing_slash(url: str) -> str:
    """Add trailing slash to a URL if it does not already have one."""
    if not url.endswith("/"):
        url += "/"
    return url


def parse_nodes_as_dict(path: Path) -> dict:
    """
    Reads names and URLs of user-defined Neurobagel nodes from a JSON file
    (if available) and stores them in a dict
    where the keys are the node URLs, and the values are the node names.
    Makes sure node URLs end with a slash and only valid nodes are returned.
    """
    valid_nodes = []

    # Check if the path points to an existing file and also is not empty
    # NOTE:
    # Empty directories do not necessarily have a size of 0. This depends on the filesystem.
    # So, we check first if the path is a file.
    if path.is_file() and path.stat().st_size > 0:
        try:
            with open(path, "r") as f:
                local_nodes = json.load(f)
        except json.JSONDecodeError:
            warnings.warn(f"You provided an invalid JSON file at {path}.")
            local_nodes = []

        # We wrap our input in a list if it isn't already to enable
        # easy iteration for adding trailing slashes, even though our
        # file level schema could handle a single non-array input
        input_nodes = (
            local_nodes if isinstance(local_nodes, list) else [local_nodes]
        )

        try:
            # We validate the entire file first, checking all nodes together
            validate(instance=input_nodes, schema=LOCAL_NODE_SCHEMA)
            valid_nodes = input_nodes
        except jsonschema.ValidationError:
            invalid_nodes = []
            for node in input_nodes:
                try:
                    validate(
                        instance=node,
                        schema=LOCAL_NODE_SCHEMA["definitions"]["node"],
                    )
                    valid_nodes.append(node)
                except jsonschema.ValidationError:
                    invalid_nodes.append(node)

            if invalid_nodes:
                warnings.warn(
                    "Some of the nodes in the JSON are invalid:\n"
                    f"{json.dumps(invalid_nodes, indent=2)}"
                )

    if valid_nodes:
        return {
            add_trailing_slash(node["ApiURL"]): node["NodeName"]
            for node in valid_nodes
        }

    return {}


async def create_federation_node_index():
    """
    Creates an index of nodes for federation, which is a dict
    where the keys are the node URLs, and the values are the node names.
    Fetches the names and URLs of public Neurobagel nodes from a remote
    directory file, and combines them with the user-defined local nodes.
    """
    node_directory_url = "https://raw.githubusercontent.com/neurobagel/menu/main/node_directory/neurobagel_public_nodes.json"
    local_nodes = parse_nodes_as_dict(LOCAL_NODE_INDEX_PATH)

    if not local_nodes:
        warnings.warn(
            "No local Neurobagel nodes defined or found. Federation "
            " will be limited to nodes available from the "
            f"Neurobagel public node directory {node_directory_url}. "
            "(To specify one or more local nodes to federate over, "
            "define them in a 'local_nb_nodes.json' file in the "
            "current directory and relaunch the API.)\n"
        )

    node_directory_response = {}
    public_nodes = {}
    failed_get_warning = ""

    if IS_FEDERATE_REMOTE_PUBLIC_NODES.value:
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
                    "IS_FEDERATE_REMOTE_PUBLIC_NODES is set to True, but",
                    f"unable to fetch directory of public Neurobagel nodes from {node_directory_url}.",
                    "Details of the response from the source:",
                    f"Status code {node_directory_response.status_code}: {node_directory_response.reason_phrase}\n",
                ]
            )

            if local_nodes:
                logging.warning(
                    failed_get_warning
                    + f"Federation will be limited to the nodes defined locally for this API: {local_nodes}."
                )
            else:
                logging.warning(failed_get_warning)
                raise RuntimeError(
                    "No local or public Neurobagel nodes available for federation."
                    "Please define at least one local node in "
                    "a 'local_nb_nodes.json' file in the "
                    "current directory and try again."
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
    """
    Format and validate node URLs passed as values to the query endpoint,
    including setting a default list of node URLs when none are provided.
    """
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


async def send_get_request(
    url: str,
    params: list | None = None,
    token: str | None = None,
    timeout: float | None = None,
) -> dict:
    """
    Makes a GET request to one or more Neurobagel nodes.

    Parameters
    ----------
    url : str
        URL of Neurobagel node API.
    params : list, optional
        Neurobagel query parameters, by default None.
    token : str, optional
        Authorization token for the request, by default None.
    timeout : float, optional
        Timeout for the request, by default None.

    Returns
    -------
    dict
        JSON response from Neurobagel node API.


    Raises
    ------
    HTTPException
        _description_
    """
    async with httpx.AsyncClient() as client:
        headers = {
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        }
        try:
            response = await client.get(
                url=url,
                params=params,
                headers=headers,
                timeout=timeout,
                # Enable redirect following (off by default) so
                # APIs behind a proxy can be reached
                follow_redirects=True,
            )
            if not response.is_success:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"{response.reason_phrase}: {response.text}",
                )
            return response.json()
        # Make sure that any HTTPException raised by us is not then caught by the most generic Exception block below
        # (from https://stackoverflow.com/a/16123643)
        except HTTPException:
            raise
        except httpx.NetworkError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Request failed due to a network error or because the node API could not be reached: {exc}",
            ) from exc
        except httpx.TimeoutException as exc:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Request failed due to a timeout: {exc}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Request failed due to an error: {exc}",
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error was encountered: {exc}",
            ) from exc
