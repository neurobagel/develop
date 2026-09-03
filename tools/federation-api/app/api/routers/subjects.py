"""Router for /subjects path operations."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2

from .. import crud, security
from ..models import CombinedSubjectsQueryResponse, SubjectsQueryModel
from ..security import verify_token

router = APIRouter(prefix="/subjects", tags=["subjects"])

# Adapted from info in https://github.com/tiangolo/fastapi/discussions/9137#discussioncomment-5157382
# I believe for us this is purely for documentatation/a nice looking interactive API docs page,
# and doesn't actually have any bearing on the ID token validation process.
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
#
# TODO: if our response model for fully successful vs. not fully successful responses grows more complex in the future,
# consider additionally using https://fastapi.tiangolo.com/advanced/additional-responses/#additional-response-with-model to document
# example responses for different status codes in the OpenAPI docs (less relevant for now since there is only one response model).
@router.post("", response_model=CombinedSubjectsQueryResponse)
async def post_subjects_query(
    response: Response,
    query: SubjectsQueryModel,
    token: str | None = Depends(oauth2_scheme),
):
    """When a POST request is sent, return list of dicts corresponding to subject-level metadata aggregated by dataset."""
    # NOTE: Currently, when the request is unauthenticated (missing or malformed authorization header -> missing token),
    # the default response is a 403 Forbidden error.
    # This doesn't fully align with HTTP status code conventions:
    # - 401 Unauthorized should be used when the client lacks authentication credentials
    # - 403 Forbidden should be used when the client has been authenticated but lacks the required permissions
    # If we really care about returning a 401 Unauthorized error, we can use auto_error=False
    # when creating the OAuth2 object and raise a custom HTTPException.
    # See also https://github.com/tiangolo/fastapi/discussions/9130
    # if not token:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Not authenticated",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    if security.AUTH_ENABLED:
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authenticated",
            )
        token = verify_token(token)

    # Remove fields set to None (default value) from the dict
    # to avoid type validation errors of specific query parameters on the receiving nodes
    # (e.g., the value an n-API receives for min_age must be a float and cannot be null/None)
    response_dict = await crud.post_subjects(
        query=query.model_dump(exclude_none=True),
        token=token,
    )

    if response_dict["errors"]:
        response.status_code = status.HTTP_207_MULTI_STATUS

    return response_dict
