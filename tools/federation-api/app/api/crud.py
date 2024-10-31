"""CRUD functions called by path operations."""

import asyncio
import logging

from fastapi import HTTPException

from . import utility as util


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


async def get(
    min_age: float,
    max_age: float,
    sex: str,
    diagnosis: str,
    is_control: str,
    min_num_imaging_sessions: int,
    min_num_phenotypic_sessions: int,
    assessment: str,
    image_modal: str,
    pipeline_name: str,
    pipeline_version: str,
    node_urls: list[str],
    token: str | None = None,
) -> dict:
    """
    Makes GET requests to one or more Neurobagel node APIs using send_get_request utility function where the parameters are Neurobagel query parameters.

    Parameters
    ----------
    min_age : float
        Minimum age of subject.
    max_age : float
        Maximum age of subject.
    sex : str
        Sex of subject.
    diagnosis : str
        Subject diagnosis.
    is_control : str
        Whether or not subject is a control.
    min_num_imaging_sessions : int
        Subject minimum number of imaging sessions.
    min_num_phenotypic_sessions : int
        Subject minimum number of phenotypic sessions.
    assessment : str
        Non-imaging assessment completed by subjects.
    image_modal : str
        Imaging modality of subject scans.
    pipeline_name : str
        Name of pipeline run on subject scans.
    pipeline_version : str
        Version of pipeline run on subject scans.
    node_urls : list[str]
        List of Neurobagel nodes to send the query to.
    token : str, optional
        Google ID token for authentication, by default None

    Returns
    -------
    httpx.response
        Response of the POST request.

    """
    cross_node_results = []
    node_errors = []

    node_urls = util.validate_query_node_url_list(node_urls)

    # Node API query parameters
    params = {}
    if min_age:
        params["min_age"] = min_age
    if max_age:
        params["max_age"] = max_age
    if sex:
        params["sex"] = sex
    if diagnosis:
        params["diagnosis"] = diagnosis
    if is_control:
        params["is_control"] = is_control
    if min_num_imaging_sessions:
        params["min_num_imaging_sessions"] = min_num_imaging_sessions
    if min_num_phenotypic_sessions:
        params["min_num_phenotypic_sessions"] = min_num_phenotypic_sessions
    if assessment:
        params["assessment"] = assessment
    if image_modal:
        params["image_modal"] = image_modal
    if pipeline_name:
        params["pipeline_name"] = pipeline_name
    if pipeline_version:
        params["pipeline_version"] = pipeline_version

    tasks = [
        util.send_get_request(node_url + "query", params, token)
        for node_url in node_urls
    ]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

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

    return build_combined_response(
        total_nodes=len(node_urls),
        cross_node_results=cross_node_results,
        node_errors=node_errors,
    )


async def get_instances(attribute_base_path: str):
    """
    Makes a GET request to the root subpath of the specified attribute router of all available Neurobagel n-APIs.

    Parameters
    ----------
    attribute_base_path : str
        Base path corresponding to a specific Neurobagel class for which all the available instances should be retrieved, e.g., "assessments"

    Returns
    -------
    dict
        Dictionary where the key is the Neurobagel class and values correspond to all the unique terms representing available (i.e. used) instances of that class.
    """
    node_errors = []
    unique_terms_dict = {}
    # We want to always provide the URI of the requested attribute in a successful federated response,
    # but cannot rely on it always being available in the node responses (e.g., if all nodes fail),
    # so we define it locally based on the requested attribute base path.
    attribute_uri = util.RESOURCE_URI_MAP[attribute_base_path]

    tasks = [
        util.send_get_request(
            url=node_url + attribute_base_path + "/",
        )
        for node_url in util.FEDERATION_NODES
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
        util.send_get_request(f"{node_url}pipelines/{pipeline_term}/versions")
        for node_url in util.FEDERATION_NODES
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
