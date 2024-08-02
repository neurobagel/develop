from fastapi import APIRouter

from .. import utility as util

router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.get("")
async def get_nodes():
    """Returns a dict of all available nodes apis where key is node URL and value is node name."""
    return [
        {"NodeName": v, "ApiURL": k} for k, v in util.FEDERATION_NODES.items()
    ]
