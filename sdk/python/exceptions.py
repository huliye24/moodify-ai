"""
Moodify SDK Exceptions

Custom exceptions for error handling.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class MoodifyError(Exception):
    """
    Base exception for Moodify SDK.

    Attributes:
        message: Error message
        code: Error code
        details: Additional error details
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error": self.message,
            "code": self.code,
            "details": self.details
        }


class APIError(MoodifyError):
    """
    API request error.

    Attributes:
        status_code: HTTP status code
        response_body: Raw response body
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        response_body: Optional[str] = None,
        code: Optional[str] = None
    ):
        super().__init__(message, code=code)
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:
        return f"API Error {self.status_code}: {self.message}"


class ValidationError(MoodifyError):
    """
    Input validation error.

    Raised when input parameters or files are invalid.
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        code: Optional[str] = None
    ):
        super().__init__(message, code=code or "VALIDATION_ERROR")
        self.field = field

    def __str__(self) -> str:
        if self.field:
            return f"Validation error in '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class AuthenticationError(MoodifyError):
    """
    Authentication error.

    Raised when API key is invalid or expired.
    """

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="AUTH_ERROR")


class RateLimitError(APIError):
    """
    Rate limit exceeded error.

    Attributes:
        retry_after: Seconds to wait before retry
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ):
        super().__init__(message, status_code=429, code="RATE_LIMIT")
        self.retry_after = retry_after

    def __str__(self) -> str:
        if self.retry_after:
            return f"Rate limit exceeded. Retry after {self.retry_after} seconds."
        return self.message


class ProcessingError(MoodifyError):
    """
    Audio processing error.

    Raised when audio processing fails.
    """

    def __init__(
        self,
        message: str,
        job_id: Optional[str] = None,
        code: Optional[str] = None
    ):
        super().__init__(message, code=code or "PROCESSING_ERROR")
        self.job_id = job_id


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, code="NOT_FOUND")


class ServerError(APIError):
    """Internal server error."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500, code="SERVER_ERROR")


class TimeoutError(APIError):
    """Request timeout error."""

    def __init__(self, message: str = "Request timeout"):
        super().__init__(message, status_code=408, code="TIMEOUT")


class NetworkError(MoodifyError):
    """Network connection error."""

    def __init__(self, message: str = "Network error"):
        super().__init__(message, code="NETWORK_ERROR")


class FileError(MoodifyError):
    """File operation error."""

    def __init__(
        self,
        message: str,
        path: Optional[str] = None,
        code: Optional[str] = None
    ):
        super().__init__(message, code=code or "FILE_ERROR")
        self.path = path

    def __str__(self) -> str:
        if self.path:
            return f"File error for '{self.path}': {self.message}"
        return f"File error: {self.message}"


class ConfigurationError(MoodifyError):
    """SDK configuration error."""

    def __init__(self, message: str):
        super().__init__(message, code="CONFIG_ERROR")


# Error code mapping for HTTP status codes
HTTP_ERROR_MAP = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthenticationError,
    404: NotFoundError,
    408: TimeoutError,
    429: RateLimitError,
    500: ServerError,
    502: ServerError,
    503: ServerError,
    504: TimeoutError,
}


def raise_for_status(status_code: int, message: str, response_body: Optional[str] = None) -> None:
    """
    Raise appropriate exception based on HTTP status code.

    Args:
        status_code: HTTP status code
        message: Error message
        response_body: Raw response body

    Raises:
        APIError or subclass
    """
    error_class = HTTP_ERROR_MAP.get(status_code, APIError)
    raise error_class(message, status_code=status_code, response_body=response_body)
