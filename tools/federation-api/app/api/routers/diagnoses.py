from fastapi import APIRouter

from ..models import CombinedAttributeResponse
from . import route_factory

router = APIRouter(prefix="/diagnoses", tags=["diagnoses"])

router.add_api_route(
    path="/",
    endpoint=route_factory.create_get_instances_handler(
        attributes_base_path="diagnoses"
    ),
    response_model=CombinedAttributeResponse,
    methods=["GET"],
)
