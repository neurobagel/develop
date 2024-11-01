"""Router for query path operations."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2

from .. import crud, security
from ..models import CombinedQueryResponse, QueryModel
from ..security import verify_and_extract_token

# from fastapi.security import open_id_connect_url


router = APIRouter(prefix="/query", tags=["query"])

# Adapted from info in https://github.com/tiangolo/fastapi/discussions/9137#discussioncomment-5157382
oauth2_scheme = OAuth2(
    flows={
        "implicit": {
            "authorizationUrl": "https://accounts.google.com/o/oauth2/auth",
        }
    },
    # Don't automatically error out when request is not authenticated, to support optional authentication
    auto_error=False,
)
# NOTE: Can also explicitly use OpenID Connect because Google supports it - results in the same behavior as the OAuth2 scheme above.
# openid_connect_scheme = open_id_connect_url.OpenIdConnect(
#     openIdConnectUrl="https://accounts.google.com/.well-known/openid-configuration"
# )


# We use the Response parameter below to change the status code of the response while still being able to validate the returned data using the response model.
# (see https://fastapi.tiangolo.com/advanced/response-change-status-code/ for more info).
#
# TODO: if our response model for fully successful vs. not fully successful responses grows more complex in the future,
# consider additionally using https://fastapi.tiangolo.com/advanced/additional-responses/#additional-response-with-model to document
# example responses for different status codes in the OpenAPI docs (less relevant for now since there is only one response model).
@router.get("", response_model=CombinedQueryResponse)
async def get_query(
    response: Response,
    query: QueryModel = Depends(QueryModel),
    token: str | None = Depends(oauth2_scheme),
):
    """When a GET request is sent, return list of dicts corresponding to subject-level metadata aggregated by dataset."""
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
        token = verify_and_extract_token(token)

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
        query.pipeline_name,
        query.pipeline_version,
        query.node_url,
        token,
    )

    if response_dict["errors"]:
        response.status_code = status.HTTP_207_MULTI_STATUS

    return response_dict
