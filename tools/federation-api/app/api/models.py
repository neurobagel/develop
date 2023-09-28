"""Data models."""
from pydantic import BaseModel


class QueryModel(BaseModel):
    """Data model and dependency for API that stores the query parameters to be accepted and validated."""

    min_age: float = None
    max_age: float = None
    sex: str = None
    diagnosis: str = None
    is_control: bool = None
    min_num_sessions: int = None
    assessment: str = None
    image_modal: str = None
