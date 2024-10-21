from fastapi import APIRouter, Response, status
from pydantic import constr

from .. import crud
from ..models import CONTROLLED_TERM_REGEX, CombinedAttributeResponse
from . import route_factory

router = APIRouter(prefix="/pipelines", tags=["pipelines"])

router.add_api_route(
    path="/",
    endpoint=route_factory.create_get_instances_handler(
        attributes_base_path="pipelines"
    ),
    response_model=CombinedAttributeResponse,
    methods=["GET"],
)


@router.get(
    "/{pipeline_term}/versions", response_model=CombinedAttributeResponse
)
async def get_pipeline_versions(
    pipeline_term: constr(regex=CONTROLLED_TERM_REGEX), response: Response
):
    """
    When a GET request is sent, return a dict where the key is the pipeline term and the value
    is a list containing all available versions of a pipeline, across all nodes known to the f-API.
    """
    response_dict = await crud.get_pipeline_versions(pipeline_term)

    if response_dict["errors"]:
        response.status_code = status.HTTP_207_MULTI_STATUS

    return response_dict
