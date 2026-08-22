"""
Moodify Python SDK

Developer-friendly SDK for Moodify auditory intelligence API.
"""

from .client import MoodifyClient, AsyncMoodifyClient
from .models import (
    AudioAnalysisResult,
    MRSResult,
    ProcessingResult,
    BatchResult,
    AudioFeatures,
    SpectralFeatures,
    TemporalFeatures,
)
from .exceptions import (
    MoodifyError,
    APIError,
    ValidationError,
    AuthenticationError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ConnectionError,
    ProcessingError,
    NotFoundError,
    ConflictError,
)

__version__ = "0.1.0"
__all__ = [
    "MoodifyClient",
    "AsyncMoodifyClient",
    "AudioAnalysisResult",
    "MRSResult",
    "ProcessingResult",
    "BatchResult",
    "AudioFeatures",
    "SpectralFeatures",
    "TemporalFeatures",
    "MoodifyError",
    "APIError",
    "ValidationError",
    "AuthenticationError",
    "RateLimitError",
    "ServerError",
    "TimeoutError",
    "ConnectionError",
    "ProcessingError",
    "NotFoundError",
    "ConflictError",
]
