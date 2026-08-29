"""Audio-facing API contracts for the experimental intelligence facade."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AudioRequest(BaseModel):
    """Metadata associated with a multipart audio upload.

    The binary file itself is received as FastAPI ``UploadFile`` in the route;
    this model records its public filename and caller-provided metadata.
    """

    file: str = Field(description="Original audio filename or caller-provided ID.")
    metadata: dict[str, Any] = Field(default_factory=dict)


class AudioAnalysisResponse(BaseModel):
    """Basic acoustic analysis returned by the API facade."""

    duration: float
    format: str
    features: dict[str, Any]


class MRSResponse(BaseModel):
    """Experimental MRS evaluation response.

    ``score`` is absent until a caller supplies a validated normalized-feature
    contract. Raw acoustic measurements are never silently converted into a
    human listening score.
    """

    score: float | None
    metrics: dict[str, Any]
    status: str
    method: str | None = None
