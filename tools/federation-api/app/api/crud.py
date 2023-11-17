"""CRUD functions called by path operations."""

from . import utility as util


async def get(
    min_age: float,
    max_age: float,
    sex: str,
    diagnosis: str,
    is_control: bool,
    min_num_sessions: int,
    assessment: str,
    image_modal: str,
):
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
    min_num_sessions : int
        Subject minimum number of imaging sessions.
    assessment : str
        Non-imaging assessment completed by subjects.
    image_modal : str
        Imaging modality of subject scans.

    Returns
    -------
    httpx.response
        Response of the POST request.

    """
    cross_node_results = []
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
    if min_num_sessions:
        params["min_num_sessions"] = min_num_sessions
    if assessment:
        params["assessment"] = assessment
    if image_modal:
        params["image_modal"] = image_modal

    nodes_dict = util.parse_nodes_as_dict(util.NEUROBAGEL_NODES)
    for node_url, node_name in nodes_dict.items():
        response = util.send_get_request(node_url + "query/", params)

        for result in response:
            result["node_name"] = node_name

        cross_node_results += response

    return cross_node_results


async def get_terms(data_element_URI: str):
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

    for node_url in util.parse_nodes_as_dict(util.NEUROBAGEL_NODES).keys():
        response = util.send_get_request(
            node_url + "attributes/" + data_element_URI, params
        )

        cross_node_results.append(response)

    unique_terms_dict = {}

    for list_of_terms in cross_node_results:
        for term in list_of_terms[data_element_URI]:
            unique_terms_dict[term["TermURL"]] = term

    return {data_element_URI: list(unique_terms_dict.values())}
