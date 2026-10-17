"""Router for /datasets path operations."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2

from .. import crud, security
from ..models import CombinedDatasetsQueryResponse, DatasetsQueryModel
from ..security import verify_token

router = APIRouter(prefix="/datasets", tags=["datasets"])

oauth2_scheme = OAuth2(
    flows={
        "implicit": {
            "authorizationUrl": "https://neurobagel.ca.auth0.com/authorize",
        }
    },
    # Don't automatically error out when request is not authenticated, to support optional authentication
    auto_error=False,
)


@router.post("", response_model=CombinedDatasetsQueryResponse)
async def post_datasets_query(
    response: Response,
    query: DatasetsQueryModel,
    token: str | None = Depends(oauth2_scheme),
):
    """When a POST request is sent, return list of dicts corresponding to metadata for datasets matching the query."""
    if security.AUTH_ENABLED:
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authenticated",
            )
        token = verify_token(token)

    response_dict = await crud.post_datasets(
        query=query.model_dump(exclude_none=True),
        token=token,
    )

    if response_dict["errors"]:
        response.status_code = status.HTTP_207_MULTI_STATUS

    return response_dict
