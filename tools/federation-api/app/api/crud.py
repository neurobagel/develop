"""CRUD functions called by path operations."""

import asyncio
import logging

from fastapi import HTTPException

from . import utility as util


# TODO: Consider removing in future -
# this utility function is currently used by several CRUD functions,
# but could be removed if we switched to using for loops instead of list comprehensions
# when building request tasks.
def build_node_request_urls(node_urls: list, path: str) -> list:
    """
    Return a list of URLs for the current request for the specified set of Neurobagel nodes.
    """
    node_request_urls = []
    for node_url in node_urls:
        node_request_urls.append(node_url + path)
    return node_request_urls


def build_combined_response(
    total_nodes: int, cross_node_results: list | dict, node_errors: list
) -> dict:
    """Return a combined response containing all the nodes' responses and errors. Logs to console a summary of the federated request."""
    content = {"errors": node_errors, "responses": cross_node_results}

    if node_errors:
        logging.warning(
            f"Requests to {len(node_errors)}/{total_nodes} nodes failed: {[node_error['node_name'] for node_error in node_errors]}."
        )
        if len(node_errors) == total_nodes:
            # See https://fastapi.tiangolo.com/advanced/additional-responses/ for more info
            content["nodes_response_status"] = "fail"
        else:
            content["nodes_response_status"] = "partial success"
    else:
        logging.info(
            f"Requests to all nodes succeeded ({total_nodes}/{total_nodes})."
        )
        content["nodes_response_status"] = "success"

    return content


def gather_node_query_responses(node_urls: list, responses: list):
    """Gather results and errors from a list of cohort query responses from multiple nodes."""
    cross_node_results = []
    node_errors = []
    for node_url, response in zip(node_urls, responses):
        node_name = util.FEDERATION_NODES[node_url]
        if isinstance(response, HTTPException):
            node_errors.append(
                {"node_name": node_name, "error": response.detail}
            )
            logging.warning(
                f"Request to node {node_name} ({node_url}) did not succeed: {response.detail}"
            )
        else:
            for result in response:
                result["node_name"] = node_name
            cross_node_results.extend(response)
    return cross_node_results, node_errors


async def get(
    query: dict,
    token: str | None = None,
) -> dict:
    """
    Makes GET requests to one or more Neurobagel node APIs where the parameters are Neurobagel query parameters.

    Parameters
    ----------
    query : dict
        Dictionary of Neurobagel query parameters, including a node_url list.
    token : str, optional
        ID token for authentication, by default None

    Returns
    -------
    httpx.response
        Response of the GET request.

    """
    cross_node_results = []
    node_errors = []

    node_urls = util.validate_query_node_url_list(query.get("node_url"))

    query.pop("node_url", None)

    tasks = [
        util.send_request(
            method="GET", url=node_request_url, params=query, token=token
        )
        for node_request_url in build_node_request_urls(node_urls, "query")
    ]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    cross_node_results, node_errors = gather_node_query_responses(
        node_urls, responses
    )

    return build_combined_response(
        total_nodes=len(node_urls),
        cross_node_results=cross_node_results,
        node_errors=node_errors,
    )


async def post_subjects(
    # We accept a dict instead of a Pydantic model to make it more flexible to inspect
    # and modify the node list as a list of dictionaries (rather than NodeDatasets model instances)
    query: dict,
    token: str | None = None,
):
    """
    Makes POST requests to the /subjects route of one or more Neurobagel node APIs.

    Parameters
    ----------
    query : dict
        Dictionary of Neurobagel query parameters,
        including a "nodes" list of dictionaries of node URLs and specific dataset UUIDs.
    token : str, optional
        ID token for authentication, by default None

    Returns
    -------
    httpx.response
        Response of the POST request.

    """
    nodes = util.validate_queried_nodes(query.get("nodes"))
    node_urls = [node["node_url"] for node in nodes]

    query.pop("nodes", None)

    tasks = []
    # NOTE: Nodes in a single request can only be ALL dicts
    for node in nodes:
        node_request_url = node["node_url"] + "subjects"
        query["datasets"] = node.get("dataset_uuids")
        tasks.append(
            util.send_request(
                method="POST", url=node_request_url, body=query, token=token
            )
        )

    responses = await asyncio.gather(*tasks, return_exceptions=True)

    cross_node_results, node_errors = gather_node_query_responses(
        node_urls, responses
    )

    return build_combined_response(
        total_nodes=len(nodes),
        cross_node_results=cross_node_results,
        node_errors=node_errors,
    )


