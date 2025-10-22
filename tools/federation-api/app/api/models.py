"""Data models."""

from enum import Enum
from typing import Optional, Union

from fastapi import Query
from pydantic import BaseModel, Field

CONTROLLED_TERM_REGEX = r"^[a-zA-Z]+[:]\S+$"


class BaseQueryModel(BaseModel):
    """Data model for standardized variable-based query parameters."""

    min_age: float = Field(default=None, description="Minimum age of subject.")
    max_age: float = Field(default=None, description="Maximum age of subject.")
    sex: str = Field(default=None, description="Sex of subject.")
    diagnosis: str = Field(default=None, description="Subject diagnosis.")
    min_num_imaging_sessions: int = Field(
        default=None, description="Subject minimum number of imaging sessions."
    )
    min_num_phenotypic_sessions: int = Field(
        default=None,
        description="Subject minimum number of phenotypic sessions.",
    )
    assessment: str = Field(
        default=None,
        description="Non-imaging assessment completed by subjects.",
    )
    image_modal: str = Field(
        default=None, description="Imaging modality of subject scans."
    )
    pipeline_name: str = Field(
        default=None, description="Name of pipeline run on subject scans."
    )
    pipeline_version: str = Field(
        default=None, description="Version of pipeline run on subject scans."
    )


class QueryModel(BaseQueryModel):
    # TODO: Revisit after addressing https://github.com/neurobagel/federation-api/issues/165
    # After FastAPI v0.115.0+, we should no longer need this custom syntax to support a list query parameter in a GET request
    # (and ensure the interactive docs work to specify a list)
    # originally adapted from https://github.com/tiangolo/fastapi/issues/4445#issuecomment-1117632409
    node_url: list[str] | None = Field(Query(default=[]))


class NodeDatasets(BaseModel):
    """Data model for specifying datasets to query within a specific node."""

    node_url: str
    dataset_uuids: list[str] | None = None


class SubjectsQueryModel(BaseQueryModel):
    """Data model a for POST /subjects query."""

    nodes: list[NodeDatasets] | None = None


class NodeUrl(BaseModel):
    """Data model for specifying a single node URL."""

    node_url: str


class DatasetsQueryModel(BaseQueryModel):
    """Data model for a POST /datasets query."""

    nodes: list[NodeUrl] | None = None


class DatasetsQueryResponse(BaseModel):
    """Data model for dataset-level results for one dataset matching a given query."""

    node_name: str
    dataset_uuid: str
    # dataset_file_path: str  # TODO: Revisit this field once we have datasets without imaging info/sessions.
    dataset_name: str
    dataset_portal_uri: Optional[str]
    dataset_total_subjects: int
    records_protected: bool
    num_matching_subjects: int
    image_modals: list
    available_pipelines: dict


class SubjectsQueryResponse(DatasetsQueryResponse):
    """Data model for subject-level results for one dataset matching a given query."""

    subject_data: Union[list[dict], str]


class NodesResponseStatus(str, Enum):
    """Possible values for the status of the responses from the queried nodes."""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial success"
    FAIL = "fail"


class NodeError(BaseModel):
    """Data model for an error encountered when querying a node."""

    node_name: str
    error: str


class BaseCombinedQueryResponse(BaseModel):
    """Base data model for combined query results across all queried nodes."""

    errors: list[NodeError]
    nodes_response_status: NodesResponseStatus


class CombinedSubjectsQueryResponse(BaseCombinedQueryResponse):
    """Data model for the combined subjects query results of all matching datasets across all queried nodes."""

    responses: list[SubjectsQueryResponse]


class CombinedDatasetsQueryResponse(BaseCombinedQueryResponse):
    """Data model for the combined dataset query results of all matching datasets across all queried nodes."""

    responses: list[DatasetsQueryResponse]


class CombinedAttributeResponse(BaseModel):
    """Data model for the combined available terms for a given Neurobagel attribute/variable across all available nodes."""

    errors: list[NodeError]
    responses: dict
    nodes_response_status: NodesResponseStatus
