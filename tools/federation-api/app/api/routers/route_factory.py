from fastapi import Response, status

from .. import crud


# We use the Response parameter below to change the status code of the response while still being able to validate the returned data using the response model.
# (see https://fastapi.tiangolo.com/advanced/response-change-status-code/ for more info).
#
# TODO: if our response model for fully successful vs. not fully successful responses grows more complex in the future,
# consider additionally using https://fastapi.tiangolo.com/advanced/additional-responses/#additional-response-with-model
# when defining API routes to document example responses for different status codes in the OpenAPI docs
# (less relevant for now since there is only one response model).
def create_get_instances_handler(attributes_base_path: str):
    """
    Create the handler (path function) for a federated GET request to the base subpath of
    a given attribute router, e.g. /assessments
    """

    async def get_instances(response: Response) -> dict:
        """
        When a GET request is sent, return a dict containing the responses from all known federation nodes
        to a request for all available instances of a given Neurobagel class.

        The returned dict contains:
        - "errors": a list of any error messages encountered from nodes
        - "responses": a dict containing the unique aggregated instances (and corresponding term metadata)
          from all nodes
        """
        response_dict = await crud.get_instances(attributes_base_path)

        if response_dict["errors"]:
            response.status_code = status.HTTP_207_MULTI_STATUS

        return response_dict

    return get_instances
