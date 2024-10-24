"""Data models."""

from enum import Enum
from typing import Optional, Union

from fastapi import Query
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field, validator

CONTROLLED_TERM_REGEX = r"^[a-zA-Z]+[:]\S+$"


class QueryModel(BaseModel):
    """Data model and dependency for API that stores the query parameters to be accepted and validated."""

    min_age: float = None
    max_age: float = None
    sex: str = None
    diagnosis: str = None
    is_control: str = None
    min_num_imaging_sessions: int = None
    min_num_phenotypic_sessions: int = None
    assessment: str = None
    image_modal: str = None
    pipeline_name: str = None
    pipeline_version: str = None
    # TODO: Replace default value with union of local and public nodes once https://github.com/neurobagel/federation-api/issues/28 is merged
    # syntax from https://github.com/tiangolo/fastapi/issues/4445#issuecomment-1117632409
    node_url: list[str] | None = Field(Query(default=[]))

    @validator("is_control")
    def check_allowed_iscontrol_values(cls, v):
        """Raise a validation error if the value of 'is_control' is not 'true' (case-insensitive) or None."""
        if v is not None:
            # Ensure that the allowed value is case-insensitive
            if v.lower() != "true":
                raise HTTPException(
                    status_code=422,
                    detail="'is_control' must be either set to 'true' or omitted from the query",
                )
            # Keep it a str because that's what the n-API expects
            return v
        return None


class CohortQueryResponse(BaseModel):
    """Data model for query results for one matching dataset (i.e., a cohort)."""

    node_name: str
    dataset_uuid: str
    # dataset_file_path: str  # TODO: Revisit this field once we have datasets without imaging info/sessions.
    dataset_name: str
    dataset_portal_uri: Optional[str]
    dataset_total_subjects: int
    records_protected: bool
    num_matching_subjects: int
    subject_data: Union[list[dict], str]
    image_modals: list
    available_pipelines: dict


class NodesResponseStatus(str, Enum):
    """Possible values for the status of the responses from the queried nodes."""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial success"
    FAIL = "fail"


class NodeError(BaseModel):
    """Data model for an error encountered when querying a node."""

    node_name: str
    error: str


class CombinedQueryResponse(BaseModel):
    """Data model for the combined query results of all matching datasets across all queried nodes."""

    errors: list[NodeError]
    responses: list[CohortQueryResponse]
    nodes_response_status: NodesResponseStatus


class CombinedAttributeResponse(BaseModel):
    """Data model for the combined available terms for a given Neurobagel attribute/variable across all available nodes."""

    errors: list[NodeError]
    responses: dict
    nodes_response_status: NodesResponseStatus
