from fastapi import APIRouter, Response, status
from pydantic import constr

from .. import crud
from ..models import CONTROLLED_TERM_REGEX, CombinedAttributeResponse

router = APIRouter(prefix="/attributes", tags=["attributes"])


# We use the Response parameter below to change the status code of the response while still being able to validate the returned data using the response model.
# (see https://fastapi.tiangolo.com/advanced/response-change-status-code/ for more info).
#
# TODO: if our response model for fully successful vs. not fully successful responses grows more complex in the future,
# consider additionally using https://fastapi.tiangolo.com/advanced/additional-responses/#additional-response-with-model to document
# example responses for different status codes in the OpenAPI docs (less relevant for now since there is only one response model).
@router.get("/{data_element_URI}", response_model=CombinedAttributeResponse)
async def get_terms(
    data_element_URI: constr(regex=CONTROLLED_TERM_REGEX), response: Response
):
    """When a GET request is sent, return a list dicts with the only key corresponding to controlled term of a neurobagel class and value corresponding to all the available terms."""
    response_dict = await crud.get_terms(data_element_URI)

    if response_dict["errors"]:
        response.status_code = status.HTTP_207_MULTI_STATUS

    return response_dict
