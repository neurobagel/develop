"""CRUD functions called by path operations."""

import asyncio
import logging
from typing import TypeVar

from fastapi import HTTPException
from pydantic import BaseModel

from . import models
from . import utility as util

logger = logging.getLogger(__name__)

QueryResponseT = TypeVar("QueryResponseT", bound=BaseModel)


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
        logger.warning(
            f"Requests to {len(node_errors)}/{total_nodes} nodes failed: {[node_error['node_name'] for node_error in node_errors]}."
        )
        if len(node_errors) == total_nodes:
            # See https://fastapi.tiangolo.com/advanced/additional-responses/ for more info
            content["nodes_response_status"] = "fail"
        else:
            content["nodes_response_status"] = "partial success"
    else:
        logger.info(
            f"Requests to all nodes succeeded ({total_nodes}/{total_nodes})."
        )
        content["nodes_response_status"] = "success"

    return content


def gather_node_query_responses(
    node_urls: list, responses: list, response_cls: type[QueryResponseT]
) -> tuple[list[QueryResponseT], list[dict]]:
    """Gather results and errors from a list of cohort query responses from multiple nodes."""
    cross_node_results = []
    node_errors = []
    for node_url, node_response in zip(node_urls, responses):
        node_name = util.FEDERATION_NODES[node_url]
        if isinstance(node_response, HTTPException):
            node_errors.append(
                {"node_name": node_name, "error": node_response.detail}
            )
            logger.warning(
                f"Request to node {node_name} ({node_url}) did not succeed: {node_response.detail}"
            )
        else:
            for dataset_response in node_response:
                dataset_response["node_name"] = node_name
                dataset_result = response_cls.model_validate(dataset_response)
                cross_node_results.append(dataset_result)
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
    dict
        A combined response containing all nodes' responses and errors.

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
        node_urls=node_urls,
        responses=responses,
        response_cls=models.CohortQueryResponse,
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
) -> dict:
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
    dict
        A combined response containing all nodes' responses and errors.

    """
    # NOTE: The 'nodes' field in a single request can only be ALL dicts
    # Normalize trailing slashes in specified node URLs for downstream requests
    nodes_filter = util.validate_and_format_queried_nodes(query.get("nodes"))
    node_urls = [node["node_url"] for node in nodes_filter]

    node_requests = util.build_node_requests_for_query(
        path="subjects",
        nodes_filter=nodes_filter,
        query=query,
    )

    tasks = []
    for request_url, request_body in node_requests.items():
        tasks.append(
            util.send_request(
                method="POST",
                url=request_url,
                body=request_body,
                token=token,
            )
        )
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    cross_node_results, node_errors = gather_node_query_responses(
        node_urls=node_urls,
        responses=responses,
        response_cls=models.SubjectsQueryResponse,
    )

    return build_combined_response(
        total_nodes=len(nodes_filter),
        cross_node_results=cross_node_results,
        node_errors=node_errors,
    )


async def post_datasets(
    query: dict,
    token: str | None = None,
) -> dict:
    """
    Makes POST requests to the /datasets route of one or more Neurobagel node APIs.

    Parameters
    ----------
    query : dict
        Dictionary of Neurobagel query parameters,
        including a "nodes" list of dictionaries of node URLs.
    token : str, optional
        ID token for authentication, by default None

    Returns
    -------
    dict
        A combined response containing all nodes' responses and errors.

    """
    nodes_filter = util.validate_and_format_queried_nodes(query.get("nodes"))
    node_urls = [node["node_url"] for node in nodes_filter]

    query.pop("nodes", None)

    node_requests = util.build_node_requests_for_query(
        path="datasets",
        nodes_filter=nodes_filter,
        query=query,
    )

    tasks = []
    for request_url, request_body in node_requests.items():
        tasks.append(
            util.send_request(
                method="POST",
                url=request_url,
                body=request_body,
                token=token,
            )
        )

    responses = await asyncio.gather(*tasks, return_exceptions=True)

    cross_node_results, node_errors = gather_node_query_responses(
        node_urls=node_urls,
        responses=responses,
        response_cls=models.DatasetsQueryResponse,
    )

    return build_combined_response(
        total_nodes=len(node_urls),
        cross_node_results=cross_node_results,
        node_errors=node_errors,
    )


async def get_instances(attribute_path: str) -> dict:
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
    # We want to always provide the URI of the requested attribute (e.g., "nb:Assessment")
    # in a successful federated response,
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
        is_response_valid, node_error = util.is_valid_dict_response(
            response=response, find_key=attribute_uri
        )
        if is_response_valid:
            # NOTE: We return only the unique attribute instances from all nodes, with uniqueness determined
            # based on the instance's *term URL*.
            # This means that if the same term appears in multiple nodes with potentially different human-readable labels,
            # only the last instance (+ term metadata) received from the nodes will be included in the response.
            for term_dict in response.get(attribute_uri):
                unique_terms_dict[term_dict["TermURL"]] = term_dict
        else:
            node_errors.append({"node_name": node_name, "error": node_error})
            logger.warning(
                f"Request to node {node_name} ({node_url}) did not succeed: {node_error}"
            )

    cross_node_results = {attribute_uri: list(unique_terms_dict.values())}

    return build_combined_response(
        total_nodes=len(util.FEDERATION_NODES),
        cross_node_results=cross_node_results,
        node_errors=node_errors,
    )


async def get_pipeline_versions(pipeline_term: str) -> dict:
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
    node_errors = []
    all_pipe_versions = []

    # TODO: Consider refactoring out coroutine list definition
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
        response_valid, node_error = util.is_valid_dict_response(
            response=response, find_key=pipeline_term
        )
        if response_valid:
            all_pipe_versions.extend(response.get(pipeline_term))
        else:
            node_errors.append({"node_name": node_name, "error": node_error})
            logger.warning(
                f"Request to node {node_name} ({node_url}) did not succeed: {node_error}"
            )

    cross_node_results = {pipeline_term: sorted(list(set(all_pipe_versions)))}

    return build_combined_response(
        total_nodes=len(util.FEDERATION_NODES),
        cross_node_results=cross_node_results,
        node_errors=node_errors,
    )
