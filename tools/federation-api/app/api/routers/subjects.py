"""Router for /subjects path operations."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2

from .. import crud, security
from ..models import CombinedSubjectsQueryResponse, SubjectsQueryModel
from ..security import verify_token

router = APIRouter(prefix="/subjects", tags=["subjects"])

oauth2_scheme = OAuth2(
    flows={
        "implicit": {
            "authorizationUrl": "https://neurobagel.ca.auth0.com/authorize",
        }
    },
    # Don't automatically error out when request is not authenticated, to support optional authentication
    auto_error=False,
)


# We use the Response parameter below to change the status code of the response while still being able to validate the returned data using the response model.
# (see https://fastapi.tiangolo.com/advanced/response-change-status-code/ for more info).
@router.post("", response_model=CombinedSubjectsQueryResponse)
async def post_subjects_query(
    response: Response,
    query: SubjectsQueryModel,
    token: str | None = Depends(oauth2_scheme),
):
    """When a POST request is sent, return list of dicts corresponding to subject-level metadata aggregated by dataset."""
    if security.AUTH_ENABLED:
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authenticated",
            )
        token = verify_token(token)

    response_dict = await crud.post_subjects(
        query=query.dict(exclude_none=True),
        token=token,
    )

    if response_dict["errors"]:
        response.status_code = status.HTTP_207_MULTI_STATUS

    return response_dict
