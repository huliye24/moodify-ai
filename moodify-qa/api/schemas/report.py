"""Pydantic schemas for Moodify QA API.

Request and response models for API endpoints.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Analysis task status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class IssueSeverity(str, Enum):
    """Issue severity levels."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


# =============================================================================
# Request Schemas
# =============================================================================


class AnalyzeRequest(BaseModel):
    """Request for audio analysis.

    Note: File is uploaded as multipart/form-data, not JSON.
    This schema is for documentation purposes.
    """

    webhook_url: Optional[str] = Field(
        None,
        description="Optional webhook URL to receive completion notification"
    )


class BatchAnalyzeRequest(BaseModel):
    """Request for batch audio analysis."""

    webhook_url: Optional[str] = Field(
        None,
        description="Optional webhook URL for batch completion notification"
    )


# =============================================================================
# Response Schemas
# =============================================================================


class TaskResponse(BaseModel):
    """Response for task creation."""

    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    created_at: datetime = Field(..., description="Task creation timestamp")
    estimated_seconds: int = Field(
        default=30,
        description="Estimated processing time in seconds"
    )
    message: str = Field(default="Task created successfully")


class BatchTaskResponse(BaseModel):
    """Response for batch task creation."""

    batch_id: str = Field(..., description="Unique batch identifier")
    task_ids: list[str] = Field(..., description="List of individual task IDs")
    total: int = Field(..., description="Total number of files")
    status: TaskStatus = Field(..., description="Overall batch status")
    created_at: datetime = Field(..., description="Batch creation timestamp")
    estimated_seconds: int = Field(
        default=60,
        description="Estimated processing time in seconds"
    )


class QAIssue(BaseModel):
    """Detected quality issue."""

    category: str = Field(..., description="Issue category")
    severity: IssueSeverity = Field(..., description="Issue severity")
    message: str = Field(..., description="Human-readable issue description")
    metric: str = Field(..., description="Related metric name")
    value: Optional[float] = Field(None, description="Actual metric value")
    threshold: Optional[float] = Field(None, description="Threshold value")


class QARecommendation(BaseModel):
    """Quality improvement recommendation."""

    issue_category: str = Field(..., description="Related issue category")
    priority: int = Field(..., ge=1, le=3, description="Priority level (1=highest)")
    action: str = Field(..., description="Recommended action")
    details: str = Field(..., description="Detailed guidance")


class ScoreBreakdown(BaseModel):
    """Detailed score breakdown."""

    technical: dict[str, float] = Field(..., description="Technical quality scores")
    musical: dict[str, float] = Field(..., description="Musical quality scores")


class FileInfo(BaseModel):
    """Audio file information."""

    name: str = Field(..., description="Original filename")
    duration_seconds: float = Field(..., description="Audio duration in seconds")
    sample_rate_hz: int = Field(..., description="Sample rate in Hz")
    channels: int = Field(..., description="Number of channels")
    bit_depth: Optional[int] = Field(None, description="Bit depth if available")
    size_bytes: int = Field(..., description="File size in bytes")
    sha256: str = Field(..., description="SHA256 hash of file")


class QAReportResponse(BaseModel):
    """Complete QA report response."""

    task_id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(..., description="Task status")

    # File info
    file: FileInfo = Field(..., description="Audio file information")

    # Scores
    qa_score: float = Field(..., ge=0, le=100, description="Overall QA score (0-100)")
    technical_score: float = Field(..., ge=0, le=100, description="Technical quality score")
    musical_score: float = Field(..., ge=0, le=100, description="Musical quality score")

    # Issues and recommendations
    issues: list[QAIssue] = Field(default_factory=list, description="Detected issues")
    recommendations: list[QARecommendation] = Field(
        default_factory=list,
        description="Improvement recommendations"
    )

    # Detailed breakdown
    breakdown: ScoreBreakdown = Field(..., description="Score breakdown by category")

    # Raw metrics (optional, for advanced users)
    metrics: Optional[dict[str, Any]] = Field(
        None,
        description="Raw measurement metrics"
    )

    # Timestamps
    created_at: datetime = Field(..., description="Task creation time")
    completed_at: Optional[datetime] = Field(None, description="Task completion time")
    processing_time_seconds: Optional[float] = Field(
        None,
        description="Actual processing time"
    )


class BatchReportResponse(BaseModel):
    """Batch analysis report response."""

    batch_id: str = Field(..., description="Batch identifier")
    status: TaskStatus = Field(..., description="Overall batch status")
    total: int = Field(..., description="Total number of files")
    completed: int = Field(..., description="Number of completed analyses")
    failed: int = Field(..., description="Number of failed analyses")
    average_score: Optional[float] = Field(None, description="Average QA score")
    reports: list[QAReportResponse] = Field(
        default_factory=list,
        description="Individual reports"
    )
    created_at: datetime = Field(..., description="Batch creation time")
    completed_at: Optional[datetime] = Field(None, description="Batch completion time")


class WebhookPayload(BaseModel):
    """Webhook notification payload."""

    task_id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(..., description="Task status")
    qa_score: Optional[float] = Field(None, description="QA score if completed")
    message: str = Field(..., description="Status message")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


# =============================================================================
# Health & Status
# =============================================================================


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy")
    version: str = Field(..., description="API version")
    uptime_seconds: Optional[int] = Field(None, description="Service uptime")
    queue_size: int = Field(default=0, description="Current task queue size")


class VersionResponse(BaseModel):
    """API version response."""

    api_version: str = Field(..., description="API version")
    service_version: str = Field(..., description="Service version")
    build_date: Optional[str] = Field(None, description="Build date")


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    task_id: Optional[str] = Field(None, description="Related task ID if applicable")
