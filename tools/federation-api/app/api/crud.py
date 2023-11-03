"""CRUD functions called by path operations."""

import httpx
from fastapi import HTTPException

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
    Makes GET requests to one or more Neurobagel node APIs using httpx where the parameters are Neurobagel query parameters.

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

    for node_url in util.parse_nodes_as_list(util.NEUROBAGEL_NODES):
        response = httpx.get(
            url=node_url,
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

        cross_node_results += response.json()

    return cross_node_results