async def get_instances(attribute_path: str):
    """
    Makes a GET request to the root subpath of the specified attribute router of all available Neurobagel n-APIs.

    Parameters
    ----------
    attribute_path : str
        Path corresponding to a specific Neurobagel class for which all the available instances should be retrieved, e.g., "assessments"

    Returns
    -------
    dict
        Dictionary where the key is the Neurobagel class and values correspond to all the unique terms representing available (i.e. used) instances of that class.
    """
    node_errors = []
    unique_terms_dict = {}
    # We want to always provide the URI of the requested attribute in a successful federated response,
    # but cannot rely on it always being available in the node responses (e.g., if all nodes fail),
    # so we define it locally based on the requested attribute path.
    attribute_uri = util.RESOURCE_URI_MAP[attribute_path]

    tasks = [
        util.send_request(method="GET", url=node_request_url)
        for node_request_url in build_node_request_urls(
            util.FEDERATION_NODES, attribute_path
        )
    ]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    for (node_url, node_name), response in zip(
        util.FEDERATION_NODES.items(), responses
    ):
        if isinstance(response, HTTPException):
            node_errors.append(
                {"node_name": node_name, "error": response.detail}
            )
            logging.warning(
                f"Request to node {node_name} ({node_url}) did not succeed: {response.detail}"
            )
        else:
            # NOTE: We return only the unique attribute instances from all nodes, based on the instance's *term URL*.
            # This means that if the same instance term appears in multiple nodes with potentially different human-readable labels,
            # only one version (term-label pairing) will be included in the response.
            for term_dict in response[attribute_uri]:
                unique_terms_dict[term_dict["TermURL"]] = term_dict

    cross_node_results = {attribute_uri: list(unique_terms_dict.values())}

    return build_combined_response(
        total_nodes=len(util.FEDERATION_NODES),
        cross_node_results=cross_node_results,
        node_errors=node_errors,
    )


async def get_pipeline_versions(pipeline_term: str):
    """
    Make a GET request to all available node APIs for available versions of a specified pipeline.

    Parameters
    ----------
    pipeline_term : str
        Controlled term of pipeline for which all the available terms should be retrieved.

    Returns
    -------
    dict
        Dictionary where the key is the pipeline term and the value is the list of unique available (i.e. used) versions of the pipeline.
    """
    # TODO: The logic in this function is very similar to get_terms. Consider refactoring to reduce code duplication.
    node_errors = []
    all_pipe_versions = []

    tasks = [
        util.send_request(method="GET", url=node_request_url)
        for node_request_url in build_node_request_urls(
            util.FEDERATION_NODES, f"pipelines/{pipeline_term}/versions"
        )
    ]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    for (node_url, node_name), response in zip(
        util.FEDERATION_NODES.items(), responses
    ):
        if isinstance(response, HTTPException):
            node_errors.append(
                {"node_name": node_name, "error": response.detail}
            )
            logging.warning(
                f"Request to node {node_name} ({node_url}) did not succeed: {response.detail}"
            )
        else:
            all_pipe_versions.extend(response[pipeline_term])

    cross_node_results = {pipeline_term: sorted(list(set(all_pipe_versions)))}

    return build_combined_response(
        total_nodes=len(util.FEDERATION_NODES),
        cross_node_results=cross_node_results,
        node_errors=node_errors,
    )
