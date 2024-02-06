"""Router for query path operations."""

from fastapi import APIRouter, Depends, Response, status

from .. import crud
from ..models import CombinedQueryResponse, QueryModel

router = APIRouter(prefix="/query", tags=["query"])


# We use the Response parameter below to change the status code of the response while still being able to validate the returned data using the response model.
# (see https://fastapi.tiangolo.com/advanced/response-change-status-code/ for more info).
#
# TODO: if our response model for fully successful vs. not fully successful responses grows more complex in the future,
# consider additionally using https://fastapi.tiangolo.com/advanced/additional-responses/#additional-response-with-model to document
# example responses for different status codes in the OpenAPI docs (less relevant for now since there is only one response model).
@router.get("/", response_model=CombinedQueryResponse)
async def get_query(
    response: Response, query: QueryModel = Depends(QueryModel)
):
    """When a GET request is sent, return list of dicts corresponding to subject-level metadata aggregated by dataset."""
    response_dict = await crud.get(
        query.min_age,
        query.max_age,
        query.sex,
        query.diagnosis,
        query.is_control,
        query.min_num_imaging_sessions,
        query.min_num_phenotypic_sessions,
        query.assessment,
        query.image_modal,
        query.node_url,
    )

    if response_dict["errors"]:
        response.status_code = status.HTTP_207_MULTI_STATUS

    return response_dict
