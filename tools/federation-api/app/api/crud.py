"""CRUD functions called by path operations."""

import asyncio
import warnings

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from . import utility as util


async def get(
    min_age: float,
    max_age: float,
    sex: str,
    diagnosis: str,
    is_control: bool,
    min_num_imaging_sessions: int,
    min_num_phenotypic_sessions: int,
    assessment: str,
    image_modal: str,
    node_urls: list[str],
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
    is_control : bool
        Whether or not subject is a control.
    min_num_imaging_sessions : int
        Subject minimum number of imaging sessions.
    min_num_phenotypic_sessions : int
        Subject minimum number of phenotypic sessions.
    assessment : str
        Non-imaging assessment completed by subjects.
    image_modal : str
        Imaging modality of subject scans.
    node_urls : list[str]
        List of Neurobagel nodes to send the query to.

    Returns
    -------
    httpx.response
        Response of the POST request.

    """
    cross_node_results = []
    node_errors = []

    node_urls = util.validate_query_node_url_list(node_urls)
    total_nodes = len(node_urls)

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

    tasks = [
        util.send_get_request(node_url + "query/", params)
        for node_url in node_urls
    ]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    for node_url, response in zip(node_urls, responses):
        node_name = util.FEDERATION_NODES[node_url]
        if isinstance(response, HTTPException):
            node_errors.append(
                {"node_name": node_name, "error": response.detail}
            )
            warnings.warn(
                f"Query to node {node_name} ({node_url}) did not succeed: {response.detail}"
            )
        else:
            for result in response:
                result["node_name"] = node_name
            cross_node_results.extend(response)

    if node_errors:
        # TODO: Use logger instead of print, see https://github.com/tiangolo/fastapi/issues/5003
        print(
            f"Queries to {len(node_errors)}/{total_nodes} nodes failed: {[node_error['node_name'] for node_error in node_errors]}."
        )

        if len(node_errors) == total_nodes:
            # See https://fastapi.tiangolo.com/advanced/additional-responses/ for more info
            return JSONResponse(
                status_code=status.HTTP_207_MULTI_STATUS,
                content={
                    "errors": node_errors,
                    "responses": cross_node_results,
                    "nodes_response_status": "fail",
                },
            )
        return JSONResponse(
            status_code=status.HTTP_207_MULTI_STATUS,
            content={
                "errors": node_errors,
                "responses": cross_node_results,
                "nodes_response_status": "partial success",
            },
        )

    print(f"All nodes queried successfully ({total_nodes}/{total_nodes}).")
    return {
        "errors": node_errors,
        "responses": cross_node_results,
        "nodes_response_status": "success",
    }


async def get_terms(data_element_URI: str):
    # TODO: Make this path able to handle partial successes as well
    """
    Makes a GET request to one or more Neurobagel node APIs using send_get_request utility function where the only parameter is a data element URI.

    Parameters
    ----------
    data_element_URI : str
        Controlled term of neurobagel class for which all the available terms should be retrieved.

    Returns
    -------
    dict
        Dictionary where the key is the Neurobagel class and values correspond to all the unique terms representing available (i.e. used) instances of that class.
    """
    cross_node_results = []
    params = {data_element_URI: data_element_URI}

    for node_url in util.FEDERATION_NODES:
        response = util.send_get_request(
            node_url + "attributes/" + data_element_URI, params
        )

        cross_node_results.append(response)

    unique_terms_dict = {}

    for list_of_terms in cross_node_results:
        for term in list_of_terms[data_element_URI]:
            unique_terms_dict[term["TermURL"]] = term

    return {data_element_URI: list(unique_terms_dict.values())}
