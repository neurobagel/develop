from fastapi import APIRouter
from pydantic import constr

from .. import crud
from ..models import CONTROLLED_TERM_REGEX

router = APIRouter(prefix="/attributes", tags=["attributes"])


@router.get("/{data_element_URI}")
async def get_terms(data_element_URI: constr(regex=CONTROLLED_TERM_REGEX)):
    """When a GET request is sent, return a list dicts with the only key corresponding to controlled term of a neurobagel class and value corresponding to all the available terms."""
    response = await crud.get_terms(data_element_URI)

    return response
